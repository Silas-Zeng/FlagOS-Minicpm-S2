"""仅上传已审门素材到独立目录，不编译、不启动设备任务。"""
from pathlib import Path
import ast
import base64
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEST = '/workspace/experiments/minicpm-s2/scripts/kv-pitched-restore-gate/'
controller = HERE/'launch_kv_pitched_restore_gate.py'
assert hashlib.sha256(controller.read_bytes()).hexdigest() == 'ed7331a693719a5db950527812eac3072432d8bc4e6db2da1cd32fcbed6f4862'
sources, = [ast.literal_eval(n.value) for n in ast.parse(controller.read_bytes()).body
            if isinstance(n, ast.Assign) and len(n.targets)==1
            and isinstance(n.targets[0], ast.Name) and n.targets[0].id=='SOURCES']
known = {
    'biv150_kv_pitched_copy.py':ROOT/'tmp/q-gqa-kv-swap/biv150_kv_pitched_copy.py',
    'biv150_kv_page_copy.py':ROOT/'tmp/q-gqa-kv-swap/biv150_kv_page_copy.py',
    'validate_kv_pitched_copy.py':ROOT/'scripts/remote/validate_kv_pitched_copy.py',
    'memcpy2d-abi.json':ROOT/'experiments/framework/20261022T032653Z-kv-pitched-copy-gate/source/memcpy2d-abi.json',
}
payload = {}
for remote, pin in sources.values():
    assert remote.startswith(DEST)
    name = remote[len(DEST):]
    assert '/' not in name
    raw = known.get(name, HERE/name).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==pin, name
    payload[name] = {'sha256':pin, 'base64':base64.b64encode(raw).decode()}
payload[controller.name] = {'sha256':hashlib.sha256(controller.read_bytes()).hexdigest(),
                          'base64':base64.b64encode(controller.read_bytes()).decode()}
encoded = base64.b64encode(json.dumps(payload).encode()).decode()
script = f'''from pathlib import Path
import base64,hashlib,json
dest=Path({DEST!r})
assert not dest.is_symlink()
dest.mkdir(exist_ok=True)
payload=json.loads(base64.b64decode({encoded!r}))
for name,item in payload.items():
    path=dest/name
    raw=base64.b64decode(item['base64'])
    assert hashlib.sha256(raw).hexdigest()==item['sha256']
    assert not path.is_symlink()
    if path.exists():
        assert path.read_bytes()==raw, '已有不同素材，拒绝覆盖'
    else:
        with path.open('xb') as f: f.write(raw)
print(json.dumps({{'uploaded_to':str(dest),'files':{{n:i['sha256'] for n,i in payload.items()}},'GPU_started':False}}))
'''
args = ['ssh','-F','NUL','-i','C:/Users/Administrator/.ssh/id_ed25519_flagos_s2',
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes',
        '-o','ConnectTimeout=12','-p','2224',
        'lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io','python3 -']
result=subprocess.run(args,input=script.encode(),capture_output=True,timeout=45)
sys.stdout.buffer.write(result.stdout);sys.stderr.buffer.write(result.stderr)
raise SystemExit(result.returncode)
