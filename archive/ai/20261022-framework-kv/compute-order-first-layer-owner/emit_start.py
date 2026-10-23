"""将冻结的 shadow 增量经 SSH stdin 发送；输出代码只由 root 派发一次。"""
import base64
import hashlib
import json
from pathlib import Path

here = Path(__file__).parent
payload = json.loads((here / 'payload.json').read_text())
for rel, item in payload.items():
    data = (here / rel).read_bytes()
    assert hashlib.sha256(data).hexdigest() == item['sha256'], rel
    assert base64.b64decode(item['data']) == data
encoded = base64.b64encode(json.dumps(payload).encode()).decode()
print('import base64, hashlib, json, subprocess\nfrom pathlib import Path')
print('payload=json.loads(base64.b64decode(' + repr(encoded) + '))')
print('''
assets = Path('/workspace/experiments/minicpm-s2/scripts/compute-order-first-layer-20261023')
assets.mkdir(exist_ok=True)
for rel, item in payload.items():
    relative = Path(rel)
    assert not relative.is_absolute() and '..' not in relative.parts
    assert rel in ('launch_candidate.py', 'deployment.json', 'base-source-sha256.json') or rel.startswith('files/vllm_fl/')
    data = base64.b64decode(item['data'])
    assert hashlib.sha256(data).hexdigest() == item['sha256']
    target = assets / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.is_file() and not target.is_symlink() and target.read_bytes() == data
    else:
        with target.open('xb') as handle:
            handle.write(data)
subprocess.run(['python3', str(assets / 'launch_candidate.py')], check=True)
''')
