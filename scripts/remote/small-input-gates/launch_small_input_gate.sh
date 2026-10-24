#!/usr/bin/env bash
# 同一入口选择一个方法；每次控制器独占卡并完成清理后才能启动下一个。
set -euo pipefail
test "$#" -eq 2
method=$1
source_dir=$2
assets=$(cd -- "$(dirname -- "$0")" && pwd)
root=/workspace/experiments/minicpm-s2
[[ "$source_dir" == "$root/code/"* ]]
case "$method" in
  hot-key-v2) gate=validate_small_hot_key.py; policy=biv150_attention_key_recipe.py ;;
  c3views) gate=validate_small_c3_views.py; policy=biv150_c3_view_reuse.py ;;
  *) printf '%s\n' '方法只能是 hot-key-v2 或 c3views' >&2; exit 2 ;;
esac
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-small-input-$method-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(env VLLM_PLUGINS=fl "PYTHONPATH=$source_dir:$root/scripts"
  timeout --signal=TERM --kill-after=15s 380s
  python3 "$assets/$gate"
  --run-dir "$run"
  --runtime-path "$source_dir/vllm_fl/patches/biv150_decode_launch_runtime.py"
  --mixed-path "$source_dir/vllm_fl/patches/biv150_mixed_decode.py"
  --policy-path "$assets/$policy")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$assets/$gate" "$assets/$policy" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nMETHOD=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$method" "$runner_pid"
