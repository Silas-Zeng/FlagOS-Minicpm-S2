#!/usr/bin/env bash
# root实际验收213134 VERIFY1后才手动调用；每次一侧，无自动pair/新controller。
set -euo pipefail
test "$#" -eq 1
variant=$1
[[ "$variant" == baseline || "$variant" == candidate ]]
root=/workspace/experiments/minicpm-s2
assets=$(cd -- "$(dirname -- "$0")" && pwd)
case "$variant" in
  baseline)
    source_dir="$root/code/q-gqa-service-candidate-20261022T184141Z"
    reference="$root/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long-control"
    marker=BIV150_Q_FRAGMENT_SERVICE_INSTALLED ;;
  candidate)
    source_dir="$root/code/q-gqa-kv-swap-20261022T213134Z"
    reference="$root/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control"
    marker=BIV150_KV_PROTOCOL_INSTALLED ;;
esac
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-q-gqa-kv-swap-verify0-$variant-context16k-long"
control="$run-control"
python3 - "$root" "$assets" <<'PY'
from pathlib import Path
import hashlib, json, socket, subprocess, sys
root, assets = map(Path, sys.argv[1:])
for path,pin in {
    assets/'base-source-sha256.json':'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392',
    assets/'expected-source-sha256.json':'82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
    root/'scripts/run_framework_screen.py':'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
    root/'scripts/snapshot_tuning_db.py':'0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}.items():
    if hashlib.sha256(path.read_bytes()).hexdigest()!=pin:
        raise RuntimeError('冻结输入/driver/DB工具变化: '+str(path))
first = root/'framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long'
if (first/'exit-code').read_text().strip()!='0':
    raise RuntimeError('213134尚未完成；此外仍须root实际验收字节/消费')
post = json.loads((first/'postflight-full.json').read_text())
if (post['source_count']!=422 or post['source_failures'] or post['query'].strip()!='68, 0'
        or not all(post['ports_closed'].values())):
    raise RuntimeError('213134后态尚未收口')
query = subprocess.check_output(['ixsmi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True)
table = subprocess.check_output(['ixsmi'], text=True)
if (query.strip()!='68, 0' or 'No running processes found' not in table
        or 'BI-V150' not in table or '32768MiB' not in table):
    raise RuntimeError('不是空闲单BI-V150/32GiB: '+query)
for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host, 9031))==0:
            raise RuntimeError('9031正在使用: '+host)
PY
mkdir "$control"
cp "$0" "$control/launch.sh"
cp "$assets/base-source-sha256.json" "$assets/expected-source-sha256.json" "$control/"
python3 - "$control" "$source_dir" "$reference" "$variant" <<'PY'
from pathlib import Path
import hashlib, json, shutil, sys
control, source, reference = map(Path, sys.argv[1:4]); variant = sys.argv[4]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def mapping(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(x in ('.git','__pycache__') for x in rel.parts) or path.suffix in ('.pyc','.pyo'):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(folder):
                raise RuntimeError('源含外部/目录链接')
        if path.is_file(): result[rel.as_posix()] = sha(path)
    return result
expected = json.loads((control/('base-source-sha256.json' if variant=='baseline' else 'expected-source-sha256.json')).read_text())
original = json.loads((reference/'source-sha256.json').read_text())
if len(expected)!=(414 if variant=='baseline' else 422) or original!=expected or mapping(source)!=expected:
    raise RuntimeError('完整现有冻结源/原source证据不符')
shutil.copytree(source, control/'plugin-source')
if mapping(control/'plugin-source')!=expected or mapping(source)!=expected:
    raise RuntimeError('源码归档不符或源在归档期间变化')
evidence = control/'original-source-evidence'; evidence.mkdir()
for name in ('source-sha256.json','purpose.json','preparation.json','command.txt'):
    shutil.copyfile(reference/name, evidence/name)
purpose = {'kind':'QGQA414 vs累计原FULL/pitched-SAVE VERIFY0单侧；root验收VERIFY1后手动',
    'variant':variant,'source':str(source),'source_count':len(expected),'reference_control':str(reference),
    'reference_file_sha256':{p.name:sha(p) for p in evidence.iterdir()},'verify_restore':'0',
    'limits':['非profiler/不新增字节回读；不自动pair','需真实协议/消费者/QGQA与DB四端/实际KV可比，不继承accuracy']}
(control/'source-sha256.json').write_text(json.dumps(expected,indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps(purpose,ensure_ascii=False,indent=2)+'\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
mkdir "$control/q-hoist-artifacts"
command=(env -u BIV150_FINITE_GROWTH_ADMISSION
  "BIV150_KV_VERIFY_RESTORE=0"
  "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts"
  python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir"
  --context-long-screen --seed 721201 --require-log-marker "$marker")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nVARIANT=%s\nRUNNER_PID=%s\nVERIFY=0\n' "$run" "$control" "$source_dir" "$variant" "$runner_pid"
