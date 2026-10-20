#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <profile-id> <prefill|decode>" >&2
  exit 2
fi

PROFILE_ID=$1
PHASE=$2
if [[ "$PHASE" != "prefill" && "$PHASE" != "decode" ]]; then
  echo "phase must be prefill or decode" >&2
  exit 2
fi

ROOT=/workspace/experiments/minicpm-s2
RUN_DIR="$ROOT/profiles/$PROFILE_ID/$PHASE"
TRACE_DIR="$RUN_DIR/trace"
mkdir -p "$TRACE_DIR"

if timeout 1 bash -c 'exec 3<>/dev/tcp/127.0.0.1/9031' 2>/dev/null; then
  echo "Port 9031 is already in use; refusing to start a second server" >&2
  exit 2
fi

PROFILER_CONFIG=$(printf \
  '{"profiler":"torch","torch_profiler_dir":"%s","torch_profiler_with_stack":false,"torch_profiler_with_flops":false,"torch_profiler_use_gzip":true,"torch_profiler_dump_cuda_time_total":true,"torch_profiler_record_shapes":true,"torch_profiler_with_memory":false,"max_iterations":5}' \
  "$TRACE_DIR")

cat > "$RUN_DIR/server-command.txt" <<EOF
export VLLM_PLUGINS=fl
vllm serve /workspace/MiniCPM5-2B \\
  --port 9031 \\
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \\
  --served-model-name minicpm \\
  --gpu-memory-utilization 0.85 \\
  --max-model-len 131072 \\
  --profiler-config '$PROFILER_CONFIG'
EOF

cd /workspace
setsid env VLLM_PLUGINS=fl vllm serve /workspace/MiniCPM5-2B \
  --port 9031 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --served-model-name minicpm \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072 \
  --profiler-config "$PROFILER_CONFIG" \
  > "$RUN_DIR/server.log" 2>&1 < /dev/null &

pid=$!
echo "$pid" > "$RUN_DIR/server.pid"
echo "$RUN_DIR"
