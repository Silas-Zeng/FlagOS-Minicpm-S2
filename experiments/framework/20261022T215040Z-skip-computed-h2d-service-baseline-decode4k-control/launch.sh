#!/usr/bin/env bash
# 方法门通过且官方清理后才启动原bc51短服务；每次一侧，不加profiler/每步日志。
set -euo pipefail
test "$#" -eq 3
base_dir=$1
variant=$2
method_gate=$3
[[ "$variant" == baseline || "$variant" == candidate ]]
root=/workspace/experiments/minicpm-s2
[[ "$base_dir" == "$root/code/"* ]]
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-skip-computed-h2d-service-$variant-decode4k"
control="$run-control"
source_dir="$root/code/skip-computed-h2d-service-$variant-$stamp"
python3 - "$root" "$assets" <<'PY'
from pathlib import Path
import hashlib, socket, subprocess, sys
root, assets = map(Path, sys.argv[1:])
for name,pin in {
    "prepare_service_source.py":"e174044c38fe21351c23922d1307003a47e876513a8864a03eb5e3be4c96f1f3",
    "prepare_skip_computed_h2d.py":"23d833a1bd3f4155652a2457b19bdaedf29b918de488e18e5b986b2cb5e08427",
    "base-source-sha256.json":"bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392",
    "expected-source-sha256.json":"425245ed4b8a0f086dc1ac99807d137f21f0128aaa1ada45a576c19bd639c0dd",
}.items():
    if hashlib.sha256((assets/name).read_bytes()).hexdigest()!=pin:
        raise RuntimeError("冻结资产变化: "+name)
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
cp "$assets/prepare_service_source.py" "$assets/prepare_skip_computed_h2d.py" "$assets/base-source-sha256.json" "$assets/expected-source-sha256.json" "$control/"
python3 "$control/prepare_service_source.py" --base-dir "$base_dir" --output-dir "$source_dir" --variant "$variant" --method-gate-dir "$method_gate" > "$control/preparation.log"
cp "$source_dir-preparation.json" "$control/preparation.json"
python3 - "$control" <<'PY'
import json, shutil, sys
from pathlib import Path
control = Path(sys.argv[1])
receipt = json.loads((control/'preparation.json').read_text())
(control/'purpose.json').write_text(json.dumps(receipt, indent=2) + '\n')
(control/'source-sha256.json').write_text(json.dumps(receipt['source_sha256'], indent=2) + '\n')
shutil.copytree(receipt['source'], control/'plugin-source')
gate = Path(receipt['method_gate']['run'])
shutil.copyfile(gate/'results.json', control/'method-gate-results.json')
shutil.copyfile(gate/'manifest.json', control/'method-gate-manifest.json')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
mkdir "$control/q-hoist-artifacts"
command=(env -u BIV150_FINITE_GROWTH_ADMISSION
  "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts"
  python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir"
  --decode-screen --seed 721201 --require-log-marker BIV150_Q_FRAGMENT_SERVICE_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nVARIANT=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$variant" "$runner_pid"
