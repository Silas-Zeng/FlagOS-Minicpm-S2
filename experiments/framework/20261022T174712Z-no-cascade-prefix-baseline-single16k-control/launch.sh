#!/usr/bin/env bash
# 同一单请求16K/128out/c1负载：skip候选与干净6f分别串行运行。
set -euo pipefail
test "$#" -eq 2
base_dir=$1
variant=$2
[[ "$variant" == candidate || "$variant" == baseline ]]
root=/workspace/experiments/minicpm-s2
[[ "$base_dir" == "$root/code/"* ]]
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-no-cascade-prefix-$variant-single16k"
control="$run-control"
source_dir="$root/code/no-cascade-prefix-$variant-$stamp"
python3 - "$root" "$assets" <<'PY'
from pathlib import Path
import hashlib, socket, subprocess, sys
root = Path(sys.argv[1])
assets = Path(sys.argv[2])
if hashlib.sha256((root/'scripts/run_framework_screen.py').read_bytes()).hexdigest() != 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9':
    raise RuntimeError('原 shortscreen 已改变')
if hashlib.sha256((assets/'run_prefix_skip_short.py').read_bytes()).hexdigest() != '38d8ba38669d8dacb1c4629062aaa61a43c23f70433d6d707cfad38a9408b77c':
    raise RuntimeError('单点driver已改变')
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
cp "$assets/prepare_prefix_skip.py" "$assets/biv150_no_cascade_prefix.py" "$assets/skip_init_footer.py" "$assets/base-source-sha256.json" "$assets/run_prefix_skip_short.py" "$control/"
python3 "$control/prepare_prefix_skip.py" --base-dir "$base_dir" --output-dir "$source_dir" --variant "$variant" > "$control/preparation.log"
cp "$source_dir-preparation.json" "$control/preparation.json"
python3 - "$control" <<'PY'
import json, shutil, sys
from pathlib import Path
control = Path(sys.argv[1])
receipt = json.loads((control/'preparation.json').read_text())
(control/'purpose.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
(control/'source-sha256.json').write_text(json.dumps(receipt['source_sha256'], indent=2) + '\n')
shutil.copytree(receipt['source'], control/'plugin-source')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(env -u BIV150_PREFIX_COST_OBSERVE -u BIV150_NO_CASCADE_PREFIX_SKIP)
if [[ "$variant" == candidate ]]; then
  command+=("BIV150_NO_CASCADE_PREFIX_SKIP=1")
fi
command+=(python3 "$control/run_prefix_skip_short.py" "$run" --source-dir "$source_dir" --decode-screen --seed 721201 --prefix-variant "$variant")
if [[ "$variant" == candidate ]]; then
  command+=(--require-log-marker BIV150_PREFIX_SKIP_CORE_HOOKED)
fi
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nVARIANT=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$variant" "$runner_pid"
