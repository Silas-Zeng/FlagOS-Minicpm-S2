#!/usr/bin/env bash
set -euo pipefail
root=/workspace/experiments/minicpm-s2
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-q-gqa-puredecode-native-diagnostic"
control="$run-control"
source_dir="$root/code/q-gqa-puredecode-native-$stamp"
base="$root/code/q-gqa-kv-swap-20261022T213134Z"
python3 - <<'PY'
import socket,subprocess
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
assert query.strip()=='68, 0' and 'No running processes found' in table,table
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
 with socket.socket(family,socket.SOCK_STREAM) as s:
  s.settimeout(1);assert s.connect_ex((host,9031)) != 0,host
print(query)
PY
mkdir "$control"
cp "$assets/biv150_puredecode_native.py" "$assets/init-footer.py" "$assets/prepare_puredecode_native.py" "$assets/run_puredecode_native_screen.py" "$assets/launch_puredecode_native.sh" "$assets/base-source-sha256.json" "$control/"
python3 "$control/prepare_puredecode_native.py" --base-dir "$base" --output-dir "$source_dir" > "$control/preparation.log"
cp "$source_dir-preparation.json" "$control/preparation.json"
python3 - "$root" "$control" "$source_dir" <<'PY'
from pathlib import Path
import json,shutil,sys,hashlib
root,control,source=map(Path,sys.argv[1:])
m=json.loads((control/'preparation.json').read_text())
reference=json.loads((root/'framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control/source-sha256.json').read_text())
assert len(reference)==422 and m['base_source_sha256']==reference
shutil.copytree(source,control/'plugin-source')
for rel,sha in m['source_sha256'].items():
 assert hashlib.sha256((control/'plugin-source'/rel).read_bytes()).hexdigest()==sha,rel
(control/'source-sha256.json').write_text(json.dumps(m['source_sha256'],indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'current QGQA+KV422 puredecode GPU diagnostic; not performance baseline','source':str(source),'base_source_count':422,'changed_paths':m['changed_paths']},indent=2)+'\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
mkdir "$control/q-hoist-artifacts"
command=(env -u BIV150_FINITE_GROWTH_ADMISSION "BIV150_KV_VERIFY_RESTORE=0" "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts" python3 "$control/run_puredecode_native_screen.py" "$run" --source-dir "$source_dir" --context-long-screen --native-profile --seed 721201 --require-log-marker BIV150_PUREDECODE_NATIVE_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
