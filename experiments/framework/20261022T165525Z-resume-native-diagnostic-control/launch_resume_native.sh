#!/usr/bin/env bash
set -euo pipefail
root=/workspace/experiments/minicpm-s2
assets=$(cd -- "$(dirname -- "$0")" && pwd)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-resume-native-diagnostic"
control="$run-control"
source_dir="$root/code/resume-native-$stamp"
base="$root/code/cpu-combination-combined-20261022T100830Z"
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
cp "$assets/resume_native_footer.py" "$assets/prepare_resume_native.py" "$assets/run_resume_native_screen.py" "$assets/launch_resume_native.sh" "$assets/base-source-sha256.json" "$control/"
python3 "$control/prepare_resume_native.py" --base-dir "$base" --output-dir "$source_dir" > "$control/preparation.log"
cp "$source_dir-preparation.json" "$control/preparation.json"
python3 - "$root" "$control" "$source_dir" <<'PY'
from pathlib import Path
import json,shutil,sys,hashlib
root,control,source=map(Path,sys.argv[1:])
m=json.loads((control/'preparation.json').read_text())
reference=json.loads((root/'framework/20261022T100830Z-cpu-combination-combined-decode4k-control/source-sha256.json').read_text())
assert len(reference)==412 and m['base_source_sha256']==reference
shutil.copytree(source,control/'plugin-source')
for rel,sha in m['source_sha256'].items():
 assert hashlib.sha256((control/'plugin-source'/rel).read_bytes()).hexdigest()==sha,rel
(control/'source-sha256.json').write_text(json.dumps(m['source_sha256'],indent=2)+'\n')
(control/'purpose.json').write_text(json.dumps({'kind':'current 6f resume GPU diagnostic; not performance baseline','source':str(source),'base_source_count':412,'changed_paths':m['changed_paths']},indent=2)+'\n')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(python3 "$control/run_resume_native_screen.py" "$run" --source-dir "$source_dir" --context-long-screen --native-profile --seed 721201 --require-log-marker BIV150_RESUME_NATIVE_ARMED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
