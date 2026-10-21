#!/usr/bin/env bash
# 42层16K KV连续页合并复制成本门；不加载模型、不接调度器。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-kv-page-copy-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root/scripts" "$control" <<'PY'
from pathlib import Path
import hashlib,json,sys
base,control=map(Path,sys.argv[1:])
pins={'validate_kv_page_copy.py':'d841a1abbfee94a68fddc1afec8bd236b91e2831102217577fa90bd03605f8a3',
'biv150_kv_page_copy.py':'c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c',
'validate_block_table_candidate.py':'6072137cfb178dd77ebf4fbf9dd5ffc46534a56bbc07cbbc03f603d8ac1cb3b1',
'monitor_gpu.sh':'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a'}
for name,want in pins.items():
    if hashlib.sha256((base/name).read_bytes()).hexdigest()!=want:raise RuntimeError('reviewed asset mismatch: '+name)
(control/'reviewed-sha256.json').write_text(json.dumps(pins,indent=2)+'\n')
PY
command=(python3 "$root/scripts/validate_kv_page_copy.py" --run-dir "$run" --copy-path "$root/scripts/biv150_kv_page_copy.py" --source-evidence "$root/source-audits/20261021T184108Z-kv-copy")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nRUNNER_PID=%s\n' "$run" "$control" "$runner_pid"
