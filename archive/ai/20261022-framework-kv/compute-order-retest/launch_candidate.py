"""计算序423短服务：固定四路径变化，原bc51负责SERVER/单卡锁/清理；非准确率证明。"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import socket
import subprocess

ROOT = Path('/workspace/experiments/minicpm-s2')
SOURCE = ROOT / 'code/q-gqa-kv-swap-20261022T213134Z'
REFERENCE = ROOT / 'framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, pin in {
    'run_framework_screen.py': 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
    'snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}.items():
    assert sha(ROOT / 'scripts' / name) == pin, name
reference_bytes = (REFERENCE / 'source-sha256.json').read_bytes()
expected = json.loads(reference_bytes)
assert len(expected) == 422
assert expected['vllm_fl/worker/model_runner.py'] == 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
asset_map = Path(__file__).with_name('base-source-sha256.json')
assert sha(asset_map) == '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
assert json.loads(asset_map.read_text()) == expected

def mapping(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(x in ('.git', '__pycache__') for x in rel.parts) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            assert target.is_file() and target.is_relative_to(folder), rel
        if path.is_file():
            result[rel.as_posix()] = sha(path)
    return result

assert mapping(SOURCE) == expected
query = subprocess.check_output(['ixsmi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True)
table = subprocess.check_output(['ixsmi'], text=True)
assert query.strip() == '68, 0' and 'No running processes found' in table
assert 'BI-V150' in table and '32768MiB' in table
for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        assert sock.connect_ex((host, 9031)) != 0, host

stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
assets = Path(__file__).parent
for name, pin in {
    'prepare_compute_order.py': 'b1a804a0c6da15b7c295a4eb5b62d0a6d853fc15d104b6ddcffd36c8a7211670',
    'biv150_compute_order.py': '5ce6f7b6a815ab54d9d9965c30f37362fd1d271c82d442caa76829e01f4938ce',
}.items():
    assert sha(assets / name) == pin, name
base_source = SOURCE
SOURCE = ROOT / 'code' / ('compute-order-' + stamp)
subprocess.run(['python3', str(assets / 'prepare_compute_order.py'), '--base', str(base_source), '--output', str(SOURCE)], check=True)
prepared = SOURCE.with_name(SOURCE.name + '-prepare.json')
receipt = json.loads(prepared.read_text())
expected = receipt['output_map']
assert receipt['source_count'] == len(expected) == 423
assert expected['vllm_fl/worker/model_runner.py'] == 'ea64a59cff6197c42babbc190246ab24dce4f540874b2025c0f4ebfee02195ac'
assert set(receipt['changed_paths']) == {
    'vllm_fl/patches/biv150_compute_order.py', 'vllm_fl/worker/model_runner.py',
    'vllm_fl/patches/biv150_kv_worker.py', 'vllm_fl/patches/biv150_kv_protocol.py'}
assert mapping(SOURCE) == expected
reference_bytes = (json.dumps(expected, indent=2) + '\n').encode()
run = ROOT / 'framework' / (stamp + '-compute-order-candidate-context16k')
control = run.with_name(run.name + '-control')
assert not run.exists()
control.mkdir()
shutil.copyfile(prepared, control / 'prepare.json')
for name in ('prepare_compute_order.py', 'biv150_compute_order.py'):
    shutil.copyfile(assets / name, control / name)
shutil.copyfile(__file__, control / 'launch_candidate.py')
shutil.copyfile(asset_map, control / 'base-source-sha256.json')
shutil.copytree(SOURCE, control / 'plugin-source')
assert mapping(control / 'plugin-source') == expected and mapping(SOURCE) == expected
(control / 'source-sha256.json').write_bytes(reference_bytes)
(control / 'purpose.json').write_text(json.dumps({
    'kind': '计算序423短服务；无profiler；实际命中和32/0只作集成及性能信号，不替代数值/准确率',
    'variant': 'candidate', 'source': str(SOURCE), 'source_count': 423,
    'reference_control': str(REFERENCE), 'comparison_baseline': '20261023T120949Z-compute-order-baseline-context16k', 'verify_restore': '0',
    'limits': ['不改官方SERVER；原context-screen/seed721201', '不继承原accuracy；收益须同DB/KV等可比性且实际命中；不自动排第二任务'],
}, ensure_ascii=False, indent=2) + '\n')
shutil.copyfile(ROOT / 'scripts/snapshot_tuning_db.py', control / 'snapshot_tuning_db.py')
with (control / 'db-before.log').open('x') as output:
    subprocess.run(['python3', str(control / 'snapshot_tuning_db.py'), '--database',
        '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db', '--output', str(control / 'db-before')],
        stdout=output, stderr=subprocess.STDOUT, check=True)
(control / 'q-hoist-artifacts').mkdir()
command = ['env', '-u', 'BIV150_FINITE_GROWTH_ADMISSION',
    'BIV150_KV_VERIFY_RESTORE=0', 'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=' + str(control / 'q-hoist-artifacts'),
    'python3', str(ROOT / 'scripts/run_framework_screen.py'), str(run), '--source-dir', str(SOURCE),
    '--context-screen', '--seed', '721201', '--require-log-marker', 'BIV150_KV_PROTOCOL_INSTALLED']
(control / 'command.txt').write_text(shlex.join(command) + '\n')
for name in ('MINICPM_NATIVE_PROFILE_EVENTS', 'MINICPM_DECODE_GAP_RUN_DIR'):
    assert name not in os.environ, name
with (control / 'runner.log').open('x') as output:
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=output,
        stderr=subprocess.STDOUT, start_new_session=True)
(control / 'runner.pid').write_text(str(process.pid) + '\n')
print(json.dumps({'run': str(run), 'control': str(control), 'source': str(SOURCE),
    'runner_pid': process.pid, 'preflight_gpu': query.strip(), 'owner': '原bc51 driver'}, ensure_ascii=False))
