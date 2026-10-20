#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 start|stop|wait" >&2
  exit 2
fi

case "$1" in
  start)
    curl -fsS -X POST http://127.0.0.1:9031/start_profile
    ;;
  stop)
    curl -fsS -X POST http://127.0.0.1:9031/stop_profile
    ;;
  wait)
    deadline=$((SECONDS + 900))
    while (( SECONDS < deadline )); do
      if curl -fsS --max-time 3 http://127.0.0.1:9031/v1/models >/dev/null; then
        exit 0
      fi
      sleep 5
    done
    echo "Profiled service did not become ready" >&2
    exit 1
    ;;
  *)
    echo "unknown action: $1" >&2
    exit 2
    ;;
esac
