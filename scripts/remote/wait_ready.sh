#!/usr/bin/env bash
set -euo pipefail

TIMEOUT_SECONDS=${1:-900}
deadline=$((SECONDS + TIMEOUT_SECONDS))

while (( SECONDS < deadline )); do
  if curl -fsS --max-time 3 http://127.0.0.1:9031/v1/models \
    >/tmp/minicpm-models.json 2>/tmp/minicpm-models.err; then
    cat /tmp/minicpm-models.json
    exit 0
  fi
  sleep 5
done

echo "Timed out waiting for vLLM on port 9031" >&2
exit 1
