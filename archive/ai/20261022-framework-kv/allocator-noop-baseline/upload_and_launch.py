from pathlib import Path
import base64, hashlib, json, subprocess, sys
here=Path(__file__).resolve().parent
pins={'launch.sh':'f480ab0d1c8f4c582b967804c437536621eac91a1ddb54642204011192f63de8',
      'base-source-sha256.json':'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392',
      'expected-source-sha256.json':'82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'}
payload={}
for name,pin in pins.items():
    raw=(here/name).read_bytes(); assert hashlib.sha256(raw).hexdigest()==pin
    payload[name]=base64.b64encode(raw).decode()
script=f'''from pathlib import Path
import base64,hashlib,subprocess
dest=Path('/workspace/experiments/minicpm-s2/scripts/allocator-noop-baseline-20261022')
assert not dest.exists();dest.mkdir()
payload={payload!r};pins={pins!r}
for name,b64 in payload.items():
 raw=base64.b64decode(b64);assert hashlib.sha256(raw).hexdigest()==pins[name]
 with (dest/name).open('xb') as f:f.write(raw)
launcher=str(dest/'launch.sh')
subprocess.run(['bash','-n',launcher],check=True)
subprocess.run(['bash',launcher],check=True)
'''
args=['ssh','-F','NUL','-i','C:/Users/Administrator/.ssh/id_ed25519_flagos_s2','-o','BatchMode=yes',
      '-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','-p','2224',
      'lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io','python3 -']
result=subprocess.run(args,input=script.encode(),capture_output=True,timeout=60)
sys.stdout.buffer.write(result.stdout);sys.stderr.buffer.write(result.stderr)
(here/'launch-result.json').write_text(json.dumps({'exit':result.returncode,'stdout':result.stdout.decode(),'stderr':result.stderr.decode()},indent=2)+'\n',encoding='utf-8')
raise SystemExit(result.returncode)
