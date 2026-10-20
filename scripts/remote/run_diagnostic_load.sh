#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 6 ]]; then
  echo "usage: $0 <run-dir> <label> <input-len> <output-len> <concurrency> <num-prompts>" >&2
  exit 2
fi

RUN_DIR=$1
LABEL=$2
INPUT_LEN=$3
OUTPUT_LEN=$4
CONCURRENCY=$5
NUM_PROMPTS=$6
mkdir -p "$RUN_DIR"

export VLLM_PLUGINS=fl
export PYTHONUNBUFFERED=1
exec vllm bench serve \
  --backend vllm \
  --model minicpm \
  --tokenizer /workspace/MiniCPM5-2B \
  --endpoint /v1/completions \
  --host 127.0.0.1 \
  --port 9031 \
  --dataset-name random \
  --ignore-eos \
  --random-input-len "$INPUT_LEN" \
  --random-output-len "$OUTPUT_LEN" \
  --max-concurrency "$CONCURRENCY" \
  --num-prompts "$NUM_PROMPTS" \
  --num-warmups 0 \
  --seed 0 \
  --disable-tqdm \
  > "$RUN_DIR/load-$LABEL.log" 2>&1
