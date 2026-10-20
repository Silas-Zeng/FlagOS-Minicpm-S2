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
SERVER_LOG="$RUN_DIR/server.log"
LOAD_LOG="$RUN_DIR/load-prefill.log"

if [[ ! -f "$SERVER_LOG" ]]; then
  echo "missing server log: $SERVER_LOG" >&2
  exit 2
fi

start_line=$(wc -l < "$SERVER_LOG")
python3 /workspace/experiments/minicpm-s2/scripts/profile_workload.py \
  --input-len "$INPUT_LEN" --output-len 16 --concurrency 64 \
  > "$LOAD_LOG" 2>&1 &
load_pid=$!
echo "$load_pid" > "$RUN_DIR/load.pid"
trap 'kill "$load_pid" 2>/dev/null || true' EXIT

deadline=$((SECONDS + 900))
while (( SECONDS < deadline )); do
  if ! kill -0 "$load_pid" 2>/dev/null; then
    echo "diagnostic load exited before prefill was observed" >&2
    wait "$load_pid"
    exit 1
  fi
  latest=$(tail -n +$((start_line + 1)) "$SERVER_LOG" \
    | grep 'Avg prompt throughput:' | tail -n 1 || true)
  if [[ "$latest" =~ Avg\ prompt\ throughput:\ ([1-9][0-9.]*) ]]; then
    break
  fi
  sleep 2
done

curl -fsS -X POST http://127.0.0.1:9031/start_profile \
  | tee "$RUN_DIR/start-profile.response"
sleep 4
curl -fsS -X POST http://127.0.0.1:9031/stop_profile \
  | tee "$RUN_DIR/stop-profile.response"

kill "$load_pid" 2>/dev/null || true
wait "$load_pid" 2>/dev/null || true
trap - EXIT
sleep 5
find "$RUN_DIR/trace" -maxdepth 2 -type f -printf '%P %s bytes\n' \
  | sort > "$RUN_DIR/trace-files.txt"
cat "$RUN_DIR/trace-files.txt"
