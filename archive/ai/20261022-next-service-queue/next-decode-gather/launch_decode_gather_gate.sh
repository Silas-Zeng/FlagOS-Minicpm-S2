#!/usr/bin/env bash
# 仅新增纯decode CPU gather资格与真实GPU正确性门。
set -euo pipefail
test "$#" -eq 1
source_dir=$1
root=/workspace/experiments/minicpm-s2
[[ "$source_dir" == "$root/code/"* ]]
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-decode-cpu-gather-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(env VLLM_PLUGINS=fl "PYTHONPATH=$source_dir:$root/scripts"
  timeout --signal=TERM --kill-after=15s 380s
  python3 "$assets/validate_decode_gather.py"
  --run-dir "$run"
  --runner-path "$source_dir/vllm_fl/worker/model_runner.py"
  --runtime-path "$source_dir/vllm_fl/patches/biv150_cpu_metadata.py"
  --async-runtime-path "$source_dir/vllm_fl/patches/biv150_async_token_update.py"
  --gather-runtime-path "$assets/biv150_decode_cpu_gather.py")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$assets/validate_decode_gather.py" "$assets/biv150_decode_cpu_gather.py" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
