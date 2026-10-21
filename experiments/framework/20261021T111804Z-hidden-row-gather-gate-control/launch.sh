#!/usr/bin/env bash
# One owned, no-weight BF16 row-copy gate; the Python controller holds the lock.
set -euo pipefail
test "$#" -eq 1
source_dir=$1
root=/workspace/experiments/minicpm-s2
[[ "$source_dir" == "$root/code/"* ]]
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-hidden-row-gather-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(env VLLM_PLUGINS=fl "PYTHONPATH=$source_dir"
  timeout --signal=TERM --kill-after=15s 380s
  python3 "$root/scripts/validate_hidden_row_gather.py"
  --run-dir "$run"
  --runtime-path "$root/scripts/biv150_hidden_row_gather.py"
  --transform-path "$root/scripts/biv150_hidden_row_gather_source.py"
  --runner-path "$source_dir/vllm_fl/worker/model_runner.py")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$root/scripts/validate_hidden_row_gather.py" "$root/scripts/biv150_hidden_row_gather.py" "$root/scripts/biv150_hidden_row_gather_source.py" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
