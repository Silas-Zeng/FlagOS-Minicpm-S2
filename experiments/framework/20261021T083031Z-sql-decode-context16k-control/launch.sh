#!/usr/bin/env bash
# Source is an already reviewed isolated candidate; one owned 16K short load.
set -euo pipefail
test "$#" -eq 2
source_dir=$1
label=$2
[[ "$label" =~ ^[a-z0-9-]+$ ]]
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-$label-context16k"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --context-screen --seed 721201 --require-log-marker BIV150_SQL_REFLECTION_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
