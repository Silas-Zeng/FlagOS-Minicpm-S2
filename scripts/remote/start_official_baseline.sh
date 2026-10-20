#!/usr/bin/env bash
set -euo pipefail

ROOT=/workspace/experiments/minicpm-s2
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
RUN_DIR="$ROOT/baseline/$STAMP"
mkdir -p "$RUN_DIR"

if ss -ltn 2>/dev/null | grep -q ':9031 '; then
  echo "Port 9031 is already in use" >&2
  exit 2
fi

cat > "$RUN_DIR/server-command.txt" <<'EOF'
export VLLM_PLUGINS=fl
vllm serve /workspace/MiniCPM5-2B \
  --port 9031 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --served-model-name minicpm \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072
EOF

cd /workspace
setsid env VLLM_PLUGINS=fl vllm serve /workspace/MiniCPM5-2B \
  --port 9031 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --served-model-name minicpm \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072 \
  > "$RUN_DIR/server.log" 2>&1 < /dev/null &

pid=$!
echo "$pid" > "$RUN_DIR/server.pid"
echo "$RUN_DIR"
