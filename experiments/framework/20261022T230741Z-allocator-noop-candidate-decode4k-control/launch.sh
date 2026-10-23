#!/usr/bin/env bash
# root手动单次423候选；复用原bc51 decode4k owner，对固定225044基线。
set -euo pipefail
test "$#" -eq 0
root=/workspace/experiments/minicpm-s2
base_dir="$root/code/q-gqa-kv-swap-20261022T213134Z"
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-allocator-noop-candidate-decode4k"
control="$run-control"
source_dir="$root/code/allocator-noop-candidate-$stamp"
python3 - "$root" "$assets" <<'PY'
from pathlib import Path
import hashlib, socket, subprocess, sys
root, assets = map(Path, sys.argv[1:])
for path,pin in {
    assets/'prepare_source.py':'a8264488f522c88da237eeee7d9f9c216b6a50b73374921e411db2495e62e7d9',
    assets/'base-source-sha256.json':'82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
    assets/'expected-source-sha256.json':'beb748fc30842d2ba378bcb0e526dfff0ba6e02f9ec4acf8986d8f2e7421ac5d',
    root/'scripts/run_framework_screen.py':'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
    root/'scripts/snapshot_tuning_db.py':'0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}.items():
    if hashlib.sha256(path.read_bytes()).hexdigest()!=pin:
        raise RuntimeError('冻结接线资产变化: '+str(path))
query = subprocess.check_output(['ixsmi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True)
table = subprocess.check_output(['ixsmi'], text=True)
if (query.strip() != '68, 0' or 'No running processes found' not in table
        or 'BI-V150' not in table or '32768MiB' not in table):
    raise RuntimeError('不是空闲单BI-V150/32GiB: ' + query)
for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host, 9031)) == 0:
            raise RuntimeError('9031正在使用: ' + host)
PY
mkdir "$control"
cp "$0" "$control/launch.sh"
cp "$assets/prepare_source.py" "$assets/base-source-sha256.json" "$assets/expected-source-sha256.json" "$control/"
for name in biv150_noop_allocate.py init-footer.py cpu-tested-core.py cpu-check.json; do
  cp "$assets/$name" "$control/"
done
python3 "$control/prepare_source.py" --output-dir "$source_dir" > "$control/preparation.log"
cp "$source_dir-preparation.json" "$control/preparation.json"
python3 - "$control" <<'PY'
import json, shutil, sys
from pathlib import Path
control = Path(sys.argv[1])
receipt = json.loads((control/'preparation.json').read_text())
(control/'purpose.json').write_text(json.dumps(receipt, indent=2) + '\n')
(control/'source-sha256.json').write_text(json.dumps(receipt['source_sha256'], indent=2) + '\n')
shutil.copytree(receipt['source'], control/'plugin-source')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
# baseline已由root完成；仅核本轮三端DB稳定，不恢复或重置数据库。
python3 - "$root" "$control" <<'PY'
import json, sys
from pathlib import Path
root, control = map(Path, sys.argv[1:])
base=root/'framework/20261022T225044Z-allocator-noop-baseline-decode4k'
post=json.loads((base/'postflight-full.json').read_text())
if ((base/'exit-code').read_text().strip()!='0' or post['source_count']!=422
        or post['source_failures'] or post['query'].strip()!='68, 0'
        or not all(post['ports_closed'].values())):
    raise RuntimeError('225044原422基线未完整完成')
paths=[base.with_name(base.name+'-control')/p/'manifest.json' for p in ('db-before','db-after')]
paths.append(control/'db-before/manifest.json')
snapshots=[json.loads(p.read_text()) for p in paths]
keys=('snapshot_sha256','schema_sha256','logical_content_sha256')
values=[{k:v[k] for k in keys} for v in snapshots]
if any(v.get('status')!='complete' for v in snapshots) or not values[0]==values[1]==values[2]:
    raise RuntimeError('baseline前后与candidate before DB三SHA失配，不启动')
(control/'common-db-check.json').write_text(json.dumps({'baseline_run':base.name,
    'three_sha256':values[0],'candidate_after_still_required':True},indent=2)+'\n')
PY
mkdir "$control/q-hoist-artifacts"
command=(env -u BIV150_FINITE_GROWTH_ADMISSION
  "BIV150_KV_VERIFY_RESTORE=0"
  "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts"
  python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir"
  --decode-screen --seed 721201 --require-log-marker BIV150_KV_PROTOCOL_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\nVERIFY=0\n' "$run" "$control" "$source_dir" "$runner_pid"
