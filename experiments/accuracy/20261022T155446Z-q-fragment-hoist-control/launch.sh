#!/usr/bin/env bash
# 复用已测413源码与原Math500 gate，仅追加候选artifact目录和安装marker。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
source_dir="$root/code/q-hoist-service-candidate-20261022T153947Z"
reference="$root/framework/20261022T153947Z-q-hoist-service-candidate-decode4k-control/source-sha256.json"
python3 - "$source_dir" "$reference" <<'PY'
from pathlib import Path
import hashlib,json,socket,subprocess,sys
source,reference=map(Path,sys.argv[1:])
driver=Path('/workspace/experiments/minicpm-s2/scripts/run_accuracy_gate.py')
assert hashlib.sha256(driver.read_bytes()).hexdigest()=='35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54','original accuracy driver changed'
expected=json.loads(reference.read_text())
assert len(expected)==413 and expected['vllm_fl/patches/biv150_q_fragment_service.py']=='77b489a8ed0d306558405152f94ae4c19cbc2d7132b11a56d0b9610f6e729a6d'
actual={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file() and not any(x in ('.git','__pycache__') for x in p.relative_to(source).parts) and p.suffix not in ('.pyc','.pyo')}
assert actual==expected,'tested service source changed'
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
assert query.strip()=='68, 0' and 'No running processes found' in subprocess.check_output(['ixsmi'],text=True)
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
 with socket.socket(family,socket.SOCK_STREAM) as s:
  s.settimeout(1);assert s.connect_ex((host,9031))!=0
PY
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/accuracy/$stamp-q-fragment-hoist"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
cp "$reference" "$control/source-sha256.json"
mkdir "$control/q-hoist-artifacts"
command=(env "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts"
 python3 "$root/scripts/run_accuracy_gate.py" "$run" --source-dir "$source_dir"
 --require-log-marker BIV150_Q_FRAGMENT_SERVICE_INSTALLED
 --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$root/scripts/run_accuracy_gate.py" "$root/scripts/run_math500_level3.sh" "$root/scripts/snapshot_tuning_db.py" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
