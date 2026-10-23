#!/usr/bin/env bash
# 已通过103/105准确率的原KV422；复用原官方owner，两负载×4，仅绝对吞吐/压力观察。
set -euo pipefail
test "$#" -eq 0
root=/workspace/experiments/minicpm-s2
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/official/$stamp-q-gqa-kv-swap-official"
control="$run-control"
source_dir="$root/code/q-gqa-kv-swap-20261022T213134Z"
python3 - "$root" "$source_dir" "$assets" <<'PY'
from pathlib import Path
import hashlib,json,socket,subprocess,sys
root,source,assets=map(Path,sys.argv[1:])
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
expected={
 'run_official_gate.py':'79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579',
 'run_accuracy_gate.py':'35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54',
 'snapshot_tuning_db.py':'0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}
for name,pin in expected.items():
    assert sha(root/'scripts'/name)==pin, name
assert sha(Path('/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py'))=='0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565'
assert sha(assets/'base-source-sha256.json')=='82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
reference=json.loads((assets/'base-source-sha256.json').read_text())
actual={p.relative_to(source).as_posix():sha(p) for p in source.rglob('*')
    if p.is_file() and not any(x in ('.git','__pycache__') for x in p.relative_to(source).parts)
    and p.suffix not in ('.pyc','.pyo')}
assert len(reference)==422 and actual==reference, '完整冻结422源码变化'
assert 'vllm_fl/patches/biv150_finite_growth_admission.py' not in actual
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
assert query.strip()=='68, 0' and 'No running processes found' in table, '设备占用'
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        assert sock.connect_ex((host,9031))!=0, '9031占用'
PY
mkdir "$control" "$control/q-hoist-artifacts"
cp "$0" "$control/launch.sh"
cp "$assets/base-source-sha256.json" "$control/source-sha256.json"
python3 - "$source_dir" "$control" <<'PY'
from pathlib import Path
import hashlib,json,shutil,sys
source,control=map(Path,sys.argv[1:])
reference=json.loads((control/'source-sha256.json').read_text())
shutil.copytree(source,control/'plugin-source',ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
for folder in (source,control/'plugin-source'):
    actual={p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*')
        if p.is_file() and not any(x in ('.git','__pycache__') for x in p.relative_to(folder).parts)
        and p.suffix not in ('.pyc','.pyo')}
    assert actual==reference, '复制中源或完整副本变化'
with (control/'purpose.json').open('x',encoding='utf-8') as stream:
    json.dump({'kind':'当前QGQA+原swap422的原官方完整性能，非finite/allocator/425/单H2D候选，非profiler',
        'source':str(source),'source_count':422,'accuracy_run':'20261022T215836Z-q-gqa-kv-swap',
        'require_actual_after_completion':['Q/GQA同Engine真实成功execute','原八行CSV及第2–4轮均值',
            '完整源前后不变及原driver清理','DB前后原件/全程原协议事件；禁止以不同DB的414官方算因果增益'],
        'limits':['仅报告该候选绝对表现；安装标记不是实际执行或全路径覆盖。']},stream,ensure_ascii=False,indent=2)
    stream.write('\n')
PY
command=(env -u BIV150_FINITE_GROWTH_ADMISSION "BIV150_KV_VERIFY_RESTORE=0" "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts"
 python3 "$root/scripts/run_official_gate.py" "$run" --source-dir "$source_dir"
 --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db
 --require-log-marker BIV150_KV_PROTOCOL_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$root/scripts/run_official_gate.py" "$root/scripts/run_accuracy_gate.py" "$root/scripts/run_math500_level3.sh" "$root/scripts/snapshot_tuning_db.py" "$root/scripts/monitor_gpu.sh" /workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
