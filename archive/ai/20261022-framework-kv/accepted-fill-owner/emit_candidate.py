"""单SSH发送冻结候选准备资产并启动一个原bc51服务；只由root调用。"""
import base64,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
files={
 'launch_candidate.py':(root/'tmp/accepted-fill-owner/launch_candidate.py','e972c800915a319acbd29823e13abb590e56ced8f584bbf4fa2ddfe15c3a7960'),
 'prepare_accepted_fill.py':(root/'tmp/accepted-fill/prepare_accepted_fill.py','410b2c6e07018e745406cec62213fe982945edc6a29c599e3d3696bf6ff4c043'),
 'base-source-sha256.json':(root/'tmp/accepted-fill/base-source-sha256.json','82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'),
}
payload={}
for name,(path,pin) in files.items():
 data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==pin,name
 payload[name]={'sha256':pin,'data':base64.b64encode(data).decode('ascii')}
encoded=base64.b64encode(json.dumps(payload).encode('ascii')).decode('ascii')
print('import base64,hashlib,json,subprocess\nfrom pathlib import Path')
print('payload=json.loads(base64.b64decode('+repr(encoded)+'))')
print("""
assets=Path('/workspace/experiments/minicpm-s2/scripts/accepted-fill-candidate-20261023')
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
subprocess.run(['python3',str(assets/'launch_candidate.py')],check=True)
""")

