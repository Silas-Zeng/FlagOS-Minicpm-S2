"""仅启动指定一侧；上传固定接线与实际通过的VERIFY1报告，不自动串行pair。"""
from pathlib import Path
import base64,hashlib,json,re,subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DEST='/workspace/experiments/minicpm-s2/scripts/kv-restore-worker-verify0-20261022/'
PINS={'launch_restore_worker_verify0.sh':'5c1542d3ed7fdd3a4336294bd891d57b50feaa13b05c7d2b597a397c58971699',
      'base-source-sha256.json':'82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
      'restore-source-sha256.json':'fb8b867222b7b1c867e457c4c3f7f72cb6e4dce42ad528f28aa211c8cf7734ed'}
payload={}
for name,pin in PINS.items():
    raw=(HERE/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin,name
    payload[name]=base64.b64encode(raw).decode()
raw=(ROOT/'analysis/q-gqa-kv-restore-pitched-verify1.json').read_bytes()
report=json.loads(raw)
assert report['status']=='passed_qgqa_pitched_full_restore_verify1_compatibility'
assert report['source_manifest_sha256']==PINS['restore-source-sha256.json']
PINS['passed-verify1.json']=hashlib.sha256(raw).hexdigest();payload['passed-verify1.json']=base64.b64encode(raw).decode()
variant=sys.argv[1];extra=sys.argv[2:]
assert variant in ('baseline','candidate')
assert (variant=='baseline' and not extra) or (variant=='candidate' and len(extra)==1)
if extra:assert re.fullmatch(r'/workspace/experiments/minicpm-s2/framework/\d{8}T\d{6}Z-q-gqa-kv-restore-pitched-verify0-baseline-context16k-long-control',extra[0])
script=f'''from pathlib import Path
import base64,hashlib,subprocess
dest=Path({DEST!r});assert not dest.is_symlink();dest.mkdir(exist_ok=True)
payload={payload!r};pins={PINS!r}
for name,b64 in payload.items():
 raw=base64.b64decode(b64);assert hashlib.sha256(raw).hexdigest()==pins[name]
 p=dest/name;assert not p.is_symlink()
 if p.exists():assert p.read_bytes()==raw,'拒绝覆盖不同接线'
 else:
  with p.open('xb') as f:f.write(raw)
launcher=str(dest/'launch_restore_worker_verify0.sh')
subprocess.run(['bash','-n',launcher],check=True)
subprocess.run(['bash',launcher,{variant!r},str(dest/'passed-verify1.json'),*{extra!r}],check=True)
'''
args=['ssh','-F','NUL','-i','C:/Users/Administrator/.ssh/id_ed25519_flagos_s2','-o','BatchMode=yes',
      '-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','-p','2224',
      'lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io','python3 -']
out=subprocess.run(args,input=script.encode(),capture_output=True,timeout=60)
sys.stdout.buffer.write(out.stdout);sys.stderr.buffer.write(out.stderr)
raise SystemExit(out.returncode)
