#!/usr/bin/env bash
# 同一启动标量观察器分别附冻结stable/capacity；仅原bc51 smoke，不是性能成绩。
set -euo pipefail
variant=${1:?需要stable或capacity}
case "$variant" in stable|capacity) ;; *) exit 2 ;; esac
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-kv-memory-$variant-smoke"
control="$run-control"
source_dir="$root/code/kv-memory-$variant-$stamp"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$source_dir" "$control" "$variant" <<'PY'
from pathlib import Path
import sys,hashlib,json,shutil,socket,subprocess
root,source,control=map(Path,sys.argv[1:4]);variant=sys.argv[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected={
 'prepare_kv_memory_observer_source.py':'0ab0ce3ab3d8cde4a8e725d9fdfd3e62726fcf95613fbc1e55b850b3e48a9029',
 'prepare_innovation_source.py':'0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca',
 'biv150_kv_memory_observer.py':'6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c',
 'run_framework_screen.py':'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
 'snapshot_tuning_db.py':'0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}
for name,value in expected.items():
    if sha(root/'scripts'/name)!=value:raise RuntimeError('unreviewed/changed asset: '+name)
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('device occupied')
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host,9031))==0:raise RuntimeError('port occupied')
builder=root/'scripts/prepare_kv_memory_observer_source.py'
subprocess.run(['python3',str(builder),'--variant',variant,'--output',str(source)],check=True)
for name in expected:shutil.copyfile(root/'scripts'/name,control/name)
shutil.copytree(source,control/'plugin-source')
(control/'source-sha256.json').write_text(json.dumps({p.relative_to(source).as_posix():sha(p) for p in sorted(source.rglob('*')) if p.is_file()},indent=2)+'\n')
prepared=json.loads((source/'memory-observer-source.json').read_text())
(control/'purpose.json').write_text(json.dumps({'kind':'startup scalar memory observer only; not performance or official score','variant':variant,'source':str(source),'base':prepared['base_source'],'source_builder_sha256':expected['prepare_kv_memory_observer_source.py'],'observer_sha256':expected['biv150_kv_memory_observer.py'],'input_count':len(prepared['input_sha256']),'original_innovation_manifest_preserved_sha256':prepared['original_innovation_manifest_preserved_sha256'],'preflight_gpu':query,'ixsmi':table,'restore_byte_readback_enabled':False,'required_evidence':['actual samePID DETERMINE_RETURN with profile_context_calls 1','complete original worker/profile/snapshot CPU scalars and original int return','PARENT_RETURN samePID original list and all3 restored true','no REJECTED or NOT_ACTIVATED or OBSERVATION_INCOMPLETE','original smoke only command and SERVER unchanged','DB/source/live/post idle original evidence retained'],'limits':['ARMED is not actual observation; missing scalars cannot explain memory difference','no new GPU samples; root original ixsmi/driver sampling remain diagnostics','one startup sample each cannot assign cause to 6 KV blocks or report performance']},indent=2)+'\n')
PY
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
export BIV150_KV_VERIFY_RESTORE=0
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --smoke-only --seed 721201 --require-log-marker '"event": "DETERMINE_RETURN"')
printf 'BIV150_KV_VERIFY_RESTORE=0 ' > "$control/command.txt"
printf '%q ' "${command[@]}" >> "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
