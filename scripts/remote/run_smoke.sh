#!/usr/bin/env bash
set -euo pipefail

curl -fsS --max-time 300 \
  -H 'Content-Type: application/json' \
  -d '{"model":"minicpm","messages":[{"role":"user","content":"introduce llm"}],"max_tokens":256}' \
  http://127.0.0.1:9031/v1/chat/completions \
  | tee /workspace/experiments/minicpm-s2/baseline/smoke.json
