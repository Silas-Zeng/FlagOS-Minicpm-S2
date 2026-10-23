"""仅修客户端内部采样长度校验及其身份锁；保持所有模型与事件编排字节。"""
import base64
import hashlib
import json
import shutil
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'experiments/registry.csv').is_file())
old = ROOT / 'tmp/compute-order-math4-event-owner'
fix = ROOT / 'tmp/compute-order-math4-event-fix'
out = ROOT / 'tmp/compute-order-math4-event-fix-owner'
sha = lambda data: hashlib.sha256(data).hexdigest()
old_gate = '7cf010d7cf123e51abfc32dc1a51a8c4bee835a413b50bf0747b38f37653214b'
new_gate = 'b7422674fb183afe95aa909dffb12fe7ed56f574b6de768c78230a8267628604'
data = (fix / 'gate_benchmark_requests.py').read_bytes()
assert sha(data) == new_gate
cpu = json.loads((fix / 'cpu-original-samples.json').read_text(encoding='utf-8'))
assert len(cpu['rows']) == 32 and cpu['num_special_tokens_to_add'] == 1
assert all(r['prompt_len'] == 16383 and r['multi_modal_is_none'] and r['expected_output_len'] == 128 for r in cpu['rows'])
if out.exists():
    # 仅允许恢复首次复制后、尚未发生任何编辑的准备阶段。
    maps = lambda folder: {p.relative_to(folder).as_posix():sha(p.read_bytes()) for p in folder.rglob('*') if p.is_file()}
    assert maps(out) == maps(old)
else:
    shutil.copytree(old, out)
checks = {}
def replace_one(name, before, after):
    original = (old / name).read_bytes()
    assert original.count(before.encode()) == 1
    updated = original.replace(before.encode(), after.encode())
    assert updated.replace(after.encode(), before.encode()) == original
    (out / name).write_bytes(updated)
    checks[name] = dict(old_sha256=sha(original), sha256=sha(updated), inverse_exact=True)
    return sha(updated)

(out / 'gate_benchmark_requests.py').write_bytes(data)
load_sha = replace_one('run_math4_event_load.py', old_gate, new_gate)
owner_sha = replace_one('run_math4_event_gate.py',
    'f7013086ceb89d2924c9921b8f3898a919c0d694448f30200005de7d0ee4c368', load_sha)
deployment = json.loads((old / 'deployment.json').read_text(encoding='utf-8'))
deployment['diagnostic_asset_sha256'].update({
    'gate_benchmark_requests.py':new_gate, 'run_math4_event_load.py':load_sha,
    'run_math4_event_gate.py':owner_sha})
deploy_data = (json.dumps(deployment, ensure_ascii=False, indent=2) + '\n').encode()
(out / 'deployment.json').write_bytes(deploy_data)
launch_sha = replace_one('launch_candidate.py',
    '03f2d1da9caa0448ac8bc69118e974161cdbb3044297cf18fe65cf3af4dace42', sha(deploy_data))
replace_one('emit_start.py', 'compute-order-math4-event-20261023', 'compute-order-math4-event-fix1-20261023')
original_payload = json.loads((old / 'payload.json').read_text())
payload = {}
for rel in original_payload:
    raw = (out / rel).read_bytes()
    if rel.endswith('.py'): compile(raw, rel, 'exec')
    payload[rel] = dict(sha256=sha(raw), data=base64.b64encode(raw).decode())
assert len(payload) == 14
assert all(payload[k] == v for k,v in original_payload.items() if k.startswith('files/'))
(out / 'payload.json').write_text(json.dumps(payload), encoding='utf-8')
result = dict(kind='125330发送前校验错误修复；不改变题目/采样/模型/时序',
    changed_only_gate_guard=True, model_files_unchanged=True, checks=checks,
    gate_sha256=new_gate, deployment_sha256=sha(deploy_data), launch_sha256=launch_sha,
    original_cpu_samples_sha256=sha((fix/'cpu-original-samples.json').read_bytes()),
    syntax_pass=True, gpu_run=False)
(out / 'preparation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
