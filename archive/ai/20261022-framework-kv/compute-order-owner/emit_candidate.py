"""单SSH发送冻结候选准备资产并启动一个原bc51服务；只由root调用。"""
import base64,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
files={
 'launch_candidate.py':(root/'tmp/compute-order-owner/launch_candidate.py','995d27bc3295bd54d90a213aeb94b0cda072c0f9b3d5f718adf8f8301056699c'),
 'prepare_compute_order.py':(root/'tmp/compute-order/prepare_compute_order.py','b1a804a0c6da15b7c295a4eb5b62d0a6d853fc15d104b6ddcffd36c8a7211670'),
 'biv150_compute_order.py':(root/'tmp/compute-order/biv150_compute_order.py','5ce6f7b6a815ab54d9d9965c30f37362fd1d271c82d442caa76829e01f4938ce'),
 'base-source-sha256.json':(root/'tmp/compute-order/base-source-sha256.json','82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'),
}
payload={}
for name,(path,pin) in files.items():
 data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==pin,name
 payload[name]={'sha256':pin,'data':base64.b64encode(data).decode('ascii')}
encoded=base64.b64encode(json.dumps(payload).encode('ascii')).decode('ascii')
print('import base64,hashlib,json,subprocess\nfrom pathlib import Path')
print('payload=json.loads(base64.b64decode('+repr(encoded)+'))')
print("""
assets=Path('/workspace/experiments/minicpm-s2/scripts/compute-order-candidate-20261023')
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

