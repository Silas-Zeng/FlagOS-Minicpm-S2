#!/usr/bin/env bash
# Use only after the isolated SQL candidate has released the device.
set -euo pipefail
root=/workspace/experiments/minicpm-s2
source_dir="$root/code/vllm-plugin-FL"
expected=d60b02367a852826f653165953f31b6dc696658e
test "$(git -C "$source_dir" rev-parse HEAD)" = "$expected"
test -z "$(git -C "$source_dir" status --porcelain)"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-b0-sql-pair"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --decode-screen --seed 721101)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
