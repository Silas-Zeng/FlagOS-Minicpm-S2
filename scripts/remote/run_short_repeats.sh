#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 8 || $# -gt 9 ]]; then
  echo "usage: $0 <run-dir> <label-prefix> <repetitions> <input> <output> <concurrency> <prompts> <control-dir> [base-seed]" >&2
  exit 2
fi

RUN_DIR=$1
LABEL_PREFIX=$2
REPETITIONS=$3
INPUT_LEN=$4
OUTPUT_LEN=$5
CONCURRENCY=$6
NUM_PROMPTS=$7
CONTROL_DIR=$8
BASE_SEED=${9:-20261021}

mkdir -p "$RUN_DIR" "$CONTROL_DIR"
printf 'started_at_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > "$CONTROL_DIR/manifest.txt"
printf 'input=%s\noutput=%s\nconcurrency=%s\nprompts=%s\nrepetitions=%s\nbase_seed=%s\n' \
  "$INPUT_LEN" "$OUTPUT_LEN" "$CONCURRENCY" "$NUM_PROMPTS" "$REPETITIONS" \
  "$BASE_SEED" >> "$CONTROL_DIR/manifest.txt"

status=0
for ((run = 1; run <= REPETITIONS; run++)); do
  label="${LABEL_PREFIX}-r${run}"
  seed=$((BASE_SEED + run - 1))
  if ! /workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh \
    "$RUN_DIR" "$label" "$INPUT_LEN" "$OUTPUT_LEN" \
    "$CONCURRENCY" "$NUM_PROMPTS" "$seed"; then
    status=$?
    break
  fi
done

echo "$status" > "$CONTROL_DIR/exit-code"
printf 'finished_at_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  >> "$CONTROL_DIR/manifest.txt"
exit "$status"
