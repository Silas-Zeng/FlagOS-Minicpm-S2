#!/usr/bin/env bash
# 一次最短真实布局观察；原服务参数，不作性能测量。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-kv-runtime-descriptor-smoke"
control="$run-control"
source_dir="$root/code/kv-runtime-descriptor-$stamp"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$control" <<'PY'
from pathlib import Path
import sys,hashlib,json,socket,subprocess
root,control=map(Path,sys.argv[1:])
expected={
 'biv150_kv_runtime_descriptor.py':'0c892ad02fbfe663d3f7c8f668cdd000c0c1fc7860ff915db8bce5949cae0667',
 'prepare_kv_runtime_descriptor_source.py':'936c9260724f97b02dc1e69da2f4f0da7cdfaf7fdcb0e8ab866c26d9c028c59e',
 'prepare_innovation_source.py':'0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca',
 'run_framework_screen.py':'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
 'snapshot_tuning_db.py':'0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}
for name,value in expected.items():
    if hashlib.sha256((root/'scripts'/name).read_bytes()).hexdigest()!=value:raise RuntimeError('asset changed: '+name)
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('device occupied')
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host,9031))==0:raise RuntimeError('port occupied: '+host)
(control/'preflight.json').write_text(json.dumps({'gpu':query,'ixsmi':table,'assets':expected},indent=2)+'\n')
PY
python3 "$root/scripts/prepare_kv_runtime_descriptor_source.py" --base-source "$root/code/sql-mixed-20261021T080656Z" --output "$source_dir" --asset-dir "$root/scripts" > "$control/prepare.log"
python3 - "$root" "$source_dir" "$control" <<'PY'
from pathlib import Path
import sys,hashlib,json,shutil
root,source,control=map(Path,sys.argv[1:])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copytree(source,control/'plugin-source')
(control/'source-sha256.json').write_text(json.dumps({str(p.relative_to(source)):sha(p) for p in sorted(source.rglob('*')) if p.is_file()},indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'actual KV/executor CPU descriptor observation; not performance or accuracy','source':str(source),'base':str(root/'code/sql-mixed-20261021T080656Z'),'required_post_events':['worker-kv:observed_complete:42','core-objects:first_engine_step_after_constructor'],'scheduling_changed':False},indent=2)+'\n')
for name in ['biv150_kv_runtime_descriptor.py','prepare_kv_runtime_descriptor_source.py','prepare_innovation_source.py','snapshot_tuning_db.py']:
    shutil.copyfile(root/'scripts'/name,control/name)
PY
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
export BIV150_KV_DESCRIPTOR_DIR="$run/kv-descriptors"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --smoke-only --seed 721201 --require-log-marker BIV150_KV_RUNTIME_DESCRIPTOR_INSTALLED)
printf 'BIV150_KV_DESCRIPTOR_DIR=%q ' "$BIV150_KV_DESCRIPTOR_DIR" > "$control/command.txt"
printf '%q ' "${command[@]}" >> "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
