#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <diagnostic-run-dir>" >&2
  exit 2
fi

RUN_DIR=$1
TRACE_DIR="$RUN_DIR/trace"
mkdir -p "$TRACE_DIR"

if timeout 1 bash -c 'exec 3<>/dev/tcp/127.0.0.1/9031' 2>/dev/null; then
  echo "Port 9031 is already in use; stop the baseline service first" >&2
  exit 2
fi

profiler_config=$(
  python3 - "$TRACE_DIR" <<'PY'
import json
import sys

print(
    json.dumps(
        {
            "profiler": "torch",
            "torch_profiler_dir": sys.argv[1],
            "torch_profiler_with_stack": False,
            "torch_profiler_with_flops": False,
            "torch_profiler_use_gzip": True,
            "torch_profiler_dump_cuda_time_total": True,
            "torch_profiler_record_shapes": True,
            "torch_profiler_with_memory": False,
            "ignore_frontend": True,
            "delay_iterations": 0,
            "max_iterations": 0,
            "warmup_iterations": 0,
            "active_iterations": 5,
            "wait_iterations": 0,
        },
        separators=(",", ":"),
    )
)
PY
)

cat > "$RUN_DIR/server-command.txt" <<EOF
export VLLM_PLUGINS=fl
vllm serve /workspace/MiniCPM5-2B \\
  --port 9031 \\
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \\
  --served-model-name minicpm \\
  --gpu-memory-utilization 0.85 \\
  --max-model-len 131072 \\
  --profiler-config '$profiler_config'

# The profiler options are diagnostic-only and are not part of the official
# baseline or final scoring command.
EOF

env | grep -E '^(VLLM_|FLAG|COREX_|USE_C_EXTENSION)=' \
  | sort > "$RUN_DIR/inherited-env.txt" || true

cd /workspace
setsid env VLLM_PLUGINS=fl PYTHONUNBUFFERED=1 \
  vllm serve /workspace/MiniCPM5-2B \
  --port 9031 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --served-model-name minicpm \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072 \
  --profiler-config "$profiler_config" \
  > "$RUN_DIR/server.log" 2>&1 < /dev/null &

echo "$!" > "$RUN_DIR/server.pid"
echo "$RUN_DIR"
