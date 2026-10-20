#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <control-dir>" >&2
  exit 2
fi

CONTROL_DIR=$1
case "$CONTROL_DIR" in
  /workspace/experiments/minicpm-s2/*) ;;
  *)
    echo "control directory must be below /workspace/experiments/minicpm-s2" >&2
    exit 2
    ;;
esac

mkdir -p "$CONTROL_DIR"
if [[ -e "$CONTROL_DIR/launcher.pid" ]]; then
  echo "control directory is already used by another run" >&2
  exit 2
fi

setsid bash \
  /workspace/experiments/minicpm-s2/scripts/run_official_benchmark_job.sh \
  "$CONTROL_DIR" \
  > "$CONTROL_DIR/runner.log" 2>&1 < /dev/null &
echo "$!" > "$CONTROL_DIR/launcher.pid"
echo "$CONTROL_DIR"
