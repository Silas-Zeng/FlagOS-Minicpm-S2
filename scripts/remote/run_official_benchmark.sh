#!/usr/bin/env bash
set -euo pipefail

ROOT=/workspace/experiments/minicpm-s2
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
RUN_DIR="$ROOT/baseline/$STAMP"
mkdir -p "$RUN_DIR"

cd /workspace
python3 /workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py \
  --model /workspace/MiniCPM5-2B \
  --served-model-name minicpm \
  --port 9031 \
  --test-cases '[[4096,1024,64,256],[16384,1024,64,128]]' \
  2>&1 | tee "$RUN_DIR/benchmark.log"

find /workspace/benchmark_results -maxdepth 2 -type f -printf '%T@ %p\n' \
  2>/dev/null | sort -n | tail -20 > "$RUN_DIR/result-files.txt"
