#!/usr/bin/env bash
set -euo pipefail
root=/workspace/experiments/minicpm-s2
base=d60b02367a852826f653165953f31b6dc696658e
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-sql-decode-screen"
control="$run-control"
source_dir="$root/code/sql-decode-$stamp"
mkdir "$control" "$source_dir"
cp "$0" "$control/launch.sh"
git -C "$root/code/vllm-plugin-FL" archive "$base" | tar -x -C "$source_dir"
printf '%s\n' "$base" > "$source_dir/base-revision.txt"
cp "$root/scripts/biv150_sql_reflection.py" "$root/scripts/biv150_decode_launch_runtime.py" "$source_dir/vllm_fl/patches/"
printf '\n' >> "$source_dir/vllm_fl/worker/model_runner.py"
cat "$root/scripts/sql_reflection_footer.py" "$root/scripts/decode_launch_footer.py" >> "$source_dir/vllm_fl/worker/model_runner.py"
sha256sum "$source_dir/vllm_fl/patches/biv150_sql_reflection.py" "$source_dir/vllm_fl/patches/biv150_decode_launch_runtime.py" "$source_dir/vllm_fl/worker/model_runner.py" "$root/scripts/run_framework_screen.py" > "$control/source.sha256"
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --decode-screen --seed 721101 --require-log-marker BIV150_DECODE_LAUNCH_FIRST_SELECTED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
