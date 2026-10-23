#!/usr/bin/env bash
# 原bc51短服务仅判断真实编译recipe命中；不加profiler、不自动重复。
set -euo pipefail
test "$#" -eq 3
base_dir=$1
variant=$2
screen=$3
[[ "$variant" == baseline || "$variant" == candidate ]]
case "$screen" in
  decode4k) screen_arg=--decode-screen ;;
  context16k-long) screen_arg=--context-long-screen ;;
  *) exit 2 ;;
esac
root=/workspace/experiments/minicpm-s2
[[ "$base_dir" == "$root/code/"* ]]
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-q-gqa-service-$variant-$screen"
control="$run-control"
source_dir="$root/code/q-gqa-service-$variant-$stamp"
python3 - "$root" <<'PY'
from pathlib import Path
import hashlib, socket, subprocess, sys
root = Path(sys.argv[1])
if hashlib.sha256((root/'scripts/run_framework_screen.py').read_bytes()).hexdigest() != 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9':
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
cp "$assets/prepare_q_gqa_service.py" "$assets/biv150_q_fragment_service.py" "$assets/service_append.py" "$assets/base-source-sha256.json" "$assets/biv150_gqa_decode.py" "$assets/gqa_append.py" "$control/"
python3 "$control/prepare_q_gqa_service.py" --base-dir "$base_dir" --output-dir "$source_dir" --variant "$variant" > "$control/preparation.log"
cp "$source_dir-preparation.json" "$control/preparation.json"
python3 - "$control" <<'PY'
import json, shutil, sys
from pathlib import Path
control = Path(sys.argv[1])
receipt = json.loads((control/'preparation.json').read_text())
(control/'purpose.json').write_text(json.dumps(receipt, indent=2) + '\n')
(control/'source-sha256.json').write_text(json.dumps(receipt['source_sha256'], indent=2) + '\n')
shutil.copytree(receipt['source'], control/'plugin-source')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
mkdir "$control/q-hoist-artifacts"
marker=BIV150_GQA_DECODE_INSTALL
if [[ "$variant" == candidate ]]; then marker=BIV150_Q_FRAGMENT_SERVICE_INSTALLED; fi
command=(env "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts"
  python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir"
  "$screen_arg" --seed 721201 --require-log-marker "$marker")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nVARIANT=%s\nSCREEN=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$variant" "$screen" "$runner_pid"
