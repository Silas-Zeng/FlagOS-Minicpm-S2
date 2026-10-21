#!/usr/bin/env bash
# 单设备门；只改独立 JIT 的 CTA 枚举，不改 installed 或稳定候选。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-mm-cta-group-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" <<'PY'
from pathlib import Path
import sys,hashlib
root=Path(sys.argv[1])
for name,expected in [('validate_mm_cta_group.py','4b44b930aad534301c1545d5748a6dae2a85e2345d7a446185a46d5082d71cd9'),('biv150_mm_cta_group.py','06c7cd9216907886e7d66a81d4fd5d9f78edef9daac2380ca263ce8c1770b8e1')]:
    if hashlib.sha256((root/'scripts'/name).read_bytes()).hexdigest()!=expected:
        raise RuntimeError('reviewed script mismatch: '+name)
PY
command=(python3 "$root/scripts/validate_mm_cta_group.py" --run-dir "$run" --policy-path "$root/scripts/biv150_mm_cta_group.py" --mm-source /usr/local/lib/python3.12/site-packages/flag_gems/runtime/backend/_iluvatar/ops/mm.py --model /workspace/MiniCPM5-2B)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nRUNNER_PID=%s\n' "$run" "$control" "$runner_pid"
