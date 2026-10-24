"""仅CPU生成447两路径及原owner薄适配；不运行服务或旧套件。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import textwrap

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / 'tmp/compute-order-main-profile'
INIT = 'vllm_fl/__init__.py'
HELPER = 'vllm_fl/patches/biv150_resume_cpu_observer.py'
FOOTER = b'''
    # _biv150_resume_cpu_observer_v1
    import os as _resume_cpu_os
    if _resume_cpu_os.environ.get("BIV150_RESUME_CPU_OBSERVE") == "1":
        _resume_cpu_handle = None
        try:
            import atexit as _resume_cpu_atexit
            from vllm_fl.patches.biv150_resume_cpu_observer import install as _resume_cpu_install
            _resume_cpu_handle = _resume_cpu_install(enabled=True)
            _resume_cpu_atexit.register(_resume_cpu_handle["restore"])
            print("BIV150_RESUME_CPU_OBSERVER_CORE_HOOKED", flush=True)
        except Exception:
            if _resume_cpu_handle is not None:
                _resume_cpu_handle["restore"]()
'''


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def oid(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def save(name, doc):
    (HERE / name).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    helper = (HERE / 'biv150_resume_cpu_observer.py').read_bytes()
    init = subprocess.check_output(['git', '-C', str(ROOT / 'collaboration/FlagOS-S2-vllm-plugin-FL'),
        'show', '3283672b92fa30f93f652b242193999836a95f88:' + INIT])
    assert sha(init) == 'e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff'
    payload = {INIT: init + FOOTER, HELPER: helper}
    assert payload[INIT][:-len(FOOTER)] == init
    base_blobs = json.loads((BASE / 'candidate-git-blobs.json').read_bytes())
    assert len(base_blobs) == 446 and HELPER not in base_blobs
    expected = dict(base_blobs)
    delta = {}
    for path, data in payload.items():
        target = HERE / 'files' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        compile(data, path, 'exec')
        expected[path] = dict(mode='100644', sha=oid(data))
        delta[path] = dict(before=base_blobs.get(path), after=expected[path], sha256=sha(data))
    # 只读已审tree整数算法，不重新导出或核原tar。
    ns = runpy.run_path(str(BASE / 'launch_compute_order_main.py'))
    target_tree = ns['tree_oid'](expected)
    save('observer-manifest.json', dict(base_tree='5c77e68caff6aa0c8b6c230adb78a2d4c293cca1',
        target_tree=target_tree, base_count=446, source_count=447, changed_paths=delta))
    save('observer-git-blobs.json', expected)
    for name in ('candidate-git-blobs.json', 'candidate-manifest.json'):
        (HERE / name).write_bytes((BASE / name).read_bytes())
    schedule_path = ROOT / 'experiments/source-audits/20261021T184108Z-kv-copy/source/vllm/v1/core/sched/scheduler.py'
    raw = schedule_path.read_text(encoding='utf-8')
    cls = next(n for n in ast.parse(raw).body if isinstance(n, ast.ClassDef) and n.name == 'Scheduler')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'schedule')
    source = textwrap.dedent(''.join(raw.splitlines(True)[fn.lineno-1:fn.end_lineno]))
    observer = runpy.run_path(str(HERE / 'biv150_resume_cpu_observer.py'))
    transformed = observer['transform_schedule'](source)
    compile(transformed, '<resume-cpu-observed-schedule>', 'exec')
    reversed_schedule = transformed
    for call in observer['CALLS']:
        reversed_schedule = reversed_schedule.replace(call, '', 1)
    assert reversed_schedule == source
    (HERE / 'schedule.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True), transformed.splitlines(True),
        fromfile='df780-87a-schedule', tofile='CPU-observed-schedule')), encoding='utf-8')
    old = (ROOT / 'tmp/current-main-combined-accuracy/launch_combined_accuracy.py').read_text(encoding='utf-8')
    assert sha(old.encode()) == 'c5ec1da7e43d54f2bca1bf4da91d4b7a57119168ceb239e422b11ccde5ec036d'
    changed, edits = old, []
    def replace(a, b):
        nonlocal changed
        assert changed.count(a) == 1, a
        edits.append(dict(before=a, after=b))
        changed = changed.replace(a, b, 1)
    replace('复用141159受测446源码，交原35d owner运行原105题；不重建源码或评测。',
            '当前446加两路径纯CPU抢占/恢复观察，交原bc51单次longscreen；无profiler。')
    start, end = changed.index('SCRIPTS = {'), changed.index('\n}\n', changed.index('SCRIPTS = {')) + 3
    replace(changed[start:end], "SCRIPTS = " + repr(ns['SCRIPTS']) + '\n')
    manifest = (HERE / 'observer-manifest.json').read_bytes()
    injected = '''OBSERVER_MANIFEST_SHA = %r
OBSERVER_TREE = %r
OBSERVER_PINS = %r


def prepare_source(stamp, blobs, hashes):
    raw = (HERE / 'observer-manifest.json').read_bytes()
    manifest = json.loads(raw)
    if (hashlib.sha256(raw).hexdigest() != OBSERVER_MANIFEST_SHA
            or manifest['base_tree'] != TREE or manifest['source_count'] != 447):
        raise ValueError('observer两路径身份变化')
    source = ROOT / 'code' / ('current-main-resume-cpu-' + stamp)
    if source.exists():
        raise FileExistsError(source)
    expected = dict(blobs)
    payload = {}
    for name, pin in OBSERVER_PINS.items():
        data = (HERE / 'files' / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != pin:
            raise ValueError('observer payload变化：' + name)
        payload[name] = data
        expected[name] = dict(mode='100644', sha=hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\\0' + data).hexdigest())
    delta = {name: dict(before=blobs.get(name), after=expected[name], sha256=hashlib.sha256(data).hexdigest())
             for name, data in payload.items()}
    if manifest['changed_paths'] != delta or manifest['target_tree'] != OBSERVER_TREE:
        raise ValueError('不是current446仅init/observer变化')
    shutil.copytree(SOURCE, source, symlinks=True, ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
    for name, data in payload.items():
        target = source / name
        if target.is_symlink():
            raise ValueError('不覆写payload symlink')
        target.write_bytes(data)
        target.chmod(0o644)
    actual_blobs, actual_hashes = source_maps(source)
    if (len(actual_blobs) != 447 or actual_blobs != expected
            or {k:v for k,v in actual_hashes.items() if k not in payload}
                != {k:v for k,v in hashes.items() if k not in payload}
            or source_maps(SOURCE) != (blobs, hashes)):
        raise ValueError('原446或新447出现未声明变更')
    return source, actual_blobs, actual_hashes


''' % (sha(manifest), target_tree, {k: sha(v) for k, v in payload.items()})
    replace('def main():', injected + 'def main():')
    replace('    blobs, hashes, selected = reference_ready()\n',
            "    blobs, hashes, selected = reference_ready()\n    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')\n    source, blobs, hashes = prepare_source(stamp, blobs, hashes)\n")
    replace("    for name in ('VLLM_FL_BIV150_PREFILL_NORMALIZE',", "    env['BIV150_RESUME_CPU_OBSERVE'] = '1'\n    for name in ('VLLM_FL_BIV150_PREFILL_NORMALIZE',")
    replace("ROOT / 'accuracy' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-current-main-compute-order')",
            "ROOT / 'framework' / (stamp + '-current-main-resume-cpu-context16k-long')")
    replace("shutil.copytree(SOURCE, control / 'plugin-source'", "shutil.copytree(source, control / 'plugin-source'")
    replace("if source_maps(SOURCE) != (blobs, hashes) or source_maps(control / 'plugin-source')", "if source_maps(source) != (blobs, hashes) or source_maps(control / 'plugin-source')")
    replace("('candidate-git-blobs.json', 'candidate-manifest.json')", "('candidate-git-blobs.json', 'candidate-manifest.json', 'observer-manifest.json')")
    replace("control / 'launch_combined_accuracy.py'", "control / 'launch_resume_cpu.py'")
    replace("kind='当前main加P的独立完整105题准确率，尚未通过'", "kind='当前446原路单RID抢占/恢复CPU因果诊断，无profiler/收益结论'")
    replace("source=str(SOURCE), source_count=446, base_commit=COMMIT, tree=TREE,",
            "source=str(source), source_count=447, base_commit=COMMIT, base_tree=TREE, tree=OBSERVER_TREE,")
    replace("limits=['复用受测446源码，不重建tar、不叠PR15/旧Qservice/KV事务或诊断资产',\n            '原35d/6e045/105题/SERVER/DB/设备锁及清理不变，非性能测试',\n            '准确率本轮P可能0命中，须如实限定覆盖；不继承队友main102/105或旧423成绩']",
            "limits=['原446仅init+observer，runner/P/normalized字节不变，无KV策略/传输',\n            '原bc51 context-long-screen/32x16K+1024/seed721201/SERVER/锁/到达/采样不变',\n            '仅实际CPU提交/原execute返回，GPU完成/重算耗时未知；最多16target片段，未覆盖不补跑']")
    replace("command = ['python3', str(ROOT / 'scripts/run_accuracy_gate.py'), str(run), '--source-dir', str(SOURCE),\n        '--require-log-marker', 'BIV150_PREFILL_NORMALIZATION_INSTALL', '--database',\n        '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db']",
            "command = ['python3', str(ROOT / 'scripts/run_framework_screen.py'), str(run), '--source-dir', str(source),\n        '--context-long-screen', '--seed', '721201', '--require-log-marker', 'BIV150_RESUME_CPU_OBSERVER_CORE_HOOKED']")
    # 沿88b当前main短测的6CPU/实时idle/DB-before原字节；不新建GPUowner或控制器。
    baseline = (BASE / 'launch_compute_order_main.py').read_text(encoding='utf-8')
    preflight = baseline[baseline.index('    quota_root='):baseline.index("    (control / 'command.txt')")]
    replace("    (control / 'command.txt').write_text", preflight + "    (control / 'command.txt').write_text")
    replace("source=str(SOURCE), runner_pid=process.pid", "source=str(source), runner_pid=process.pid")
    compile(changed, 'launch_resume_cpu.py', 'exec')
    reverse = changed
    for edit in reversed(edits):
        assert reverse.count(edit['after']) == 1
        reverse = reverse.replace(edit['after'], edit['before'], 1)
    assert reverse == old
    (HERE / 'launch_resume_cpu.py').write_text(changed, encoding='utf-8', newline='\n')
    (HERE / 'launcher.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True), changed.splitlines(True),
        fromfile='c5ec-original-owner', tofile='CPU-resume-longscreen-owner')), encoding='utf-8')
    save('preparation.json', dict(helper_sha256=sha(helper), launcher_sha256=sha(changed.encode()),
        source_count=447, target_tree=target_tree, changed_paths=delta, syntax_compiled=True,
        init_reverse_exact=True, schedule_three_callbacks_reverse_exact=True,
        launcher_reverse_to_c5ec_exact=True, launcher_edits=len(edits),
        reused_preflight_from='88b35410', runner_P_normalized_unchanged=True,
        device_call_expressions=[ast.unparse(n.func) for n in ast.walk(ast.parse(helper))
            if isinstance(n, ast.Call) and any(x in ast.unparse(n.func)
                for x in ('torch.', 'cuda.', 'Profiler', 'synchronize'))],
        observer_imported_stdlib_only=True, model_imported=False, GPU_used=False, owner_executed=False))
    print(json.dumps(dict(helper=sha(helper), launcher=sha(changed.encode()), source_count=447, tree=target_tree)))


if __name__ == '__main__':
    main()
