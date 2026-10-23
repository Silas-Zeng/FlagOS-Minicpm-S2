#!/usr/bin/env bash
# 有限KV准入的未改调度基线；原bc51长负载，关闭profiler。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
base="$root/code/q-gqa-service-candidate-20261022T184141Z"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-finite-growth-baseline-context16k-long"
control="$run-control"
source_dir="$root/code/finite-growth-baseline-$stamp"
python3 - "$root" <<'PY'
from pathlib import Path
import hashlib,socket,subprocess,sys
root=Path(sys.argv[1])
assert hashlib.sha256((root/'scripts/run_framework_screen.py').read_bytes()).hexdigest()=='bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9'
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
assert query.strip()=='68, 0' and 'No running processes found' in table,table
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
 with socket.socket(family,socket.SOCK_STREAM) as s:
  s.settimeout(2);assert s.connect_ex((host,9031))!=0,host
PY
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$base" "$source_dir" "$control" <<'PY'
from pathlib import Path
import hashlib,json,shutil,sys
root,base,source,control=map(Path,sys.argv[1:])
expected=json.loads((root/'framework/20261022T184141Z-q-gqa-service-candidate-context16k-long-control/source-sha256.json').read_text())
def mapping(folder):
 return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob('*')) if p.is_file() and not any(x in ('.git','__pycache__') for x in p.relative_to(folder).parts) and p.suffix not in ('.pyc','.pyo')}
assert len(expected)==414 and mapping(base)==expected
assert expected['vllm_fl/worker/model_runner.py']=='cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
shutil.copytree(base,source,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
assert mapping(source)==expected
shutil.copytree(source,control/'plugin-source')
(control/'source-sha256.json').write_text(json.dumps(expected,indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'有限KV准入的未改调度基线；原bc51服务，非诊断','base':str(base),'source':str(source),'changed_paths':[],'source_count':414},ensure_ascii=False,indent=2)+'\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
mkdir "$control/q-hoist-artifacts"
command=(env "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts" python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --context-long-screen --seed 721201 --require-log-marker BIV150_Q_FRAGMENT_SERVICE_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
