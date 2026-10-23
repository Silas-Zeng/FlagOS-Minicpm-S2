"""复用已审 owner；从本地完整候选树冻结增量，准备一次原负载 shadow 诊断。"""
import argparse
import base64
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
sha = lambda data: hashlib.sha256(data).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--prepared-dir', required=True, type=Path)
parser.add_argument('--receipt', required=True, type=Path)
args = parser.parse_args()
prepared = args.prepared_dir.resolve()
assert prepared.is_relative_to(ROOT / 'tmp/compute-order-oracle-gate')
base_bytes = (ROOT / 'tmp/compute-order/base-source-sha256.json').read_bytes()
assert sha(base_bytes) == '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
base = json.loads(base_bytes)
emitted = {}
for path in sorted(prepared.rglob('*')):
    rel = path.relative_to(prepared)
    if any(part in ('.git', '__pycache__') for part in rel.parts) or path.suffix in ('.pyc', '.pyo'):
        continue
    assert not path.is_symlink(), path
    if path.is_file():
        emitted[rel.as_posix()] = sha(path.read_bytes())
target = json.loads(args.receipt.read_text(encoding='utf-8'))['output_map']
assert set(base) <= set(target) and 423 <= len(target) <= 425
changed = sorted(k for k in target if target[k] != base.get(k))
assert emitted in (target, {k: target[k] for k in changed})
assert all(k == 'vllm_fl/worker/model_runner.py' or k.startswith('vllm_fl/patches/biv150_') for k in changed)
assert 4 <= len(changed) <= 7
for rel in changed:
    output = HERE / 'files' / rel
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes((prepared / rel).read_bytes())
deployment = dict(kind='单次自然命中的首层实际KV采集供独立oracle与logits诊断，不是性能成绩',
                  source_count=len(target), output_map=target, changed_paths=changed)
deployment_bytes = (json.dumps(deployment, ensure_ascii=False, indent=2) + '\n').encode()
(HERE / 'deployment.json').write_bytes(deployment_bytes)
(HERE / 'base-source-sha256.json').write_bytes(base_bytes)
old = (ROOT / 'tmp/compute-order-owner/launch_candidate.py').read_bytes()
assert sha(old) == '995d27bc3295bd54d90a213aeb94b0cda072c0f9b3d5f718adf8f8301056699c'
text = old.decode()
edits = []
def replace(a, b):
    global text
    assert text.count(a) == 1, a
    text = text.replace(a, b)
    edits.append((a, b))

start = text.index("assets = Path(__file__).parent\n")
end = text.index("reference_bytes = (json.dumps(expected, indent=2)", start)
replace(text[start:end], f'''assets = Path(__file__).parent
deployment_path = assets / 'deployment.json'
assert sha(deployment_path) == {sha(deployment_bytes)!r}
receipt = json.loads(deployment_path.read_text())
expected = receipt['output_map']
assert receipt['source_count'] == len(expected) == {len(target)}
assert receipt['changed_paths'] == {changed!r}
for rel in receipt['changed_paths']:
    assert sha(assets / 'files' / rel) == expected[rel], rel
base_source = SOURCE
SOURCE = ROOT / 'code' / ('compute-order-oracle-' + stamp)
assert not SOURCE.exists()
shutil.copytree(base_source, SOURCE, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
for rel in receipt['changed_paths']:
    destination = SOURCE / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(assets / 'files' / rel, destination)
assert mapping(SOURCE) == expected
prepared = deployment_path
''')
replace('计算序423短服务：固定四路径变化，原bc51负责SERVER/单卡锁/清理；非准确率证明。', '一次自然命中的计算顺序shadow诊断；原bc51负责SERVER/单卡锁/清理，不计性能。')
replace("stamp + '-compute-order-candidate-context16k'", "stamp + '-compute-order-oracle-context16k'")
replace("for name in ('prepare_compute_order.py', 'biv150_compute_order.py'):\n    shutil.copyfile(assets / name, control / name)", "shutil.copytree(assets / 'files', control / 'changed-source')")
replace("'计算序423短服务；无profiler；实际命中和32/0只作集成及性能信号，不替代数值/准确率'", "'单次原序/P首层对照与一请求KV采集供独立oracle；不采第二次样、不计性能'")
replace("'variant': 'candidate', 'source': str(SOURCE), 'source_count': 423", f"'variant': 'shadow-diagnostic', 'source': str(SOURCE), 'source_count': {len(target)}")
replace("'reference_control': str(REFERENCE), 'comparison_baseline': '20261023T054306Z-compute-order-baseline-context16k', 'verify_restore': '0'", "'reference_control': str(REFERENCE), 'comparison_baseline': None, 'verify_restore': '0'")
replace("'不继承原accuracy；收益须同DB/KV等可比性且实际命中；不自动排第二任务'", "'必须有实际shadow完成证据；未命中为未覆盖；不同bit不自动等于算法错误；不自动排第二任务'")
replace("(control / 'q-hoist-artifacts').mkdir()", "(control / 'q-hoist-artifacts').mkdir()\n(control / 'shadow-artifacts').mkdir()")
replace("'BIV150_KV_VERIFY_RESTORE=0', 'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR='", "'BIV150_COMPUTE_ORDER_SHADOW_DIR=' + str(control / 'shadow-artifacts'),\n    'BIV150_KV_VERIFY_RESTORE=0', 'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR='")
reverse = text
for a, b in reversed(edits):
    assert reverse.count(b) == 1
    reverse = reverse.replace(b, a)
assert reverse.encode() == old
compile(text, 'launch_candidate.py', 'exec')
(HERE / 'launch_candidate.py').write_text(text, encoding='utf-8', newline='\n')
(HERE / 'owner.diff').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True), text.splitlines(True), fromfile='original-owner', tofile='shadow-owner')), encoding='utf-8', newline='\n')
payload = {}
for path in [HERE / 'launch_candidate.py', HERE / 'deployment.json', HERE / 'base-source-sha256.json', *[HERE / 'files' / rel for rel in changed]]:
    data = path.read_bytes()
    payload[path.relative_to(HERE).as_posix()] = dict(sha256=sha(data), data=base64.b64encode(data).decode())
(HERE / 'payload.json').write_text(json.dumps(payload), encoding='utf-8', newline='\n')
(HERE / 'owner-preparation.json').write_text(json.dumps(dict(original_owner_sha256=sha(old), launch_sha256=sha(text.encode()), deployment_sha256=sha(deployment_bytes), changes=len(edits), inverse_exact=True, compiled=True, source_count=len(target), changed_paths=changed), ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
print((HERE / 'owner-preparation.json').read_text())
