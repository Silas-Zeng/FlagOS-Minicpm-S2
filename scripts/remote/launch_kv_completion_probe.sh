#!/usr/bin/env bash
# 保持原调度，只观察已知会压满 KV 的短负载；不可作为性能基线。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-kv-completion-context16k-long"
control="$run-control"
source_dir="$root/code/kv-completion-probe-$stamp"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$source_dir" "$control" <<'PY'
from pathlib import Path
import sys,hashlib,json,shutil,runpy,socket,subprocess
root,source,control=map(Path,sys.argv[1:])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('device occupied')
with socket.socket() as sock:
    sock.settimeout(2)
    if sock.connect_ex(('127.0.0.1',9031))==0:raise RuntimeError('port occupied')
module=root/'scripts/biv150_kv_completion_probe.py'
if sha(module)!='a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6':raise RuntimeError('probe changed')
if sha(root/'scripts/run_framework_screen.py')!='bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9':raise RuntimeError('driver changed')
base=root/'code/sql-mixed-20261021T080656Z'
shutil.copytree(base,source,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
if sha(source/'vllm_fl/worker/model_runner.py')!='e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1':raise RuntimeError('runner changed')
init=source/'vllm_fl/__init__.py'
init.write_bytes(runpy.run_path(str(module))['transform_init'](init.read_bytes()))
if sha(init)!='b3b7e2e8d9064c47ac09422741f18c9a3f7079946bc3306a9ccae393d554ca7c':raise RuntimeError('init differs')
shutil.copyfile(module,source/'vllm_fl/patches/biv150_kv_completion_probe.py')
shutil.copytree(source,control/'plugin-source')
(control/'source-sha256.json').write_text(json.dumps({str(p.relative_to(source)):sha(p) for p in sorted(source.rglob('*')) if p.is_file()},indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'KV failure and terminal-output capacity diagnostic; not performance','source':str(source),'base':str(base),'preflight_gpu':query,'ixsmi':table,'future_readiness_evaluated':False,'scheduling_changed':False},indent=2)+'\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --context-long-screen --seed 721201 --require-log-marker BIV150_KV_COMPLETION_PROBE_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
