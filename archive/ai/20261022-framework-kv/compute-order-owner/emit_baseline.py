"""复用单SSH上传模式；仅发送冻结baseline编排与原422清单。"""
import base64
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
files = {
    'launch_baseline.py': (root/'tmp/compute-order-owner/launch_baseline.py', '90554d08b1a274458e355ad7c7da739740c52da0a5045aee48eea16757447abe'),
    'base-source-sha256.json': (root/'tmp/q-gqa-mixed-coverage-only/base-source-sha256.json', '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'),
}
payload = {}
for name, (path, pin) in files.items():
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == pin, name
    payload[name] = {'sha256': pin, 'data': base64.b64encode(data).decode('ascii')}
encoded = base64.b64encode(json.dumps(payload).encode('ascii')).decode('ascii')
print('import base64,hashlib,json,subprocess\nfrom pathlib import Path')
print('payload=json.loads(base64.b64decode(' + repr(encoded) + '))')
print("""
assets=Path('/workspace/experiments/minicpm-s2/scripts/compute-order-baseline-20261023')
assets.mkdir(exist_ok=True)
for name,item in payload.items():
    assert Path(name).name==name
    data=base64.b64decode(item['data'])
    assert hashlib.sha256(data).hexdigest()==item['sha256']
    target=assets/name
    if target.exists():
        assert target.is_file() and not target.is_symlink() and target.read_bytes()==data
    else:
        with target.open('xb') as f:f.write(data)
subprocess.run(['python3',str(assets/'launch_baseline.py')],check=True)
""")
