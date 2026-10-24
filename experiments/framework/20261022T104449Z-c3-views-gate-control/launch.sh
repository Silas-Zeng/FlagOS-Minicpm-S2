#!/usr/bin/env bash
# Independent C3 view cleanup; two correctness shapes and one warm ABBA; no hot-key.
set -euo pipefail
test "$#" -eq 1
source_dir=$1
root=/workspace/experiments/minicpm-s2
[[ "$source_dir" == "$root/code/"* ]]
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-c3-views-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(env VLLM_PLUGINS=fl "PYTHONPATH=$source_dir"
  timeout --signal=TERM --kill-after=15s 380s
  python3 "$root/scripts/validate_c3_views.py"
  --run-dir "$run"
  --runtime-path "$source_dir/vllm_fl/patches/biv150_decode_launch_runtime.py"
  --mixed-path "$source_dir/vllm_fl/patches/biv150_mixed_decode.py"
  --policy-path "$root/scripts/biv150_c3_view_reuse.py")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$root/scripts/validate_c3_views.py" "$root/scripts/biv150_c3_view_reuse.py" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
