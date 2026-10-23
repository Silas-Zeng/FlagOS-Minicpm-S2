#!/usr/bin/env bash
# 每次只启动一侧原bc51 smoke；原driver独占锁、PID和清理，不是性能pair。
set -euo pipefail
test "$#" -eq 1
variant=$1
case "$variant" in baseline|finite) ;; *) exit 2 ;; esac
root=/workspace/experiments/minicpm-s2
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-current-kv-memory-$variant-smoke"
control="$run-control"
source_dir="$root/code/current-kv-memory-$variant-$stamp"
python3 - "$root" "$assets" <<'PY'
from pathlib import Path
import hashlib, socket, subprocess, sys
root,assets=map(Path,sys.argv[1:])
expected={
    'prepare_current_kv_memory.py':'e3b93fe293a054db0704e4c2dc5f4e0dc6bd0ae08be844eedea2709c1f826bb7',
    'biv150_kv_memory_observer.py':'9d43de58bfe587e3f80cbc8aeed2174f03755172858817fb7c90769374aef119',
    'baseline-source-sha256.json':'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392',
    'finite-source-sha256.json':'7ad1f1acd9188b617a879f7e5de97c883fddf5ccc7981cbb27e0e474f92043c7',
}
for name,pin in expected.items():
    if hashlib.sha256((assets/name).read_bytes()).hexdigest()!=pin:
        raise RuntimeError('未冻结资产变化: '+name)
for name,pin in {
    'run_framework_screen.py':'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
    'snapshot_tuning_db.py':'0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}.items():
    if hashlib.sha256((root/'scripts'/name).read_bytes()).hexdigest()!=pin:
        raise RuntimeError('原owner/helper变化: '+name)
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:
    raise RuntimeError('设备不空闲: '+query)
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host,9031))==0: raise RuntimeError('9031正在使用: '+host)
PY
mkdir "$control"
cp "$0" "$control/launch.sh"
cp "$assets/prepare_current_kv_memory.py" "$assets/biv150_kv_memory_observer.py" "$assets/baseline-source-sha256.json" "$assets/finite-source-sha256.json" "$control/"
python3 "$control/prepare_current_kv_memory.py" --variant "$variant" --output-dir "$source_dir" > "$control/preparation.log"
cp "$source_dir-preparation.json" "$control/preparation.json"
python3 - "$control" <<'PY'
from pathlib import Path
import json, shutil, sys
control=Path(sys.argv[1])
receipt=json.loads((control/'preparation.json').read_text(encoding='utf-8'))
shutil.copytree(receipt['source'],control/'plugin-source')
for name,value in (('purpose.json',receipt),('source-sha256.json',receipt['source_sha256'])):
    with (control/name).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
mkdir "$control/q-hoist-artifacts"
nohup python3 - "$root" "$run" "$control" "$source_dir" "$variant" > "$control/runner.log" 2>&1 <<'PY' &
from pathlib import Path
import json, os, re, shlex, subprocess, sys
root,run,control,source=map(Path,sys.argv[1:5]);variant=sys.argv[5]
env=os.environ.copy()
env.pop('BIV150_FINITE_GROWTH_ADMISSION',None)
selected={'BIV150_KV_VERIFY_RESTORE':'0',
    'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR':str(control/'q-hoist-artifacts')}
if variant=='finite': selected['BIV150_FINITE_GROWTH_ADMISSION']='1'
env.update(selected)
command=['python3',str(root/'scripts/run_framework_screen.py'),str(run),
    '--source-dir',str(source),'--smoke-only','--seed','721201',
    '--require-log-marker','"event": "DETERMINE_RETURN"']
with (control/'command.json').open('x',encoding='utf-8') as f:
    json.dump({'argv':command,'environment_overrides':selected,
        'environment_unset':['BIV150_FINITE_GROWTH_ADMISSION'] if variant=='baseline' else [],
        'kind':'startup smoke only; original bc51 owns device lock and cleanup'},f,indent=2);f.write('\n')
with (control/'command.txt').open('x',encoding='utf-8') as f:
    prefix=['env','-u','BIV150_FINITE_GROWTH_ADMISSION',*[k+'='+v for k,v in selected.items()]]
    f.write(shlex.join(prefix+command)+'\n')
status=1
try:
    driver_rc=subprocess.run(command,env=env,cwd='/workspace').returncode
    (control/'driver-exit-code').write_text(str(driver_rc)+'\n',encoding='utf-8')
    log=(run/'server.log').read_text(encoding='utf-8',errors='replace')
    events=[]
    for line in log.splitlines():
        if 'BIV150_KV_MEMORY_OBSERVER ' not in line: continue
        prefix,payload=line.split('BIV150_KV_MEMORY_OBSERVER ',1)
        event=json.loads(payload)
        match=re.search(r'\(EngineCore(?:_[A-Za-z0-9]+)? pid=(\d+)\)',prefix)
        event['same_engine_log_pid']=match is not None and int(match.group(1))==event.get('pid')
        events.append(event)
    determines=[e for e in events if e.get('event')=='DETERMINE_RETURN']
    parents=[e for e in events if e.get('event')=='PARENT_RETURN']
    d=determines[0] if len(determines)==1 else {}
    p=parents[0] if len(parents)==1 else {}
    checks={'original_driver_exit0':driver_rc==0,
        'same_Engine_DETERMINE_RETURN':len(determines)==1 and d.get('same_engine_log_pid') is True,
        'original_profile_once':d.get('profile_context_calls')==1 and d.get('error_type') is None,
        'same_Engine_PARENT_RETURN':len(parents)==1 and p.get('same_engine_log_pid') is True
            and p.get('pid')==d.get('pid') and p.get('error_type') is None,
        'original_int_and_parent_list':type(d.get('returned')) is int
            and p.get('returned_type')=='list' and p.get('returned')==[d.get('returned')],
        'all_three_hooks_restored':all(p.get('restored',{}).get(k) is True
            for k in ('worker_method','profiling_context','parent_method')),
        'no_observation_rejection':not any(e.get('event') in
            ('REJECTED','NOT_ACTIVATED','OBSERVATION_INCOMPLETE','DETERMINE_RAISED','PARENT_RAISED') for e in events)}
    status=0 if all(checks.values()) else 2
    with (control/'observation-validation.json').open('x',encoding='utf-8') as f:
        json.dump({'status':'pass' if status==0 else 'fail','checks':checks,'events':events,
            'performance_pair':False,'limits':['不增加设备采样；不能证明分配来源或历史差的因果。',
            'Q/GQA真实执行由root从原smoke原件读取，不在本launcher另加门。']},f,ensure_ascii=False,indent=2);f.write('\n')
finally:
    # 只封存owner结果，绝不另做GPU清理/第二把锁或自动下一轮。
    with (control/'runner-exit-code').open('x',encoding='utf-8') as f:f.write(str(status)+'\n')
raise SystemExit(status)
PY
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
