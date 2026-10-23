from pathlib import Path
import base64,hashlib,json,subprocess,sys
here=Path(__file__).resolve().parent
pins={
 'launch_candidate.sh':'72f82a7c12b48e9ef4bb0b851b7c7d36121fd8bba42c19073c0500934036bdd7',
 'prepare_source.py':'a8264488f522c88da237eeee7d9f9c216b6a50b73374921e411db2495e62e7d9',
 'base-source-sha256.json':'82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
 'expected-source-sha256.json':'beb748fc30842d2ba378bcb0e526dfff0ba6e02f9ec4acf8986d8f2e7421ac5d',
 'biv150_noop_allocate.py':'7393aa23cbef2c795faed23e32504a028ad1a867226089c45ad5c43026a9f3e9',
 'init-footer.py':'14a55c38704415d1a5bb99074e605ddf78b854bf41540f6fc397ec37b2354f6d',
 'cpu-tested-core.py':'fc410a4a02f93694402480a91a4a027ce16e5c6beaf90efc59d141cf0c5de2b3',
 'cpu-check.json':'e876f792614c0cbbd7e1a2222fddf233cbe6adc8dd3ac94355be6e2e010be23b'}
payload={}
for name,pin in pins.items():
 raw=(here/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin,name
 payload[name]=base64.b64encode(raw).decode()
script=f'''from pathlib import Path
import base64,hashlib,subprocess
dest=Path('/workspace/experiments/minicpm-s2/scripts/allocator-noop-20261022')
assert not dest.exists();dest.mkdir()
payload={payload!r};pins={pins!r}
for name,b64 in payload.items():
 raw=base64.b64decode(b64);assert hashlib.sha256(raw).hexdigest()==pins[name]
 with (dest/name).open('xb') as f:f.write(raw)
launcher=str(dest/'launch_candidate.sh')
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
