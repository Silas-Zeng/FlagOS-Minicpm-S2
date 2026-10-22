#!/usr/bin/env bash
# 仅真实服务输入准备成本诊断；6f918 组合基点、原短筛参数。
set -euo pipefail
test "$#" -eq 1
base_dir=$1
assets=$(cd -- "$(dirname -- "$0")" && pwd)
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-input-prep-timing-combined-decode4k"
control="$run-control"
source_dir="$root/code/input-prep-timing-combined-$stamp"
python3 - "$root" <<'PY'
from pathlib import Path
import hashlib, socket, subprocess, sys
root = Path(sys.argv[1])
driver = root / 'scripts/run_framework_screen.py'
if hashlib.sha256(driver.read_bytes()).hexdigest() != 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9':
    raise RuntimeError('原 shortscreen 已改变')
query = subprocess.check_output(['ixsmi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True)
table = subprocess.check_output(['ixsmi'], text=True)
if query.strip() != '68, 0' or 'No running processes found' not in table:
    raise RuntimeError('设备不空闲: ' + query)
for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host, 9031)) == 0:
            raise RuntimeError('9031 正在使用: ' + host)
PY
mkdir "$control"
cp "$0" "$control/launch.sh"
cp "$assets/prepare_input_prep_timing.py" "$assets/biv150_input_prep_timing.py" "$control/"
python3 "$control/prepare_input_prep_timing.py" --base-dir "$base_dir" --output-dir "$source_dir" > "$control/preparation.log"
cp "$source_dir-preparation.json" "$control/preparation.json"
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(env "BIV150_INPUT_PREP_TIMING_OUTPUT_DIR=$control" python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --decode-screen --seed 721201 --require-log-marker BIV150_SQL_REFLECTION_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
