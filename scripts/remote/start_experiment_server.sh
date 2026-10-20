#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <experiment-run-dir>" >&2
  exit 2
fi

RUN_DIR=$1
case "$RUN_DIR" in
  /workspace/experiments/minicpm-s2/*) ;;
  *)
    echo "run directory must be below /workspace/experiments/minicpm-s2" >&2
    exit 2
    ;;
esac

mkdir -p "$RUN_DIR"
if timeout 1 bash -c 'exec 3<>/dev/tcp/127.0.0.1/9031' 2>/dev/null; then
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

{
  printf 'VLLM_PLUGINS=fl\n'
  printf 'VLLM_FL_USE_FLAGGEMS_ATTN=%s\n' \
    "${VLLM_FL_USE_FLAGGEMS_ATTN:-<unset>}"
  printf 'USE_C_EXTENSION=%s\n' "${USE_C_EXTENSION:-<unset>}"
  printf 'FLAGTUNE=%s\n' "${FLAGTUNE:-<unset>}"
  printf 'COREX_VISIBLE_DEVICES=%s\n' \
    "${COREX_VISIBLE_DEVICES:-<unset>}"
  printf 'PYTHONPATH=%s\n' "${PYTHONPATH:-<unset>}"
} > "$RUN_DIR/inherited-env.txt"

cd /workspace
setsid env VLLM_PLUGINS=fl PYTHONUNBUFFERED=1 \
  vllm serve /workspace/MiniCPM5-2B \
  --port 9031 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --served-model-name minicpm \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072 \
  > "$RUN_DIR/server.log" 2>&1 < /dev/null &

echo "$!" > "$RUN_DIR/server.pid"
echo "$RUN_DIR"
