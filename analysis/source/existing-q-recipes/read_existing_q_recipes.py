"""只读回收现有 w8/s1 原路径 Q-load IR，避免为编译身份重复上卡。"""
import base64
import hashlib
import json
from pathlib import Path
import subprocess

remote = r'''
from pathlib import Path
import base64,hashlib,json,datetime
root=Path('/root/.triton/cache');files=[];count=0
for p in sorted(root.glob('*/kernel_unified_attention.json')):
 m=json.loads(p.read_text());count+=1
 if m.get('num_warps')!=8 or m.get('num_stages')!=1 or m.get('shared')!=65536 or m.get('ir_override'):continue
 ir=p.with_suffix('.ttgir')
 if not ir.is_file():continue
 raw=ir.read_bytes();s=raw.decode()
 if s.count('%Q_222 = ttg.local_load %Q_131')!=1:continue
 files.append(dict(path=str(ir),metadata=m,sha256=hashlib.sha256(raw).hexdigest(),data=base64.b64encode(raw).decode()))
print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checked=count,files=files)))
'''
args=['ssh','-F','NUL','-i','C:/Users/Administrator/.ssh/id_ed25519_flagos_s2','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','-p','2224','lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io','python3 -']
r=subprocess.run(args,input=remote.encode(),capture_output=True,check=True,timeout=45)
data=json.loads(r.stdout)
out=Path('analysis/source/existing-q-recipes');out.mkdir(exist_ok=False)
for item in data['files']:
 raw=base64.b64decode(item.pop('data'));assert hashlib.sha256(raw).hexdigest()==item['sha256']
 dest=out/(item['sha256']+'.ttgir')
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
 item['local_path']=dest.as_posix()
data['operation']='只读既有缓存；未导入GPU框架、编译、启动设备作业；缓存无run归属，不能直接认定是当前服务recipe。'
(out/'retrieval.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checked':data['checked'],'matches':len(data['files']),'unique':len({x['sha256'] for x in data['files']}),'out':str(out)},ensure_ascii=False))
