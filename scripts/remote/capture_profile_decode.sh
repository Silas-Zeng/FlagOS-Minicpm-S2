#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 6 ]]; then
  echo "usage: $0 <profile-id> <input-len> <output-len> <concurrency> <num-prompts> <min-steady-running>" >&2
  exit 2
fi

PROFILE_ID=$1
INPUT_LEN=$2
OUTPUT_LEN=$3
CONCURRENCY=$4
NUM_PROMPTS=$5
MIN_STEADY_RUNNING=$6
ROOT=/workspace/experiments/minicpm-s2
RUN_DIR="$ROOT/profiles/$PROFILE_ID/decode"
SERVER_LOG="$RUN_DIR/server.log"
LOAD_LOG="$RUN_DIR/load-steady-decode.log"

if [[ ! -f "$SERVER_LOG" ]]; then
  echo "missing server log: $SERVER_LOG" >&2
  exit 2
fi

start_line=$(wc -l < "$SERVER_LOG")
bash /workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh \
  "$RUN_DIR" "steady-decode" "$INPUT_LEN" "$OUTPUT_LEN" \
  "$CONCURRENCY" "$NUM_PROMPTS" &
load_pid=$!
echo "$load_pid" > "$RUN_DIR/load.pid"

deadline=$((SECONDS + 1200))
steady_observations=0
while (( SECONDS < deadline )); do
  if ! kill -0 "$load_pid" 2>/dev/null; then
    echo "diagnostic load exited before steady decode was observed" >&2
    wait "$load_pid"
    exit 1
  fi

  latest=$(tail -n +$((start_line + 1)) "$SERVER_LOG" \
    | grep 'Avg prompt throughput:' | tail -n 1 || true)
  if [[ "$latest" =~ Avg\ prompt\ throughput:\ 0\.0\ tokens/s.*Running:\ ([0-9]+)\ reqs ]]; then
    running=${BASH_REMATCH[1]}
    if (( running >= MIN_STEADY_RUNNING )); then
      steady_observations=$((steady_observations + 1))
    else
      steady_observations=0
    fi
  else
    steady_observations=0
  fi

  if (( steady_observations >= 2 )); then
    break
  fi
  sleep 5
done

if (( steady_observations < 2 )); then
  kill "$load_pid" 2>/dev/null || true
  echo "timed out waiting for steady decode" >&2
  exit 1
fi

curl -fsS -X POST http://127.0.0.1:9031/start_profile \
  | tee "$RUN_DIR/start-profile.response"
sleep 4
curl -fsS -X POST http://127.0.0.1:9031/stop_profile \
  | tee "$RUN_DIR/stop-profile.response"

wait "$load_pid"
sleep 10
find "$RUN_DIR/trace" -maxdepth 2 -type f -printf '%P %s bytes\n' \
  | sort > "$RUN_DIR/trace-files.txt"
cat "$RUN_DIR/trace-files.txt"
