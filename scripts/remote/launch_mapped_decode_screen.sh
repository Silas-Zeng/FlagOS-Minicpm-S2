#!/usr/bin/env bash
# 已通过四形状正确性门的 mapped Attention 隔离短服务。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-mapped-decode-context16k"
control="$run-control"
source_dir="$root/code/mapped-decode-$stamp"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$source_dir" "$control" <<'PY'
from pathlib import Path
import sys,hashlib,json,shutil,socket,subprocess
root,source,control=map(Path,sys.argv[1:])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('device occupied')
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host,9031))==0:raise RuntimeError('port occupied')
if sha(root/'scripts/run_framework_screen.py')!='bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9':raise RuntimeError('driver changed')
builder=root/'scripts/prepare_mapped_decode_source.py'
if sha(builder)!='a41c3858ac5d19ffbb385d9ad075635b560fb272af2c2d6b5c490f04713d2459':raise RuntimeError('builder changed')
base=root/'code/sql-mixed-20261021T080656Z'
subprocess.run(['python3',str(builder),'--base-source',str(base),'--output',str(source),'--asset-dir',str(root/'scripts')],check=True)
shutil.copyfile(builder,control/builder.name)
shutil.copytree(source,control/'plugin-source')
(control/'source-sha256.json').write_text(json.dumps({str(p.relative_to(source)):sha(p) for p in sorted(source.rglob('*')) if p.is_file()},indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'mapped mixed Attention short service; not official','variant':'mapped-decode','source':str(source),'base':str(base),'preflight_gpu':query,'ixsmi':table,'preceding_correctness_run':'20261021T184809Z-mapped-decode-sme-fix-gate','preceding_layer_timing_run':'20261021T185023Z-mapped-decode-sme-fix-timing','require_real_execute_marker':True},indent=2)+'\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --context-screen --seed 721201 --require-log-marker BIV150_MAPPED_DECODE_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
