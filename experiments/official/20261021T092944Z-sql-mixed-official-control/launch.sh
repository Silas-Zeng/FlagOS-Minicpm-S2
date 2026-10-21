#!/usr/bin/env bash
# One owned official throughput gate; source selection is explicit.
set -euo pipefail
test "$#" -ge 2 && test "$#" -le 3
source_dir=$1
label=$2
# Pass an explicit empty third argument for the unmodified baseline.
log_marker=${3-BIV150_SQL_REFLECTION_INSTALLED}
[[ "$label" =~ ^[a-z0-9-]+$ ]]
root=/workspace/experiments/minicpm-s2
mkdir -p "$root/official"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/official/$stamp-$label"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
command=(python3 "$root/scripts/run_official_gate.py" "$run" --source-dir "$source_dir" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db)
if [[ -n "$log_marker" ]]; then
  command+=(--require-log-marker "$log_marker")
fi
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$root/scripts/run_official_gate.py" "$root/scripts/run_accuracy_gate.py" "$root/scripts/run_math500_level3.sh" "$root/scripts/snapshot_tuning_db.py" "$root/scripts/monitor_gpu.sh" /workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
