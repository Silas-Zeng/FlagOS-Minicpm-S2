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
if name != '20261023T130351Z-compute-order-math4-event':raise RuntimeError('not this fixed math4 event run')
exit_code=(run/'exit-code').read_text().strip()
if exit_code not in ('0','1') or not (run/'finished-at.txt').is_file():raise RuntimeError('not terminal exit0/1')
summary_path=run/'context-16k/math4-event-load-summary.json'
summary=json.loads(summary_path.read_text(encoding='utf-8')) if summary_path.is_file() else None
if summary is not None and (type(summary) is not dict or summary.get('exit_code') != int(exit_code)):
    raise RuntimeError('owner/load exit status mismatch')
if exit_code == '0' and (summary is None or summary.get('status') != 'processes_completed_requires_report_review'):
    raise RuntimeError('exit0 lacks completed original load summary')
client_jobs=summary.get('jobs',{}) if summary is not None else {}
if type(client_jobs) is not dict or not set(client_jobs) <= {'math4','background'}:
    raise RuntimeError('invalid client jobs manifest')
if exit_code == '0' and (set(client_jobs) != {'math4','background'} or summary.get('cleanup_errors')
        or any(job.get('returncode') != 0 for job in client_jobs.values())):
    raise RuntimeError('exit0 client outcome/cleanup inconsistent')
client_pids=[]
for label,job in client_jobs.items():
    pid=job.get('pid')
    if type(pid) is not int or pid <= 0:raise RuntimeError('invalid owned client PID')
    client_pids.append(pid)
if len(set(client_pids)) != len(client_pids):raise RuntimeError('duplicate owned client PID')
load_outcome={'summary_path':str(summary_path),'summary_present':summary is not None,
    'status':summary.get('status') if summary is not None else None,
    'exit_code':int(exit_code),'jobs':client_jobs,
    'cleanup_errors':summary.get('cleanup_errors') if summary is not None else None,
    'summary_missing_reason':None if summary is not None else 'summary_not_created; cause not inferred; preserve owner/client logs',
    'client_cleanup_proof':'known_jobs_pid_and_pgid' if client_jobs else 'unavailable_no_jobs_manifest',
    'quality_pass_claimed':False}
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
pids.update(client_pids)
client_groups={str(pid):[] for pid in client_pids}
group_scan_errors=[]
for entry in Path('/proc').iterdir():
    if not entry.name.isdecimal():continue
    try:
        # comm may contain spaces or ')'; fields after the final ')' start with state.
        fields=(entry/'stat').read_text().rsplit(')',1)[1].split()
        pgid=int(fields[2])
        if str(pgid) in client_groups:
            client_groups[str(pgid)].append({'pid':int(entry.name),'state':fields[0],'ppid':int(fields[1]),'pgid':pgid})
    except (FileNotFoundError,ProcessLookupError):
        pass
    except (OSError,ValueError,IndexError) as error:
        group_scan_errors.append({'pid':entry.name,'error':repr(error)})
processes={}
for pid in sorted(pids):
    p=Path('/proc')/str(pid)/'status';processes[str(pid)]=p.read_text() if p.exists() else None
post={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ports_closed':ports,'query':query,'ixsmi':table,'owned_process_status':processes,'source_count':len(expected),'source_failures':failures,'load_outcome':load_outcome,'client_group_members':client_groups,'client_group_scan_errors':group_scan_errors}
save(run/'postflight-full.json',post)
if failures or not all(ports.values()) or query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('postflight failed')
if not all(value is None or '\nState:\tZ ' in value for value in processes.values()):raise RuntimeError('owned process alive')
if group_scan_errors or any(member['state'] != 'Z' for members in client_groups.values() for member in members):
    raise RuntimeError('owned client process group alive or unreadable process status')
attention=Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py')
target=run/'postflight-sources';target.mkdir();shutil.copyfile(attention,target/attention.name)
save(target/'manifest.json',{'path':str(attention),'sha256':sha(attention)})
if sha(attention)!='54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f':raise RuntimeError('Attention changed')
subprocess.run(['python3',str(ROOT/'scripts/snapshot_tuning_db.py'),'--database','/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db','--output',str(control/'db-after')],check=True)
markers=['BIV150_SQL_REFLECTION_INSTALLED','BIV150_ASYNC_TOKEN_UPDATE_FIRST_SELECTED','BIV150_CPU_METADATA_FIRST_SELECTED']
save(run/'selected-marker-review.json',{'markers':{marker:[line for line in log.splitlines() if marker in line] for marker in markers},'first_selected_is_full_count':False})
print(json.dumps({'status':'evidence_sealed_not_quality_pass','run':str(run),'exit_code':int(exit_code),'load_status':load_outcome['status'],'source_count':len(expected),'gpu':query},indent=2))
