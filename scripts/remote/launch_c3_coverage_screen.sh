#!/usr/bin/env bash
# 一次真实 C3 覆盖诊断；不将带计数器的耗时作为性能基线。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-c3-coverage-context16k"
control="$run-control"
source_dir="$root/code/c3-coverage-$stamp"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$source_dir" "$control" <<'PY'
import sys,pathlib,hashlib,json,shutil,runpy,socket,subprocess
root,source,control=map(pathlib.Path,sys.argv[1:])
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
if query.strip()!='68, 0':raise RuntimeError('device is not idle: '+query)
with socket.socket() as sock:
    sock.settimeout(2)
    if sock.connect_ex(('127.0.0.1',9031))==0:raise RuntimeError('port is occupied')
module=root/'scripts/biv150_c3_coverage.py'
if hashlib.sha256(module.read_bytes()).hexdigest()!='29137c16ceb1d811b6b29b28782e2dcdf3463fce154917b16871d3157f7466b3':raise RuntimeError('coverage module changed')
driver=root/'scripts/run_framework_screen.py'
if hashlib.sha256(driver.read_bytes()).hexdigest()!='bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9':raise RuntimeError('screen driver changed')
base=root/'code/sql-mixed-20261021T080656Z'
shutil.copytree(base,source,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
runner=source/'vllm_fl/worker/model_runner.py'
transformed=runpy.run_path(str(module))['transform_source'](runner.read_bytes())
if hashlib.sha256(transformed).hexdigest()!='a39a894a67771e724fc198ea1c3720d1504806cc3d07723a2e3f36fe4d6e6675':raise RuntimeError('transformed runner differs')
runner.write_bytes(transformed)
shutil.copyfile(module,source/'vllm_fl/patches/biv150_c3_coverage.py')
shutil.copytree(source,control/'plugin-source')
files={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.rglob('*')) if p.is_file()}
(control/'source-sha256.json').write_text(json.dumps(files,indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'C3 CPU counter diagnostic, not performance comparison','preflight_gpu_query':query,'base':str(base),'source':str(source),'counter_plan_is_forward_execution':False},indent=2)+'\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --context-screen --seed 721201 --require-log-marker BIV150_C3_COVERAGE_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
