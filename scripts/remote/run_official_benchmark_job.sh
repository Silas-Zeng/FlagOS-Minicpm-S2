#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <control-dir>" >&2
  exit 2
fi

CONTROL_DIR=$1
mkdir -p "$CONTROL_DIR"
date -u +%Y-%m-%dT%H:%M:%SZ > "$CONTROL_DIR/started-at"

set +e
bash /workspace/experiments/minicpm-s2/scripts/run_official_benchmark.sh
status=$?
set -e

echo "$status" > "$CONTROL_DIR/exit-code"
date -u +%Y-%m-%dT%H:%M:%SZ > "$CONTROL_DIR/finished-at"
exit "$status"
