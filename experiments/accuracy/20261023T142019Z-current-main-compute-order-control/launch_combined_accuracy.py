"""复用141159受测446源码，交原35d owner运行原105题；不重建源码或评测。"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
REFERENCE_NAME = '20261023T141159Z-current-main-compute-order-context16k'
REFERENCE = ROOT / 'framework' / REFERENCE_NAME
CONTROL = REFERENCE.with_name(REFERENCE_NAME + '-control')
SOURCE = ROOT / 'code/current-main-compute-order-3283672b-20261023T141159Z'
COMMIT = '3283672b92fa30f93f652b242193999836a95f88'
TREE = '5c77e68caff6aa0c8b6c230adb78a2d4c293cca1'
BLOBS_SHA = '340e2ce1254510864d2b8b8d90939a98622f70a28f10573f9a887eebface106e'
MANIFEST_SHA = '0b17b3a18fc89a3968f409d9e340190a19ffd4e7aadec3f456293f91281f4ec4'
LAUNCH_SHA = '88b35410fc49d1d259ebad0cc910c623a5cea2723220707932e38544f3c89e02'
SCRIPTS = {
    'run_accuracy_gate.py': '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54',
    'run_math500_level3.sh': '6e045c1cda5a6379ddff1bf7c41ab1e4cbaaddd51b2ca9b4b1d2a92cfa8bb5f4',
    'snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
    'monitor_gpu.sh': 'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def source_maps(source):
    # 复用已审owner的Git link文字/mode及常规目标内容SHA两种身份。
    blobs, hashes = {}, {}
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source)
        if any(x in ('.git', '__pycache__') for x in relative.parts) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink():
            if not path.resolve(strict=True).is_relative_to(source):
                raise ValueError('source symlink越界')
            data, mode = os.readlink(path).encode(), '120000'
        elif path.is_file():
            data, mode = path.read_bytes(), '100755' if path.stat().st_mode & 0o111 else '100644'
        else:
            continue
        digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        blobs[relative.as_posix()] = dict(mode=mode, sha=digest)
        hashes[relative.as_posix()] = sha(path)
    return blobs, hashes


def reference_ready():
    if sha(HERE / 'candidate-git-blobs.json') != BLOBS_SHA or sha(HERE / 'candidate-manifest.json') != MANIFEST_SHA:
        raise ValueError('冻结候选身份材料变化')
    expected, manifest = read(HERE / 'candidate-git-blobs.json'), read(HERE / 'candidate-manifest.json')
    if (len(expected) != 446 or manifest['base_commit'] != COMMIT
            or manifest['target_tree'] != TREE or manifest['target_blob_count'] != 446):
        raise ValueError('非冻结current-main+P完整446树')
    if (REFERENCE / 'exit-code').read_text().strip() != '0':
        raise ValueError('141159短测未成功结束')
    purpose, post = read(CONTROL / 'purpose.json'), read(REFERENCE / 'postflight-full.json')
    if (purpose['source'] != str(SOURCE) or purpose['commit'] != COMMIT or purpose['tree'] != TREE
            or purpose['source_count'] != 446 or post['source_count'] != 446
            or post['source_failures'] or post['query'].strip() != '68, 0'
            or not all(post['ports_closed'].values())
            or not all(value is None or '\nState:\tZ ' in value for value in post['owned_process_status'].values())):
        raise ValueError('短测源码/清理后态不完整')
    if (sha(CONTROL / 'launch_compute_order_main.py') != LAUNCH_SHA
            or sha(CONTROL / 'candidate-manifest.json') != MANIFEST_SHA
            or read(CONTROL / 'source-git-blobs.json') != expected):
        raise ValueError('受测control身份不符')
    hashes = read(CONTROL / 'source-sha256.json')
    if SOURCE.is_symlink() or source_maps(SOURCE) != (expected, hashes) or source_maps(CONTROL / 'plugin-source') != (expected, hashes):
        raise ValueError('受测完整源码/Git blobs/mode/内容已变化')
    log = (REFERENCE / 'server.log').read_text(errors='replace')
    selected, normalized = set(), set()
    for line in log.splitlines():
        pid = re.search(r'EngineCore pid=(\d+)', line)
        if not pid:
            continue
        if 'BIV150_COMPUTE_ORDER_FIRST_SELECTED ' in line:
            item = json.loads(line.split('BIV150_COMPUTE_ORDER_FIRST_SELECTED ', 1)[1])
            if (item.get('pid') == int(pid.group(1)) and item.get('original_model_forward_returned') is True
                    and item.get('runtime_mode') == 'NONE' and item.get('sampler_rows') == item.get('N')
                    and item.get('outside', 0) > 0):
                selected.add(int(pid.group(1)))
        if 'BIV150_PREFILL_NORMALIZATION_SELECTED ' in line:
            normalized.add(int(pid.group(1)))
    if len(selected) != 1 or not selected.issubset(normalized) or 'BIV150_COMPUTE_ORDER_SCOPE_REJECTED ' in log:
        raise ValueError('短测缺同Engine真实P/normalization命中或有scope拒绝')
    return expected, hashes, sorted(selected)


def main():
    blobs, hashes, selected = reference_ready()
    for name, pin in SCRIPTS.items():
        if sha(ROOT / 'scripts' / name) != pin:
            raise ValueError('原准确率owner/评测/快照/monitor变化：' + name)
    env = os.environ.copy()
    removed = [name for name in env if name.startswith('BIV150_') or name in
               ('MINICPM_NATIVE_PROFILE_EVENTS', 'MINICPM_DECODE_GAP_RUN_DIR')]
    for name in removed:
        env.pop(name)
    for name in ('VLLM_FL_BIV150_PREFILL_NORMALIZE', 'VLLM_FL_BIV150_GQA_DECODE'):
        if env.get(name, '1') != '1':
            raise ValueError('不允许关闭受测normalized/GQA：' + name)
    run = ROOT / 'accuracy' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-current-main-compute-order')
    control = run.with_name(run.name + '-control')
    if run.exists():
        raise FileExistsError(run)
    control.mkdir(parents=True, exist_ok=False)
    shutil.copytree(SOURCE, control / 'plugin-source', symlinks=True,
                    ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    if source_maps(SOURCE) != (blobs, hashes) or source_maps(control / 'plugin-source') != (blobs, hashes):
        raise ValueError('归档期间源码变化')
    save(control / 'source-sha256.json', hashes)
    save(control / 'source-git-blobs.json', blobs)
    for name in ('candidate-git-blobs.json', 'candidate-manifest.json'):
        shutil.copyfile(HERE / name, control / name)
    shutil.copyfile(__file__, control / 'launch_combined_accuracy.py')
    save(control / 'reference-short-screen.json', dict(run=REFERENCE_NAME, source=str(SOURCE),
        selected_engine_pids=selected, source_count=446, candidate_tree=TREE,
        postflight_sha256=sha(REFERENCE / 'postflight-full.json'), server_log_sha256=sha(REFERENCE / 'server.log')))
    save(control / 'purpose.json', dict(kind='当前main加P的独立完整105题准确率，尚未通过',
        source=str(SOURCE), source_count=446, base_commit=COMMIT, tree=TREE,
        reference_short_screen=REFERENCE_NAME, removed_environment_names=sorted(removed),
        limits=['复用受测446源码，不重建tar、不叠PR15/旧Qservice/KV事务或诊断资产',
            '原35d/6e045/105题/SERVER/DB/设备锁及清理不变，非性能测试',
            '准确率本轮P可能0命中，须如实限定覆盖；不继承队友main102/105或旧423成绩']))
    command = ['python3', str(ROOT / 'scripts/run_accuracy_gate.py'), str(run), '--source-dir', str(SOURCE),
        '--require-log-marker', 'BIV150_PREFILL_NORMALIZATION_INSTALL', '--database',
        '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db']
    (control / 'command.txt').write_text(shlex.join(command) + '\n', encoding='utf-8')
    save(control / 'scripts-sha256.json', SCRIPTS)
    with (control / 'runner.log').open('x') as log:
        process = subprocess.Popen(command, cwd='/workspace', env=env, stdin=subprocess.DEVNULL,
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    (control / 'runner.pid').write_text(str(process.pid) + '\n')
    print(json.dumps(dict(run=str(run), control=str(control), source=str(SOURCE), runner_pid=process.pid)))


if __name__ == '__main__':
    main()
