"""仅CPU整理已冻结的两文件候选及原baseline启动器增量；不导入模型或设备。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / 'tmp/current-main-baseline'
COMMIT = '3283672b92fa30f93f652b242193999836a95f88'
RUNNER = 'vllm_fl/worker/model_runner.py'
HELPER = 'vllm_fl/patches/biv150_compute_order.py'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def oid(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def tree_oid(entries):
    root = {}
    for path, entry in entries.items():
        parts, node = path.split('/'), root
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = (entry['mode'], entry['sha'])
    def walk(node):
        raw = b''
        for name in sorted(node, key=lambda x: (x + '/' if isinstance(node[x], dict) else x).encode()):
            value = node[name]
            mode, digest = ('40000', walk(value)) if isinstance(value, dict) else value
            raw += mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(digest)
        return oid('tree', raw)
    return walk(root)


def save(name, doc):
    (HERE / name).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def node(raw, name):
    return next(n for n in ast.parse(raw).body if getattr(n, 'name', '') == name)


def dump(n):
    return ast.dump(n, include_attributes=False)


def main():
    old_runner = subprocess.check_output(['git', '-C', str(ROOT / 'collaboration/FlagOS-S2-vllm-plugin-FL'),
                                         'show', COMMIT + ':' + RUNNER])
    runner = (HERE / 'files' / RUNNER).read_bytes()
    helper = (HERE / 'files' / HELPER).read_bytes()
    old_helper = (ROOT / 'tmp/compute-order/biv150_compute_order.py').read_bytes()
    assert sha(old_runner) == '97c78bde864cb019fe38831804f08d201a950dd2cfafd15ac5ad77b90a93879f'
    assert sha(runner) == '183de0ab77ab27235eec00e231eb96d4a3b4037a9f628b9397cbe53d17fa3cab'
    assert sha(helper) == '5bc850ebe2643cc4a553efa8e9508871be87d60a3fc30a3053e158b03938cd68'
    edits = json.loads((ROOT / 'tmp/compute-order/files-prepare.json').read_bytes())['runner_edits']
    text = old_runner.decode()
    for edit in edits:
        assert text.count(edit['before']) == 1
        text = text.replace(edit['before'], edit['after'])
    assert text.encode() == runner
    for edit in reversed(edits):
        assert text.count(edit['after']) == 1
        text = text.replace(edit['after'], edit['before'])
    assert text.encode() == old_runner
    assert dump(node(helper, 'Plan')) == dump(node(old_helper, 'Plan'))
    platform = "    platforms = sys.modules.get('vllm.platforms')\n    if getattr(getattr(platforms, 'current_platform', None), 'vendor_name', None) != 'iluvatar':\n        return None\n"
    assert helper.decode().count(platform) == 1
    assert dump(node(helper.decode().replace(platform, ''), 'make_plan')) == dump(node(old_helper, 'make_plan'))
    assert dump(node(helper.decode().replace('    _main_stack(torch)\n', ''), '_cold')) == dump(node(old_helper, '_cold'))
    old_class, new_class = node(old_runner, 'ModelRunnerFL'), node(runner, 'ModelRunnerFL')
    methods = lambda n: {x.name: dump(x) for x in n.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))}
    before, after = methods(old_class), methods(new_class)
    changed = sorted(k for k in before if before[k] != after[k])
    assert changed == ['_build_attention_metadata', '_prepare_inputs', 'execute_model']
    for name, raw in ((RUNNER, runner), (HELPER, helper)):
        compile(raw, name, 'exec')
    tree_raw = (BASE / 'main-tree.json').read_bytes()
    assert sha(tree_raw) == '0f054156787c216c94f24062cf2ef865369a982ff32ff76a9638fa3bfb70e222'
    tree = json.loads(tree_raw)
    entries = {x['path']: dict(mode=x['mode'], sha=x['sha']) for x in tree['tree'] if x['type'] == 'blob'}
    assert len(entries) == 445 and tree_oid(entries) == tree['sha']
    targets = dict(entries)
    targets[RUNNER] = dict(mode=entries[RUNNER]['mode'], sha=oid('blob', runner))
    targets[HELPER] = dict(mode='100644', sha=oid('blob', helper))
    delta = {p: dict(before=entries.get(p), after=targets[p], sha256=sha(raw))
             for p, raw in ((RUNNER, runner), (HELPER, helper))}
    manifest = dict(base_commit=COMMIT, base_tree=tree['sha'], base_blob_count=445,
                    target_tree=tree_oid(targets), target_blob_count=446, changed_paths=delta,
                    base_tree_map_sha256=sha(tree_raw), runtime_tested=False)
    save('candidate-manifest.json', manifest)
    (HERE / 'main-tree.json').write_bytes(tree_raw)
    save('candidate-git-blobs.json', targets)
    base_launcher = (BASE / 'launch_current_main_baseline.py').read_text(encoding='utf-8')
    assert sha(base_launcher.encode()) == '571a9690fb01c0b0efca0f28c0dc5dc71d90fe0de4323bd066ba479c38837802'
    replacements = []
    def replace(old, new):
        nonlocal base_launcher
        assert base_launcher.count(old) == 1, old
        replacements.append(dict(before=old, after=new))
        base_launcher = base_launcher.replace(old, new)
    replace('固定当前main完整Git树→原bc51短服务；不改生产源、SERVER或准确率。',
            '当前main完整Git树加两文件计算序候选→原bc51短服务；不改SERVER或算子。')
    replace("RUNNER_SHA = '97c78bde864cb019fe38831804f08d201a950dd2cfafd15ac5ad77b90a93879f'",
            "BASE_RUNNER_SHA = '97c78bde864cb019fe38831804f08d201a950dd2cfafd15ac5ad77b90a93879f'\nRUNNER_SHA = '" + sha(runner) + "'\nCOMPUTE_HELPER = '" + HELPER + "'\nCOMPUTE_SHA = '" + sha(helper) + "'\nTARGET_TREE = '" + manifest['target_tree'] + "'\nMANIFEST_SHA = '" + sha((HERE / 'candidate-manifest.json').read_bytes()) + "'")
    injected = '''def payload_entries(entries):
    raw = (HERE / 'candidate-manifest.json').read_bytes()
    manifest = json.loads(raw)
    if sha(raw) != MANIFEST_SHA or manifest['base_commit'] != COMMIT or manifest['base_tree'] != TREE:
        raise ValueError('两文件候选manifest身份变化')
    payload = {RUNNER: (HERE / 'files' / RUNNER).read_bytes(),
               COMPUTE_HELPER: (HERE / 'files' / COMPUTE_HELPER).read_bytes()}
    expected = dict(entries)
    for name, data in payload.items():
        pin = RUNNER_SHA if name == RUNNER else COMPUTE_SHA
        if sha(data) != pin:
            raise ValueError('候选payload变化：' + name)
        expected[name] = dict(mode='100644', sha=oid('blob', data))
    delta = {name: dict(before=entries.get(name), after=expected[name], sha256=sha(data))
             for name, data in payload.items()}
    if (manifest['changed_paths'] != delta or len(expected) != 446
            or manifest['target_blob_count'] != 446 or tree_oid(expected) != TARGET_TREE
            or manifest['target_tree'] != TARGET_TREE):
        raise ValueError('不是原main加runner/helper两路径')
    return payload, expected


'''
    replace('def save(path, value):', injected + 'def save(path, value):')
    replace("'current-main-baseline-3283672b-'+stamp", "'current-main-compute-order-3283672b-'+stamp")
    replace("    if args.check_only:\n", "    payload, candidate_entries = payload_entries(entries)\n    if args.check_only:\n")
    replace("status='fixed_current_main_tar_tree_verified_CPU_only', commit=COMMIT, tree=TREE, files=len(entries)",
            "status='fixed_current_main_plus_two_file_payload_verified_CPU_only', commit=COMMIT, base_tree=TREE, target_tree=TARGET_TREE, base_files=445, files=446")
    replace("hashes[RUNNER] != RUNNER_SHA", "hashes[RUNNER] != BASE_RUNNER_SHA")
    replace("    run = ROOT / 'framework' / (stamp + '-current-main-baseline-context16k')", """    base_hashes = dict(hashes)
    for name, data in payload.items():
        target = source / name
        if target.is_symlink():
            raise ValueError('两路径payload不允许覆写symlink')
        target.write_bytes(data)
        target.chmod(0o644)
    blobs, hashes = source_maps(source)
    if (blobs != candidate_entries or hashes[RUNNER] != RUNNER_SHA
            or hashes[COMPUTE_HELPER] != COMPUTE_SHA
            or {k: v for k, v in hashes.items() if k not in payload}
               != {k: v for k, v in base_hashes.items() if k not in payload}):
        raise ValueError('候选不是完整原main加声明两路径')
    run = ROOT / 'framework' / (stamp + '-current-main-compute-order-context16k')""")
    replace("control / 'launch_current_main_baseline.py'", "control / 'launch_compute_order_main.py'")
    replace("    save(control / 'purpose.json'", "    shutil.copyfile(HERE / 'candidate-manifest.json', control / 'candidate-manifest.json')\n    save(control / 'purpose.json'")
    replace("kind='当前main完整代码的独立短服务基线；不是新准确率或优化收益'", "kind='当前main仅两文件计算序候选的独立短服务；不是准确率或稳定收益'")
    replace("source_count=len(hashes), commit=COMMIT, tree=TREE,", "source_count=len(hashes), commit=COMMIT, base_tree=TREE, tree=TARGET_TREE, changed_paths=sorted(payload),")
    replace("accuracy_reused='PR16已有完整105题102/105及原官方4K/16K证据；本轮不重跑'", "historical_evidence='旧423可比单pair+5.124857%和3题P路径辅助质量；不当当前normalized main资格'")
    replace("'只完整main，不叠PR15或实验Q/KV/P资产'", "'完整main仅增P runner/helper，不叠PR15或实验Q/KV/诊断资产'")
    replace("'安装marker不等实际选中，真实NORMALIZATION_SELECTED须本轮后验'", "'安装marker不等实际选中；同Engine真实COMPUTE_ORDER_FIRST_SELECTED及normalization选择须本轮后验，scope拒绝/未命中不是收益'")
    launcher = base_launcher.encode()
    compile(launcher, 'launch_compute_order_main.py', 'exec')
    reverse = base_launcher
    for edit in reversed(replacements):
        assert reverse.count(edit['after']) == 1
        reverse = reverse.replace(edit['after'], edit['before'])
    assert reverse.encode() == (BASE / 'launch_current_main_baseline.py').read_bytes()
    (HERE / 'launch_compute_order_main.py').write_bytes(launcher)
    (HERE / 'launcher.diff').write_text(''.join(difflib.unified_diff(
        (BASE / 'launch_current_main_baseline.py').read_text(encoding='utf-8').splitlines(True),
        base_launcher.splitlines(True), fromfile='baseline571a', tofile='candidate')), encoding='utf-8')
    save('static-check.json', dict(status='CPU_syntax_and_exact_delta_only', base_commit=COMMIT,
        runner_sha256=sha(runner), helper_sha256=sha(helper), launcher_sha256=sha(launcher),
        runner_recipe_edits=len(edits), runner_inverse_exact=True, all_main_footer_bytes_preserved=True,
        changed_runner_methods=changed, original_sample_AST_unchanged=True,
        Plan_AST_unchanged=True, make_plan_except_early_vendor_AST_unchanged=True,
        cold_except_exact_binding_check_AST_unchanged=True, complete_tree_declared=True,
        launcher_inverse_to_571a_exact=True, launcher_identity_edits=len(replacements),
        syntax_compiled=True, tar_recheck_reused='tmp/current-main-baseline/tar-check.json',
        framework_imported=False, GPU_used=False, launcher_executed=False))
    print(json.dumps(dict(helper=sha(helper), runner=sha(runner), launcher=sha(launcher), target_tree=manifest['target_tree'])))


if __name__ == '__main__':
    main()
