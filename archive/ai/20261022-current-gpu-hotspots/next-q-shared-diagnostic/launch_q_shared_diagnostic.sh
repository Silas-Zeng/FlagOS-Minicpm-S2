#!/usr/bin/env bash
# 原Attention硬件指标短诊断；不计性能收益，控制器独占卡。
set -euo pipefail
test "$#" -eq 1
source_dir=$1
assets=$(cd -- "$(dirname -- "$0")" && pwd)
root=/workspace/experiments/minicpm-s2
[[ "$source_dir" == "$root/code/"* ]]
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-q-shared-hardware-diagnostic"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(env VLLM_PLUGINS=fl "PYTHONPATH=$source_dir:$root/scripts"
  timeout --signal=TERM --kill-after=15s 380s
  python3 "$assets/diagnose_q_shared.py"
  --run-dir "$run"
  --runtime-path "$source_dir/vllm_fl/patches/biv150_decode_launch_runtime.py"
  --mixed-path "$source_dir/vllm_fl/patches/biv150_mixed_decode.py"
  --model /workspace/MiniCPM5-2B)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$assets/diagnose_q_shared.py" "$assets/worker.py" "$assets/fixture.py" "$assets/asset-pins.json" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
