#!/usr/bin/env bash
# 暂态保留修正版真实抢占协议诊断；原服务及已知会抢占的短负载，不作为性能成绩。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-kv-retain-context16k-long"
control="$run-control"
source_dir="$root/code/kv-retain-$stamp"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$source_dir" "$control" <<'PY'
from pathlib import Path
import sys,hashlib,json,shutil,socket,subprocess
root,source,control=map(Path,sys.argv[1:])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected={
 'prepare_kv_protocol_source.py':'ac18b84dfc2e9435c6984f05ddc084d24458d2b158003df29ec9fedc641b6429',
 'run_framework_screen.py':'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
 'snapshot_tuning_db.py':'0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}
for name,value in expected.items():
    if sha(root/'scripts'/name)!=value:raise RuntimeError('unreviewed/changed asset: '+name)
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('device occupied')
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host,9031))==0:raise RuntimeError('port occupied')
base=root/'code/sql-mixed-20261021T080656Z'
builder=root/'scripts/prepare_kv_protocol_source.py'
subprocess.run(['python3',str(builder),'--base-source',str(base),'--output',str(source),'--asset-dir',str(root/'scripts')],check=True)
for name in [*expected,'prepare_innovation_source.py']:
    shutil.copyfile(root/'scripts'/name,control/name)
shutil.copytree(source,control/'plugin-source')
(control/'source-sha256.json').write_text(json.dumps({str(p.relative_to(source)):sha(p) for p in sorted(source.rglob('*')) if p.is_file()},indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'single victim KV protocol actual preemption diagnostic; not performance or accuracy','variant':'single-victim-kv-retain-transient','preceding_protocol_run':'20261021T200957Z-kv-protocol-context16k-long','source':str(source),'base':str(base),'preflight_gpu':query,'ixsmi':table,'preceding_layout_run':'20261021T195012Z-kv-runtime-descriptor-smoke','preceding_page_copy_gate':'20261021T191545Z-kv-page-copy-gate','restore_byte_readback_enabled':True,'required_evidence':['successful SAVE and source free','ZERO then RESTORE completed ACK','restore whole-byte readback passed','RUNNER_RESUME_STATE_CHECKED','RESUME_OUTPUT_PROCESSED'],'all_events_must_match_transaction':True},indent=2)+'\n')
PY
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
export BIV150_KV_VERIFY_RESTORE=1
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --context-long-screen --seed 721201 --require-log-marker BIV150_KV_PROTOCOL_INSTALLED)
printf 'BIV150_KV_VERIFY_RESTORE=1 ' > "$control/command.txt"
printf '%q ' "${command[@]}" >> "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
