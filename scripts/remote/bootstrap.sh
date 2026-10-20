#!/usr/bin/env bash
set -euo pipefail

ROOT=/workspace/experiments/minicpm-s2
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
RUN_DIR="$ROOT/environment/$STAMP"
mkdir -p "$RUN_DIR"

{
  echo "timestamp_utc=$STAMP"
  echo "hostname=$(hostname)"
  echo "kernel=$(uname -a)"
  echo "python=$(python3 --version 2>&1)"
  echo "torch=$(python3 -c 'import torch; print(torch.__version__)' 2>&1)"
  echo "cuda_available=$(python3 -c 'import torch; print(torch.cuda.is_available())' 2>&1)"
  echo "device_count=$(python3 -c 'import torch; print(torch.cuda.device_count())' 2>&1)"
  echo "device_names=$(python3 -c 'import torch; print([torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])' 2>&1)"
  echo "corex_version=${COREX_VERSION:-unset}"
  echo "corex_visible_devices=${COREX_VISIBLE_DEVICES:-unset}"
  echo "vllm_plugins=${VLLM_PLUGINS:-unset}"
} > "$RUN_DIR/packages.txt"

/usr/local/corex-4.5.0/bin/ixsmi -q > "$RUN_DIR/ixsmi.txt" 2>&1 || true
free -h > "$RUN_DIR/memory.txt"
df -h /workspace / > "$RUN_DIR/disk.txt"

git -C /workspace/vllm-plugin-FL status --short --branch \
  > "$RUN_DIR/vllm-plugin-FL-git.txt" 2>&1
git -C /workspace/vllm-plugin-FL rev-parse HEAD \
  >> "$RUN_DIR/vllm-plugin-FL-git.txt" 2>&1
git -C /workspace/FlagGems status --short --branch \
  > "$RUN_DIR/FlagGems-git.txt" 2>&1
git -C /workspace/FlagGems rev-parse HEAD \
  >> "$RUN_DIR/FlagGems-git.txt" 2>&1
git -C /workspace/FlagGems describe --tags --always \
  >> "$RUN_DIR/FlagGems-git.txt" 2>&1

sha256sum \
  /workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py \
  /workspace/MiniCPM5-2B/config.json \
  /workspace/MiniCPM5-2B/model-00000-of-00001.safetensors \
  > "$RUN_DIR/hashes.txt"

echo "$RUN_DIR"
