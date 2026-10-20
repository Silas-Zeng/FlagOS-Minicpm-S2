#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <pid-file>" >&2
  exit 2
fi

pid_file=$1
if [[ ! -f "$pid_file" ]]; then
  echo "PID file does not exist: $pid_file" >&2
  exit 2
fi

pid=$(cat "$pid_file")
if kill -0 "$pid" 2>/dev/null; then
  kill -TERM "$pid"
fi

for _ in $(seq 1 60); do
  if ! kill -0 "$pid" 2>/dev/null; then
    exit 0
  fi
  sleep 1
done

echo "Service process $pid did not exit after SIGTERM" >&2
exit 1
