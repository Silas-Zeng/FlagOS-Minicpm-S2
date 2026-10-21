#!/usr/bin/env bash
# 四形状真实 Attention 正确性门；不加载模型权重，不计性能。
set -euo pipefail
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-mapped-decode-sme-fix-gate"
control="$run-control"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root/scripts" "$control" <<'PY'
from pathlib import Path
import hashlib,json,sys
base,control=map(Path,sys.argv[1:])
pins={
'validate_mapped_decode_sme_fix.py':'ede4519424d467bb4f47f52cb57429c5e489ee2324070c482225cc0499b0dc2f',
'biv150_mapped_decode.py':'d085ad6dcc0fd5dc26188d3e0f5801b8e394dc07a79c05a376192ec9e1e95b4b',
'biv150_mapped_decode_source.py':'919e80abf5b95c55ea63aa8619fa3202cd78b0c4cc0e303df7b4197bf1898316',
'biv150_mapped_attention.py':'72713a90584bc6567706fb881188afa04335230afc13e021c10f862f88d054a1',
'validate_hidden_row_gather.py':'65cb8affd4ae08af877ccb4b4cfca6822eec5ba3f83770f39999ee677c546863',
'validate_mixed_decode.py':'b6275ee86f4fb24824091e72fccd774d174247975f8189d360400f333a20351f',
'bench_attention_dispatch.py':'c52caaae1b693f80dacca20473d8177c766fab5941289084f3131a52514d3294',
'validate_block_table_candidate.py':'6072137cfb178dd77ebf4fbf9dd5ffc46534a56bbc07cbbc03f603d8ac1cb3b1',
'monitor_gpu.sh':'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a'}
for name,want in pins.items():
    actual=hashlib.sha256((base/name).read_bytes()).hexdigest()
    if actual!=want:raise RuntimeError('reviewed asset mismatch: '+name+' '+actual)
(control/'reviewed-sha256.json').write_text(json.dumps(pins,indent=2)+'\n')
PY
base="$root/code/sql-mixed-20261021T080656Z/vllm_fl/patches"
command=(python3 "$root/scripts/validate_mapped_decode_sme_fix.py" --run-dir "$run" --runtime-path "$base/biv150_decode_launch_runtime.py" --mixed-path "$base/biv150_mixed_decode.py" --policy-path "$root/scripts/biv150_mapped_decode.py" --transform-path "$root/scripts/biv150_mapped_decode_source.py" --derived-path "$root/scripts/biv150_mapped_attention.py")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nRUNNER_PID=%s\n' "$run" "$control" "$runner_pid"
