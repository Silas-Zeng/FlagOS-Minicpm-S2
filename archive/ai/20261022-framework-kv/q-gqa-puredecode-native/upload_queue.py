"""上传已冻结CPU资产并启动一次等待队列；当前GPU仍由官方owner持有。"""
from pathlib import Path
import ast
import base64
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
QUEUE_SHA = '4f020e5bfa618e481b82ff6079054f51643ce212bff6d59ed61e78d36e34123b'
STAMP = '20261022T235007Z'
raw_queue = (HERE / 'queue_after_official.py').read_bytes()
assert hashlib.sha256(raw_queue).hexdigest() == QUEUE_SHA
tree = ast.parse(raw_queue)
pins = next(ast.literal_eval(node.value) for node in tree.body
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == 'PINS')
pins['queue_after_official.py'] = QUEUE_SHA
payload = {}
for name, pin in pins.items():
    raw = (HERE / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == pin, name
    payload[name] = base64.b64encode(raw).decode()
script = f'''from pathlib import Path
import base64,hashlib,json,subprocess
root=Path('/workspace/experiments/minicpm-s2')
assets=root/'scripts/q-gqa-puredecode-native-{STAMP}'
queue=root/'queues/{STAMP}-after-official'
assert not assets.exists() and not queue.exists()
assets.mkdir();queue.mkdir(parents=True)
payload={payload!r};pins={pins!r}
for name,encoded in payload.items():
    raw=base64.b64decode(encoded)
    assert hashlib.sha256(raw).hexdigest()==pins[name]
    with (assets/name).open('xb') as f: f.write(raw)
compile((assets/'queue_after_official.py').read_bytes(),str(assets/'queue_after_official.py'),'exec')
with (queue/'queue.log').open('xb') as log:
    proc=subprocess.Popen(['python3',str(assets/'queue_after_official.py'),str(queue)],
        stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
with (queue/'queue.pid').open('x') as f: f.write(str(proc.pid)+'\\n')
print(json.dumps({{'assets':str(assets),'queue':str(queue),'queue_pid':proc.pid,'queue_sha256':pins['queue_after_official.py'],'gpu_started_by_uploader':False}}))
'''
ssh = ['ssh', '-F', 'NUL', '-i', 'C:/Users/Administrator/.ssh/id_ed25519_flagos_s2',
       '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'ConnectTimeout=12', '-p', '2224',
       'lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io', 'python3 -']
result = subprocess.run(ssh, input=script.encode(), capture_output=True, timeout=60)
with (HERE / 'queue-upload-result.json').open('x', encoding='utf-8') as f:
    json.dump({'exit_code': result.returncode, 'stdout': result.stdout.decode(),
               'stderr': result.stderr.decode()}, f, indent=2)
sys.stdout.buffer.write(result.stdout)
sys.stderr.buffer.write(result.stderr)
raise SystemExit(result.returncode)
