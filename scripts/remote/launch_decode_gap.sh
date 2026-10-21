#!/usr/bin/env bash
# One owned diagnostic, never an official performance result.
set -euo pipefail
root=/workspace/experiments/minicpm-s2
base=d60b02367a852826f653165953f31b6dc696658e
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/profiles/$stamp-host-gap"
control="$root/profiles/$stamp-host-gap-control"
source_dir="$root/code/host-gap-$stamp"
mkdir "$control" "$source_dir"
cp "$0" "$control/launch.sh"
git -C "$root/code/vllm-plugin-FL" archive "$base" | tar -x -C "$source_dir"
printf '%s\n' "$base" > "$source_dir/base-revision.txt"
printf '\n' >> "$source_dir/vllm_fl/worker/model_runner.py"
cat "$root/scripts/decode_gap_profile_footer.py" >> "$source_dir/vllm_fl/worker/model_runner.py"
sha256sum "$root/scripts/decode_gap_profile_footer.py" "$root/scripts/run_framework_screen.py" "$source_dir/vllm_fl/worker/model_runner.py" > "$control/source.sha256"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --host-profile --seed 721101 --require-log-marker MINICPM_DECODE_GAP_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
