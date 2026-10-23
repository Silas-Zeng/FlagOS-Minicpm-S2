"""将已审五件资产编码为单次SSH输入；校验后运行原launcher，不改实验逻辑。"""
from pathlib import Path
import base64
import hashlib
import json

root = Path(__file__).resolve().parent
pins = json.loads((root / 'cpu-preparation.json').read_text(encoding='utf-8'))['assets']
payload = {}
for name, expected in pins.items():
    data = (root / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected, name
    payload[name] = {'sha256': expected, 'base64': base64.b64encode(data).decode('ascii')}
encoded = base64.b64encode(json.dumps(payload).encode('ascii')).decode('ascii')
print('import base64,hashlib,json,subprocess\nfrom pathlib import Path')
print('payload=json.loads(base64.b64decode(' + repr(encoded) + '))')
print("""
assets=Path('/workspace/experiments/minicpm-s2/scripts/q-gqa-mixed-coverage-only-20261023T005000Z')
assert assets.is_dir()
for name,item in payload.items():
    assert Path(name).name == name
    data=base64.b64decode(item['base64'])
    assert hashlib.sha256(data).hexdigest()==item['sha256'],name
    path=assets/name
    if path.exists():
        assert path.is_file() and not path.is_symlink() and path.read_bytes()==data,name
    else:
        with path.open('xb') as output:output.write(data)
print(json.dumps({'assets_checked':len(payload),'assets':str(assets)}),flush=True)
subprocess.run(['bash',str(assets/'launch_mixed_coverage.sh')],check=True)
""")
