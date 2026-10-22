from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
base=Path('/usr/local/corex/include')
names=['IX/mapping_cudart.h','IX/ixrt/ix_runtime_api.h']
needles=['cudaMemcpy2DAsync','ixMemcpy2DAsync','cudaMemcpyDeviceToHost','cudaMemcpyHostToDevice']
result=[]
for name in names:
 p=base/name
 raw=p.read_bytes();lines=raw.decode('utf-8',errors='replace').splitlines()
 hits=[]
 for i,line in enumerate(lines):
  if any(n in line for n in needles):
   hits.append({'line':i+1,'context_start_line':max(0,i-3)+1,'context':lines[max(0,i-3):i+10]})
 result.append({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'hits':hits})
rid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-memcpy2d-header-contract'
out=Path('/workspace/experiments/minicpm-s2/source-audits')/rid
out.mkdir(exist_ok=False)
doc={'run_id':rid,'kind':'CPU-only targeted header read; no API or device calls','headers':result}
p=out/'result.json';p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'directory':str(out),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'headers':result},ensure_ascii=False))
