#!/usr/bin/env bash
# 同一冻结 SQL+C3 基点，每次只测一个已互审的小改动。
set -euo pipefail
test "$#" -eq 1
variant=$1
[[ "$variant" =~ ^(baseline|async-token|cpu-metadata)$ ]]
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-$variant-decode4k"
control="$run-control"
source_dir="$root/code/$variant-$stamp"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$source_dir" "$control" "$variant" <<'PY'
from pathlib import Path
import sys,hashlib,json,shutil,runpy,socket,subprocess
root,source,control=map(Path,sys.argv[1:4]);variant=sys.argv[4]
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:
    raise RuntimeError('device occupied: '+query)
with socket.socket() as sock:
    sock.settimeout(2)
    if sock.connect_ex(('127.0.0.1',9031))==0:raise RuntimeError('port occupied')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
driver=root/'scripts/run_framework_screen.py'
if sha(driver)!='bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9':raise RuntimeError('driver changed')
base=root/'code/sql-mixed-20261021T080656Z'
if sha(base/'vllm_fl/worker/model_runner.py')!='e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1':raise RuntimeError('base changed')
shutil.copytree(base,source,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
runner=source/'vllm_fl/worker/model_runner.py'
if variant!='baseline':
    if variant=='async-token':
        runtime,transform='biv150_async_token_update.py','biv150_async_token_update_sql_mixed_source.py'
        hashes=('1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc','cfd378a494c0ccbb5aece861527cdf59ccd148afbe53ac229a09bb43162bdb6f','f0d0bada4222038b69ed139d804622e27acd6aa4e19a37ff089b0ca35f393f41')
    else:
        runtime,transform='biv150_cpu_metadata.py','biv150_cpu_metadata_source.py'
        hashes=('0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f','0096cdac2c63544b5e3e62766168dc3df22f6ab63c09231bf9c6e93abaf29835','50493fb68b194ed935650a3a743d2f56696d7379b702f4d7717eecac0325a9de')
    runtime_path,transform_path=root/'scripts'/runtime,root/'scripts'/transform
    if (sha(runtime_path),sha(transform_path))!=hashes[:2]:raise RuntimeError('reviewed sources differ')
    runner.write_bytes(runpy.run_path(str(transform_path))['transform_source'](runner.read_bytes()))
    if sha(runner)!=hashes[2]:raise RuntimeError('transformed runner differs')
    shutil.copyfile(runtime_path,source/'vllm_fl/patches'/runtime)
    shutil.copyfile(transform_path,control/transform)
shutil.copytree(source,control/'plugin-source')
files={str(p.relative_to(source)):sha(p) for p in sorted(source.rglob('*')) if p.is_file()}
(control/'source-sha256.json').write_text(json.dumps(files,indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'matched short screening; not official','variant':variant,'base':str(base),'source':str(source),'preflight_gpu':query,'ixsmi':table},indent=2)+'\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --decode-screen --seed 721201 --require-log-marker BIV150_SQL_REFLECTION_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
