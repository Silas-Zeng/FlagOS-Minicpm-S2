"""发送只改标签的原422编排；GPU运行及清理由原bc51负责。"""
import base64, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
files = {
    'launch_baseline.py': (root/'tmp/accepted-fill-owner/launch_baseline.py', '7049cfd0bd207b1daad3e943da9281b133729cedced99ac9b754562580a8c000'),
    'base-source-sha256.json': (root/'tmp/accepted-fill/base-source-sha256.json', '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'),
}
payload = {}
for name, (path, pin) in files.items():
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == pin
    payload[name] = {'sha256': pin, 'data': base64.b64encode(raw).decode()}
print('import base64,hashlib,json,subprocess\nfrom pathlib import Path')
print('payload=json.loads(base64.b64decode('+repr(base64.b64encode(json.dumps(payload).encode()).decode())+'))')
print("""
assets=Path('/workspace/experiments/minicpm-s2/scripts/accepted-fill-baseline-20261023')
assets.mkdir(exist_ok=True)
for name,item in payload.items():
    assert Path(name).name==name
    raw=base64.b64decode(item['data']);assert hashlib.sha256(raw).hexdigest()==item['sha256']
    target=assets/name
    if target.exists():
        assert target.is_file() and not target.is_symlink() and target.read_bytes()==raw
    else:
        with target.open('xb') as stream:stream.write(raw)
subprocess.run(['python3',str(assets/'launch_baseline.py')],check=True)
""")
