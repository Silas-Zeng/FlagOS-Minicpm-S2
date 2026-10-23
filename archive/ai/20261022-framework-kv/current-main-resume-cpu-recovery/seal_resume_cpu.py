#!/usr/bin/env python3
"""保留447 CPU诊断exit0/1及未覆盖原件；核源码/DB/清理，不计算性能。"""
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
RUN = None  # root取得实际run ID后可仅锁此项；当前仅接受严格UTC+固定后缀。
match=re.fullmatch(r'(\d{8}T\d{6}Z)-current-main-resume-cpu-context16k-long',name)
if not match or (RUN is not None and name!=RUN):raise ValueError('not this observer diagnostic run')
stamp=match.group(1)
datetime.datetime.strptime(stamp,'%Y%m%dT%H%M%SZ')
terminal_code=int((run/'exit-code').read_text().strip())
if terminal_code not in (0,1) or not (run/'finished-at.txt').is_file():raise RuntimeError('not terminal exit0/1')
purpose=json.loads((control/'purpose.json').read_text())
source=Path(purpose['source'])
if source!=ROOT/'code'/('current-main-resume-cpu-'+stamp) or source.is_symlink():raise RuntimeError('not isolated observer source')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):
    with path.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
expected=json.loads((control/'source-sha256.json').read_text())
failures=[name for name,value in expected.items() if sha(source/name)!=value or sha(control/'plugin-source'/name)!=value]
launcher=control/'launch_resume_cpu.py'
if sha(launcher)!='800a4fa8f2cde61d5c66fdd657dc32283fde891a9da0dfe25df2e48237faa8cb':raise RuntimeError('frozen observer owner changed')
import runpy
namespace=runpy.run_path(str(launcher))  # 仅stdlib/定义；绝不调用prepare_source/main/reference_ready。
for filename,pin in {
    'candidate-git-blobs.json':'340e2ce1254510864d2b8b8d90939a98622f70a28f10573f9a887eebface106e',
    'candidate-manifest.json':'0b17b3a18fc89a3968f409d9e340190a19ffd4e7aadec3f456293f91281f4ec4',
    'observer-manifest.json':'64e819251918ea03be2965d9ec86f6140aa0de47800f762191dfb97c18b93c21',
}.items():
    if sha(control/filename)!=pin:raise RuntimeError('frozen identity changed: '+filename)
expected_blobs=json.loads((control/'candidate-git-blobs.json').read_text())
observer=json.loads((control/'observer-manifest.json').read_text())
def oid(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def tree_oid(entries):
    root = {}
    for path, entry in entries.items():
        parts, node = path.split('/'), root
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = (entry['mode'], entry['sha'])
    def walk(node):
        raw = b''
        for name in sorted(node, key=lambda x: (x + '/' if isinstance(node[x], dict) else x).encode()):
            value = node[name]
            mode, digest = ('40000', walk(value)) if isinstance(value, dict) else value
            raw += mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(digest)
        return oid('tree', raw)
    return walk(root)


if (len(expected_blobs)!=446 or tree_oid(expected_blobs)!=namespace['TREE']
        or observer['base_tree']!=namespace['TREE'] or observer['base_count']!=446
        or set(observer['changed_paths'])!=set(namespace['OBSERVER_PINS'])):
    raise RuntimeError('not fixed446 plus two declared observer paths')
for path,entry in observer['changed_paths'].items():
    if expected_blobs.get(path)!=entry['before'] or entry['sha256']!=namespace['OBSERVER_PINS'][path]:
        raise RuntimeError('observer base blob or payload mismatch')
    expected_blobs[path]=entry['after']
    if expected.get(path)!=entry['sha256']:raise RuntimeError('observer content SHA mismatch')
if (len(expected_blobs)!=447 or tree_oid(expected_blobs)!='cd50086ea3dd618c890533bc37e6637888b6dbf5'
        or observer['target_tree']!=namespace['OBSERVER_TREE'] or observer['source_count']!=447
        or purpose['source_count']!=447 or purpose['tree']!=observer['target_tree']
        or purpose['base_tree']!=namespace['TREE'] or purpose['base_commit']!=namespace['COMMIT']):
    raise RuntimeError('447 complete tree or purpose mismatch')
archived_blobs=json.loads((control/'source-git-blobs.json').read_text())
if len(expected)!=447 or archived_blobs!=expected_blobs:
    raise RuntimeError('not complete observer Git tree')
if namespace['source_maps'](source)!=(expected_blobs,expected) or namespace['source_maps'](control/'plugin-source')!=(expected_blobs,expected):
    raise RuntimeError('live/archive complete Git blobs, modes or symlink changed')
ports={}
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2);ports[host]=sock.connect_ex((host,9031))!=0
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
pids={int((control/'runner.pid').read_text()),int((run/'server.pid').read_text())}
log=(run/'server.log').read_text(errors='replace')
pids.update(int(pid) for pid in re.findall(r'EngineCore[^\s()]* pid=(\d+)',log))
processes={}
for pid in sorted(pids):
    p=Path('/proc')/str(pid)/'status';processes[str(pid)]=p.read_text() if p.exists() else None
