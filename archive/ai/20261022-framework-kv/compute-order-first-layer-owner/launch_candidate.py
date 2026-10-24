"""一次自然命中的计算顺序shadow诊断；原bc51负责SERVER/单卡锁/清理，不计性能。"""
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
deployment_path = assets / 'deployment.json'
assert sha(deployment_path) == '984d853e284de2611865e2f2735f01c571019457b1aa689853c50fe1cbcf984d'
receipt = json.loads(deployment_path.read_text())
expected = receipt['output_map']
assert receipt['source_count'] == len(expected) == 424
assert receipt['changed_paths'] == ['vllm_fl/patches/biv150_compute_order.py', 'vllm_fl/patches/biv150_compute_order_shadow.py', 'vllm_fl/patches/biv150_kv_protocol.py', 'vllm_fl/patches/biv150_kv_worker.py', 'vllm_fl/worker/model_runner.py']
for rel in receipt['changed_paths']:
    assert sha(assets / 'files' / rel) == expected[rel], rel
base_source = SOURCE
SOURCE = ROOT / 'code' / ('compute-order-first-layer-' + stamp)
assert not SOURCE.exists()
shutil.copytree(base_source, SOURCE, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
for rel in receipt['changed_paths']:
    destination = SOURCE / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(assets / 'files' / rel, destination)
assert mapping(SOURCE) == expected
prepared = deployment_path
reference_bytes = (json.dumps(expected, indent=2) + '\n').encode()
run = ROOT / 'framework' / (stamp + '-compute-order-first-layer-context16k')
control = run.with_name(run.name + '-control')
assert not run.exists()
control.mkdir()
shutil.copyfile(prepared, control / 'prepare.json')
shutil.copytree(assets / 'files', control / 'changed-source')
shutil.copyfile(__file__, control / 'launch_candidate.py')
shutil.copyfile(asset_map, control / 'base-source-sha256.json')
shutil.copytree(SOURCE, control / 'plugin-source')
assert mapping(control / 'plugin-source') == expected and mapping(SOURCE) == expected
(control / 'source-sha256.json').write_bytes(reference_bytes)
(control / 'purpose.json').write_text(json.dumps({
    'kind': '单次原序shadow与P生产首层Attention和logits诊断；不采第二次样、不计性能',
    'variant': 'shadow-diagnostic', 'source': str(SOURCE), 'source_count': 424,
    'reference_control': str(REFERENCE), 'comparison_baseline': None, 'verify_restore': '0',
    'limits': ['不改官方SERVER；原context-screen/seed721201', '必须有实际shadow完成证据；未命中为未覆盖；不同bit不自动等于算法错误；不自动排第二任务'],
}, ensure_ascii=False, indent=2) + '\n')
shutil.copyfile(ROOT / 'scripts/snapshot_tuning_db.py', control / 'snapshot_tuning_db.py')
with (control / 'db-before.log').open('x') as output:
    subprocess.run(['python3', str(control / 'snapshot_tuning_db.py'), '--database',
        '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db', '--output', str(control / 'db-before')],
        stdout=output, stderr=subprocess.STDOUT, check=True)
(control / 'q-hoist-artifacts').mkdir()
(control / 'shadow-artifacts').mkdir()
command = ['env', '-u', 'BIV150_FINITE_GROWTH_ADMISSION',
    'BIV150_COMPUTE_ORDER_SHADOW_DIR=' + str(control / 'shadow-artifacts'),
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
