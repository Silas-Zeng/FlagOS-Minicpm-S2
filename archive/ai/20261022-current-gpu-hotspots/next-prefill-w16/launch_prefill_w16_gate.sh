#!/usr/bin/env bash
# 当前2D主热点的唯一新warp单点；控制器独占设备，失败也保原件。
set -euo pipefail
test "$#" -eq 1
source_dir=$1
assets=$(cd -- "$(dirname -- "$0")" && pwd)
root=/workspace/experiments/minicpm-s2
[[ "$source_dir" == "$root/code/"* ]]
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-prefill-w16-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(env VLLM_PLUGINS=fl "PYTHONPATH=$source_dir:$root/scripts"
  timeout --signal=TERM --kill-after=15s 380s
  python3 "$assets/validate_prefill_w16.py"
  --run-dir "$run"
  --runtime-path "$source_dir/vllm_fl/patches/biv150_decode_launch_runtime.py"
  --mixed-path "$source_dir/vllm_fl/patches/biv150_mixed_decode.py"
  --policy-path "$assets/biv150_prefill_w16.py"
  --model /workspace/MiniCPM5-2B)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$assets/validate_prefill_w16.py" "$assets/biv150_prefill_w16.py" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