owner_pid=int((control/'runner.pid').read_text())
# 原800a Popen(start_new_session=True)，bc51的负载客户端继承该组；只检查，不发信号。
group_members=[];group_errors=[];owner_stat=None
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():continue
    try:
        raw=(proc/'stat').read_text()
        tail=raw[raw.rindex(')')+2:].split()
        pid=int(proc.name);pgrp=int(tail[2]);session=int(tail[3])
        item=dict(pid=pid,state=tail[0],ppid=int(tail[1]),pgrp=pgrp,session=session,start_ticks=int(tail[19]),stat=raw)
        if pid==owner_pid:owner_stat=item
        if pgrp==owner_pid or session==owner_pid:group_members.append(item)
    except (FileNotFoundError,ProcessLookupError):
        continue
    except (OSError,ValueError,IndexError) as error:
        group_errors.append(dict(pid=proc.name,error_type=type(error).__name__))
group=dict(owner_pid=owner_pid,expected_pgid=owner_pid,expected_session=owner_pid,
    basis='原800a start_new_session=True；原bc51客户端继承组，仅事后读取/proc',
    owner_stat=owner_stat,members=group_members,scan_errors=group_errors,
    no_signals_sent=True,limits='这是采样时的组成员检查，非全程进程追踪。')
save(run/'owner-process-group.json',group)
post={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ports_closed':ports,'query':query,'ixsmi':table,'owned_process_status':processes,'source_count':len(expected),'source_failures':failures}
save(run/'postflight-full.json',post)
if failures or not all(ports.values()) or query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('postflight failed')
if not all(value is None or '\nState:\tZ ' in value for value in processes.values()):raise RuntimeError('owned process alive')
if (group_errors or any(member['state']!='Z' for member in group_members)
        or (owner_stat is not None and (owner_stat['pgrp']!=owner_pid or owner_stat['session']!=owner_pid))):
    raise RuntimeError('owner进程组/SID仍有活跃成员或检查不完整；只记录，不杀进程')
attention=Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py')
target=run/'postflight-sources';target.mkdir();shutil.copyfile(attention,target/attention.name)
save(target/'manifest.json',{'path':str(attention),'sha256':sha(attention)})
if sha(attention)!='54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f':raise RuntimeError('Attention changed')
subprocess.run(['python3',str(ROOT/'scripts/snapshot_tuning_db.py'),'--database','/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db','--output',str(control/'db-after')],check=True)
markers=['BIV150_SQL_REFLECTION_INSTALLED','BIV150_ASYNC_TOKEN_UPDATE_FIRST_SELECTED','BIV150_CPU_METADATA_FIRST_SELECTED','BIV150_PREFILL_NORMALIZATION_INSTALL','BIV150_PREFILL_NORMALIZATION_SELECTED','BIV150_COMPUTE_ORDER_FIRST_SELECTED','BIV150_COMPUTE_ORDER_SCOPE_REJECTED']
save(run/'selected-marker-review.json',{'markers':{marker:[line for line in log.splitlines() if marker in line] for marker in markers},'first_selected_is_full_count':False})
events=[];malformed=[]
known={'ARMED','PREEMPT_BEFORE','RESUME_FIRST_ATTEMPT','RESUME_ADMITTED','TARGET_EXECUTE','FINAL','OBSERVATION_DISABLED','SCOPE_REJECTED'}
for line_number,line in enumerate(log.splitlines(),1):
    if 'BIV150_RESUME_CPU ' not in line:continue
    try:
        item=json.loads(line.split('BIV150_RESUME_CPU ',1)[1])
        pid=re.search(r'EngineCore[^\s()]* pid=(\d+)',line)
        if (not isinstance(item,dict) or not pid or item.get('pid')!=int(pid.group(1))
                or item.get('event') not in known):raise ValueError('unknown event/PID')
        events.append(dict(line_number=line_number,value=item))
    except Exception as error:
        malformed.append(dict(line_number=line_number,error_type=type(error).__name__,line=line))
counts={kind:sum(row['value']['event']==kind for row in events) for kind in sorted(known)}
save(run/'resume-cpu-events.json',dict(run_id=name,exit_code=terminal_code,events=events,counts=counts,
    malformed=malformed,final_cpu_recording_complete=[row['value'].get('cpu_recording_complete')
        for row in events if row['value']['event']=='FINAL'],
    final_present=bool(counts['FINAL']),causal_chain_reviewed=False,gain=None,
    limits=['保留FINAL/抢占/APC/execute原字段；缺覆盖、观察失败或exit1不阻封包。',
        '仅CPU提交/原方法返回，GPU完成下界未知；未计算重算GPU时间或性能收益。',
        'FINAL缺失不推定成功，后续按同PID/RID/epoch分析；不自动补跑。']))
tool=control/'seal_resume_cpu.py'
if tool.exists():
    if tool.read_bytes()!=Path(__file__).read_bytes():raise RuntimeError('existing sealer differs')
else:shutil.copyfile(__file__,tool)
save(control/'seal-command.json',{'argv':sys.argv,'sealer_sha256':sha(tool),'quality_retested':False})
seal=control/'evidence-seal.json'
archive=run.with_name(run.name+'.tgz')
if seal.exists() or archive.exists():raise FileExistsError('refuse to overwrite evidence seal/archive')
files={path.relative_to(ROOT/'framework').as_posix():sha(path)
       for folder in (run,control) for path in folder.rglob('*') if path.is_file()}
save(seal,{'utc':post['utc'],'exit_code':terminal_code,'files':files,
    'limits':['CPU observer diagnostic including exit1/uncovered; no accuracy or performance gain',
              'symlink bytes in seal follow target; source-git-blobs retains original link text/mode']})
import tarfile
with tarfile.open(archive,'x:gz') as bundle:
    for folder in (run,control):bundle.add(folder,arcname=folder.name)
print(json.dumps({'status':'sealed','run':str(run),'source_count':len(expected),'gpu':query,
    'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'sealed_files':len(files)},indent=2))
