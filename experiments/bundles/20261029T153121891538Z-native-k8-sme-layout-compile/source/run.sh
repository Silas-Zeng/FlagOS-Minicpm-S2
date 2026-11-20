#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
printf '%q ' python3 probe.py "$@" > build/run-command.txt
printf '\n' >> build/run-command.txt
python3 probe.py "$@" 2>&1 | tee build/run.log
