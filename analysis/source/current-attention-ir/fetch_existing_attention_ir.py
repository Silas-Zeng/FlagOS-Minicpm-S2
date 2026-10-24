"""只读回收已完成门的既有编译缓存；不导入设备框架、不编译或运行 kernel。"""
from pathlib import Path
import base64
import hashlib
import json
import subprocess

record = Path('experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate/results.json')
expected = {}
def walk(value):
    if isinstance(value, dict):
        if 'asm_sha256' in value:
            arm = 'baseline' if value.get('n_regs') == 102 else 'v_late'
            for kind in ('ttir', 'ttgir', 'llir', 'asm'):
                expected[value['asm_sha256'][kind]] = [arm, kind]
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)
walk(json.loads(record.read_text(encoding='utf-8')))
assert len(expected) == 8
remote = '''from pathlib import Path
import os,json,hashlib,base64,datetime
expected=EXPECTED
roots=[Path.home()/'.triton/cache', Path.home()/'.cache/triton']
if os.environ.get('TRITON_CACHE_DIR'): roots.append(Path(os.environ['TRITON_CACHE_DIR']))
seen=set(); found=[]; checked=0
for root in roots:
 if not root.is_dir(): continue
 for p in root.rglob('kernel_unified_attention.*'):
  if p in seen or not p.is_file() or p.suffix not in ('.ttir','.ttgir','.llir','.asm'): continue
  seen.add(p); raw=p.read_bytes(); checked+=1; sha=hashlib.sha256(raw).hexdigest()
  if sha in expected:
   found.append(dict(path=str(p),sha256=sha,bytes=len(raw),arm=expected[sha][0],kind=expected[sha][1],data=base64.b64encode(raw).decode()))
   expected.pop(sha)
print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cache_roots=[str(p) for p in roots if p.is_dir()],checked=checked,missing=expected,files=found)))
'''.replace('EXPECTED', repr(expected))
args = ['ssh','-F','NUL','-i','C:/Users/Administrator/.ssh/id_ed25519_flagos_s2',
        '-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12',
        '-p','2224','lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io','python3 -']
r = subprocess.run(args,input=remote.encode(),capture_output=True,check=True,timeout=50)
response = json.loads(r.stdout)
out = Path('analysis/source/current-attention-ir')
out.mkdir(exist_ok=False)
for item in response['files']:
    raw = base64.b64decode(item.pop('data'))
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    dest = out / (item['arm'] + '.' + item['kind'])
    dest.write_bytes(raw)
    item['local_path'] = str(dest)
response['evidence_source'] = str(record)
response['evidence_source_sha256'] = hashlib.sha256(record.read_bytes()).hexdigest()
response['operation'] = 'existing-cache-read-only; no import/compile/GPU launch'
(out/'retrieval.json').write_text(json.dumps(response,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(response,ensure_ascii=False))
