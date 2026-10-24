#!/usr/bin/env bash
# 两个真实后端正确性形状和一次 ABBA；不启动服务。
set -euo pipefail
test "$#" -eq 1
source_dir=$1
root=/workspace/experiments/minicpm-s2
[[ "$source_dir" == "$root/code/"* ]]
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-attention-key-recipe-diagnostic"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(env VLLM_PLUGINS=fl "PYTHONPATH=$source_dir"
  timeout --signal=TERM --kill-after=15s 380s
  python3 "$root/scripts/validate_attention_hot_launch_diagnostic.py"
  --run-dir "$run"
  --runtime-path "$source_dir/vllm_fl/patches/biv150_decode_launch_runtime.py"
  --mixed-path "$source_dir/vllm_fl/patches/biv150_mixed_decode.py"
  --policy-path "$root/scripts/biv150_attention_key_recipe_diagnostic.py")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$root/scripts/validate_attention_hot_launch_diagnostic.py" "$root/scripts/biv150_attention_key_recipe_diagnostic.py" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
