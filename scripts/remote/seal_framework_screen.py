#!/usr/bin/env python3
"""保留短服务原件，补齐 DB 后态、实际源码及进程清理证据。"""
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys

ROOT=Path('/workspace/experiments/minicpm-s2')
name=sys.argv[1]
if not re.fullmatch(r'\d{8}T\d{6}Z-[a-z0-9-]+',name):raise ValueError('invalid run ID')
run=ROOT/'framework'/name;control=Path(str(run)+'-control')
if (run/'exit-code').read_text().strip()!='0':raise RuntimeError('screen did not pass')
purpose=json.loads((control/'purpose.json').read_text())
source=Path(purpose['source'])
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):
    with path.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
expected=json.loads((control/'source-sha256.json').read_text())
failures=[name for name,value in expected.items() if sha(source/name)!=value or sha(control/'plugin-source'/name)!=value]
ports={}
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2);ports[host]=sock.connect_ex((host,9031))!=0
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
pids={int((control/'runner.pid').read_text()),int((run/'server.pid').read_text())}
log=(run/'server.log').read_text(errors='replace')
pids.update(int(pid) for pid in re.findall(r'EngineCore pid=(\d+)',log))
processes={}
for pid in sorted(pids):
    p=Path('/proc')/str(pid)/'status';processes[str(pid)]=p.read_text() if p.exists() else None
post={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ports_closed':ports,'query':query,'ixsmi':table,'owned_process_status':processes,'source_count':len(expected),'source_failures':failures}
save(run/'postflight-full.json',post)
if failures or not all(ports.values()) or query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('postflight failed')
if not all(value is None or '\nState:\tZ ' in value for value in processes.values()):raise RuntimeError('owned process alive')
attention=Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py')
target=run/'postflight-sources';target.mkdir();shutil.copyfile(attention,target/attention.name)
save(target/'manifest.json',{'path':str(attention),'sha256':sha(attention)})
if sha(attention)!='54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f':raise RuntimeError('Attention changed')
subprocess.run(['python3',str(ROOT/'scripts/snapshot_tuning_db.py'),'--database','/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db','--output',str(control/'db-after')],check=True)
markers=['BIV150_SQL_REFLECTION_INSTALLED','BIV150_ASYNC_TOKEN_UPDATE_FIRST_SELECTED','BIV150_CPU_METADATA_FIRST_SELECTED']
save(run/'selected-marker-review.json',{'markers':{marker:[line for line in log.splitlines() if marker in line] for marker in markers},'first_selected_is_full_count':False})
print(json.dumps({'status':'sealed','run':str(run),'source_count':len(expected),'gpu':query},indent=2))
