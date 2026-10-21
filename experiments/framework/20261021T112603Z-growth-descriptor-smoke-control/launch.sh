#!/usr/bin/env bash
# One startup + greedy smoke, solely to observe real EngineCore scope fields.
set -euo pipefail
test "$#" -eq 1
source_dir=$1
root=/workspace/experiments/minicpm-s2
[[ "$source_dir" == "$root/code/growth-diagnostic-"* ]]
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-growth-descriptor-smoke"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
cp -a "$source_dir/vllm_fl" "$control/plugin-source"
cp "$source_dir/innovation-source.json" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(python3 "$root/scripts/run_framework_screen.py" "$run"
  --source-dir "$source_dir" --smoke-only
  --require-log-marker GROWTH_CONSTRUCTOR_DESCRIPTORS)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
