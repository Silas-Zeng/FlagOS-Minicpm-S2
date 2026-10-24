"""上传已审425接线；可选传入已完成gate绝对路径后启动一次原VERIFY1。"""
from pathlib import Path
import base64, hashlib, json, re, subprocess, sys
HERE=Path(__file__).resolve().parent
DEST='/workspace/experiments/minicpm-s2/scripts/kv-restore-worker-20261022/'
PINS={'prepare_restore_worker_source.py':'f29f23e7de55d4acbacc7ee87e364e1c9f3ab32b002a8808b1c44b9a3495937a',
      'launch_restore_worker_verify1.sh':'352bc6b2c8f377293c6822196d8714385d9b0d924326779d07903d1b23011d31',
      'base-source-sha256.json':'82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
      'biv150_kv_pitched_restore_worker.py':'9f178a70b48cf19e97d32f7b9bea26195f7e447b593be9784659916d36120475'}
payload={}
for name,pin in PINS.items():
    raw=(HERE/name).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==pin,name
    payload[name]=base64.b64encode(raw).decode()
gate=sys.argv[1] if len(sys.argv)==2 else None
assert len(sys.argv) in (1,2)
if gate: assert re.fullmatch(r'/workspace/experiments/minicpm-s2/framework/\d{8}T\d{6}Z-kv-pitched-restore-gate',gate)
script=f'''from pathlib import Path
import base64,hashlib,json,subprocess
dest=Path({DEST!r});assert not dest.is_symlink();dest.mkdir(exist_ok=True)
payload={payload!r}
pins={PINS!r}
for name,b64 in payload.items():
 raw=base64.b64decode(b64);assert hashlib.sha256(raw).hexdigest()==pins[name]
 p=dest/name;assert not p.is_symlink()
 if p.exists():assert p.read_bytes()==raw,'拒绝覆盖不同接线'
 else:
  with p.open('xb') as f:f.write(raw)
subprocess.run(['bash','-n',str(dest/'launch_restore_worker_verify1.sh')],check=True)
gate={gate!r}
if gate:subprocess.run(['bash',str(dest/'launch_restore_worker_verify1.sh'),gate],check=True)
else:print(json.dumps({{'uploaded':str(dest),'started':False}}))
'''
args=['ssh','-F','NUL','-i','C:/Users/Administrator/.ssh/id_ed25519_flagos_s2','-o','BatchMode=yes',
      '-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','-p','2224',
      'lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io','python3 -']
out=subprocess.run(args,input=script.encode(),capture_output=True,timeout=60)
sys.stdout.buffer.write(out.stdout);sys.stderr.buffer.write(out.stderr)
raise SystemExit(out.returncode)
