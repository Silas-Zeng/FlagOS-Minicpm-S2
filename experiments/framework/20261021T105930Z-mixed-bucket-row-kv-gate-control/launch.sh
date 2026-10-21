#!/usr/bin/env bash
# One bounded, no-weight device gate. The Python gate owns the shared lock.
set -euo pipefail
test "$#" -eq 1
source_dir=$1
root=/workspace/experiments/minicpm-s2
[[ "$source_dir" == "$root/code/"* ]]
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-mixed-bucket-row-kv-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(timeout --signal=TERM --kill-after=10s 240s python3 "$root/scripts/validate_mixed_token_bucket.py"
  --run-dir "$run"
  --runtime-path "$source_dir/vllm_fl/patches/biv150_decode_launch_runtime.py"
  --mixed-path "$source_dir/vllm_fl/patches/biv150_mixed_decode.py"
  --bucket-path "$root/scripts/biv150_mixed_token_bucket.py")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$root/scripts/validate_mixed_token_bucket.py" "$root/scripts/biv150_mixed_token_bucket.py" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
