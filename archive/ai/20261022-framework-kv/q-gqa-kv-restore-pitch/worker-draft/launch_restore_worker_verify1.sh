#!/usr/bin/env bash
# 仅由root在独立单层门实际PASS后手动调用；不自动pair或编译SO。
set -euo pipefail
test "$#" -eq 1
gate_dir=$1
test "${gate_dir:0:1}" = /
root=/workspace/experiments/minicpm-s2
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-q-gqa-kv-restore-pitched-verify1-context16k-long"
control="$run-control"
source_dir="$root/code/q-gqa-kv-restore-pitched-$stamp"
python3 - "$root" "$assets" <<'PY'
from pathlib import Path
import hashlib, socket, subprocess, sys
root, assets = map(Path, sys.argv[1:])
for path,pin in {
    assets/'prepare_restore_worker_source.py':'f29f23e7de55d4acbacc7ee87e364e1c9f3ab32b002a8808b1c44b9a3495937a',
    assets/'base-source-sha256.json':'82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
    assets/'biv150_kv_pitched_restore_worker.py':'9f178a70b48cf19e97d32f7b9bea26195f7e447b593be9784659916d36120475',
    root/'scripts/run_framework_screen.py':'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
    root/'scripts/snapshot_tuning_db.py':'0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}.items():
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=pin:
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
cp "$assets/prepare_restore_worker_source.py" "$assets/base-source-sha256.json" "$assets/biv150_kv_pitched_restore_worker.py" "$control/"
python3 "$control/prepare_restore_worker_source.py" --gate-dir "$gate_dir" --output-dir "$source_dir" > "$control/preparation.log"
cp "$source_dir-preparation.json" "$control/preparation.json"
python3 - "$control" "$gate_dir" <<'PY'
import json, shutil, sys
from pathlib import Path
control, gate = map(Path, sys.argv[1:])
receipt = json.loads((control/'preparation.json').read_text())
(control/'purpose.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
(control/'source-sha256.json').write_text(json.dumps(receipt['source_sha256'], indent=2) + '\n')
shutil.copytree(receipt['source'], control/'plugin-source')
# 小份原门身份附证；完整原件仍以receipt中原gate/control完整seal为准。
proof = control/'passed-H2D-gate'
proof.mkdir()
for name in ('results.json', 'manifest.json', 'exit-code'):
    shutil.copyfile(gate/name, proof/name)
for name in ('seal.json', 'source-sha256.json', 'source-post-sha256.json', 'compile-input-identity.json'):
    shutil.copyfile(gate.with_name(gate.name+'-control')/name, proof/('control-'+name))
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
mkdir "$control/q-hoist-artifacts"
command=(env -u BIV150_FINITE_GROWTH_ADMISSION
  "BIV150_KV_VERIFY_RESTORE=1"
  "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts"
  python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir"
  --context-long-screen --seed 721201 --require-log-marker BIV150_KV_PROTOCOL_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\nVERIFY=1\n' "$run" "$control" "$source_dir" "$runner_pid"
