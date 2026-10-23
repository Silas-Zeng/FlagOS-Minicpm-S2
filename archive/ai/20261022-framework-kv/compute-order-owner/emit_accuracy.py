"""上传已冻结的423准确率入口，先Bash语法检查，再启动原35d唯一owner。"""
import base64,hashlib,json
from pathlib import Path
here=Path(__file__).resolve().parent
spec={
 'launch.sh':(here/'launch_compute_order_accuracy.sh','34bce35fb0a9d6df3227281a1e27edee39704d9fde8b2e0b99d9e8211fbfc3dd'),
 'expected-source-sha256.json':(here/'accuracy-source-sha256.json','6cf2e1d7e3084d95e0fd8db23ceaa426c5c5ab6ff887dffcd8f036e60b98a7b9'),
}
payload={}
for name,(path,pin) in spec.items():
 data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==pin,name
 payload[name]={'sha256':pin,'data':base64.b64encode(data).decode('ascii')}
encoded=base64.b64encode(json.dumps(payload).encode('ascii')).decode('ascii')
print('import base64,hashlib,json,subprocess\nfrom pathlib import Path')
print('payload=json.loads(base64.b64decode('+repr(encoded)+'))')
print("""
assets=Path('/workspace/experiments/minicpm-s2/scripts/compute-order-accuracy-20261023')
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
subprocess.run(['bash','-n',str(assets/'launch.sh')],check=True)
subprocess.run(['bash',str(assets/'launch.sh')],check=True)
""")

