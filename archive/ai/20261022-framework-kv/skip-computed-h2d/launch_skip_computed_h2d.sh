#!/usr/bin/env bash
# 仅准备就绪的actual-method短门；现有official结束且严格空闲后由root调用。
set -euo pipefail
test "$#" -eq 0
root=/workspace/experiments/minicpm-s2
base="$root/code/q-gqa-service-candidate-20261022T184141Z"
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-skip-computed-h2d-method"
control="$run-control"
python3 - "$root" "$base" "$assets" <<'PY'
from pathlib import Path
import hashlib,json,socket,subprocess,sys
root,base,assets=map(Path,sys.argv[1:])
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
for name,pin in {
 'prepare_skip_computed_h2d.py':'23d833a1bd3f4155652a2457b19bdaedf29b918de488e18e5b986b2cb5e08427',
 'validate_skip_computed_h2d.py':'461676a0b6517e5c832d315fbcfe18aff059ad0bd23cf14e51da7f34cfe4af42',
 'base-source-sha256.json':'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392',
}.items():
    assert sha(assets/name)==pin,name
assert sha(root/'scripts/validate_block_table_candidate.py')=='6072137cfb178dd77ebf4fbf9dd5ffc46534a56bbc07cbbc03f603d8ac1cb3b1'
expected=json.loads((assets/'base-source-sha256.json').read_text())
actual={p.relative_to(base).as_posix():sha(p) for p in base.rglob('*')
    if p.is_file() and not any(x in ('.git','__pycache__') for x in p.relative_to(base).parts)
    and p.suffix not in ('.pyc','.pyo')}
assert len(actual)==414 and actual==expected, '冻结414源变化'
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
assert query.strip()=='68, 0' and 'No running processes found' in table, '设备占用'
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        assert sock.connect_ex((host,9031))!=0,'9031占用'
PY
mkdir "$control"
cp "$0" "$control/launch.sh"
cp "$assets/base-source-sha256.json" "$control/base-source-sha256.json"
command=(env -u BIV150_FINITE_GROWTH_ADMISSION "PYTHONPATH=$base:$root/scripts"
 python3 "$assets/validate_skip_computed_h2d.py" --run-dir "$run"
 --runner-path "$base/vllm_fl/worker/model_runner.py"
 --runtime-path "$base/vllm_fl/patches/biv150_cpu_metadata.py"
 --async-runtime-path "$base/vllm_fl/patches/biv150_async_token_update.py"
 --transform-path "$assets/prepare_skip_computed_h2d.py")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nRUNNER_PID=%s\n' "$run" "$control" "$runner_pid"
