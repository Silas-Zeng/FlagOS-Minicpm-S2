#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <server.pid>" >&2
  exit 2
fi

pid_file=$1
root=/workspace/experiments/minicpm-s2
if [[ "$pid_file" != "$root"/* || ! -f "$pid_file" ]]; then
  echo "refusing to use a pid file outside $root: $pid_file" >&2
  exit 2
fi

pid=$(tr -d '[:space:]' < "$pid_file")
if [[ ! "$pid" =~ ^[0-9]+$ ]]; then
  echo "invalid pid file: $pid_file" >&2
  exit 2
fi

if ! kill -0 "$pid" 2>/dev/null; then
  echo "process $pid is already stopped"
  exit 0
fi

command_line=$(tr '\0' ' ' < "/proc/$pid/cmdline")
if [[ "$command_line" != *"vllm serve /workspace/MiniCPM5-2B"* ]]; then
  echo "refusing to stop pid $pid because it is not the managed vLLM server" >&2
  exit 2
fi

kill -TERM "$pid"
for _ in $(seq 1 60); do
  process_state=$(awk '/^State:/{print $2}' "/proc/$pid/status" 2>/dev/null || true)
  if ! kill -0 "$pid" 2>/dev/null || [[ "$process_state" == "Z" ]]; then
    echo "stopped process $pid"
    exit 0
  fi
  sleep 1
done

echo "process $pid did not stop after SIGTERM" >&2
exit 1
