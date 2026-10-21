#!/usr/bin/env bash
# 原方法与候选方法串行比较；固定输入、地址和原 event 生命周期。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-cpu-metadata-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" <<'PY'
from pathlib import Path
import sys,hashlib
root=Path(sys.argv[1])
for name,expected in [('validate_cpu_metadata.py','b1240720b588dae25d92cc1c173d64c1ea5f6e34fcdcab5dd0156407ebbcb757'),('biv150_cpu_metadata.py','0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f'),('biv150_cpu_metadata_source.py','0096cdac2c63544b5e3e62766168dc3df22f6ab63c09231bf9c6e93abaf29835')]:
    if hashlib.sha256((root/'scripts'/name).read_bytes()).hexdigest()!=expected:
        raise RuntimeError('reviewed script mismatch: '+name)
PY
command=(python3 "$root/scripts/validate_cpu_metadata.py" --run-dir "$run" --runtime-path "$root/scripts/biv150_cpu_metadata.py" --transform-path "$root/scripts/biv150_cpu_metadata_source.py" --runner-path "$root/code/sql-mixed-20261021T080656Z/vllm_fl/worker/model_runner.py")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nRUNNER_PID=%s\n' "$run" "$control" "$runner_pid"
