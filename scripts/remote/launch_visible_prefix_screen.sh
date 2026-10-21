#!/usr/bin/env bash
# 同一 SQL+C3 基点的 visible-prefix 最短服务 pair；原模型/服务/负载参数。
set -euo pipefail
test "$#" -eq 1
variant=$1
[[ "$variant" =~ ^(baseline|visible-prefix)$ ]]
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-$variant-context16k"
control="$run-control"
source_dir="$root/code/$variant-context-$stamp"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$source_dir" "$control" "$variant" <<'PY'
from pathlib import Path
import sys,hashlib,json,shutil,socket,subprocess
root,source,control=map(Path,sys.argv[1:4]);variant=sys.argv[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('device occupied')
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host,9031))==0:raise RuntimeError('port occupied')
if sha(root/'scripts/run_framework_screen.py')!='bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9':raise RuntimeError('driver changed')
base=root/'code/sql-mixed-20261021T080656Z'
if sha(base/'vllm_fl/worker/model_runner.py')!='e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1':raise RuntimeError('base changed')
if variant=='visible-prefix':
    builder=root/'scripts/prepare_visible_prefix_source.py'
    if sha(builder)!='a4e978770e98aa3c5a245de96470916aae570ef63a55083534465309ceaf615f':raise RuntimeError('builder changed')
    subprocess.run(['python3',str(builder),'--base-source',str(base),'--output',str(source),'--asset-dir',str(root/'scripts')],check=True)
    shutil.copyfile(builder,control/builder.name)
else:
    shutil.copytree(base,source,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
shutil.copytree(source,control/'plugin-source')
(control/'source-sha256.json').write_text(json.dumps({str(p.relative_to(source)):sha(p) for p in sorted(source.rglob('*')) if p.is_file()},indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'visible-prefix matched short service; not official','variant':variant,'source':str(source),'base':str(base),'preflight_gpu':query,'ixsmi':table,'source_change':variant=='visible-prefix','artifact_environment_only':'BIV150_VISIBLE_PREFIX_ARTIFACTS'},indent=2)+'\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
export BIV150_VISIBLE_PREFIX_ARTIFACTS="$control/prefix-artifacts"
marker=BIV150_SQL_REFLECTION_INSTALLED
if [[ "$variant" == visible-prefix ]]; then marker=BIV150_VISIBLE_PREFIX_READY; fi
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --context-screen --seed 721201 --require-log-marker "$marker")
printf 'BIV150_VISIBLE_PREFIX_ARTIFACTS=%q ' "$BIV150_VISIBLE_PREFIX_ARTIFACTS" > "$control/command.txt"
printf '%q ' "${command[@]}" >> "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
