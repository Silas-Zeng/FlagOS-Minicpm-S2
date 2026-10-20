#!/usr/bin/env bash
set -euo pipefail

if ss -ltn 2>/dev/null | grep -q ':9031 '; then
  echo "port 9031 is in use" >&2
  exit 2
fi

free_mem=$(/usr/local/corex-4.5.0/bin/ixsmi --query-gpu=memory.free \
  --format=csv,noheader,nounits | head -n 1 | tr -d ' ')
if [[ ! "$free_mem" =~ ^[0-9]+$ ]] || (( free_mem < 30000 )); then
  echo "insufficient free device memory: ${free_mem:-unknown} MiB" >&2
  exit 2
fi

test "$(git -C /workspace/vllm-plugin-FL rev-parse HEAD)" = \
  "13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0"
test "$(git -C /workspace/FlagGems rev-parse HEAD)" = \
  "4df52d9168ac55c1c1061cefb4638c570292d896"

echo "ready_for_experiment"
echo "device_free_mib=$free_mem"
