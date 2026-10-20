#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <profile-id> <input-len>" >&2
  exit 2
fi

PROFILE_ID=$1
INPUT_LEN=$2
ROOT=/workspace/experiments/minicpm-s2
RUN_DIR="$ROOT/profiles/$PROFILE_ID/prefill"

curl -fsS -X POST http://127.0.0.1:9031/start_profile \
  | tee "$RUN_DIR/start-profile.response"

bash /workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh \
  "$RUN_DIR" "first-iterations" "$INPUT_LEN" 16 64 64

curl -fsS -X POST http://127.0.0.1:9031/stop_profile \
  | tee "$RUN_DIR/stop-profile.response"
sleep 10
find "$RUN_DIR/trace" -maxdepth 2 -type f -printf '%P %s bytes\n' \
  | sort > "$RUN_DIR/trace-files.txt"
cat "$RUN_DIR/trace-files.txt"
