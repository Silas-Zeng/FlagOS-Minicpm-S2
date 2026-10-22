#!/usr/bin/env bash
# 冻结SQL+C3基点与两CPU方法组合；只做一轮原参数短筛。
set -euo pipefail

test "$#" -eq 1
variant=$1
[[ "$variant" =~ ^(baseline|combined)$ ]]
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/framework/$stamp-cpu-combination-$variant-decode4k"
control="$run-control"
source_dir="$root/code/cpu-combination-$variant-$stamp"
mkdir "$control"
cp "$0" "$control/launch.sh"
python3 - "$root" "$source_dir" "$control" "$variant" <<'PY'
from pathlib import Path
import sys,hashlib,json,shutil,socket,subprocess
root,source,control=map(Path,sys.argv[1:4]);variant=sys.argv[4]
if variant not in ('baseline','combined'):raise RuntimeError('unsupported variant')
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:
    raise RuntimeError('device occupied: '+query)
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
    with socket.socket(family,socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host,9031))==0:raise RuntimeError('port occupied: '+host)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def file_map(folder):
    files={};aliases={};resolved=folder.resolve()
    for p in sorted(folder.rglob('*')):
        rel=p.relative_to(folder)
        if any(part in ('.git','__pycache__') for part in rel.parts) or p.suffix in ('.pyc','.pyo'):continue
        if p.is_symlink():
            target=p.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(resolved):raise RuntimeError('unsafe source alias: '+str(rel))
            aliases[rel.as_posix()]={'target':str(p.readlink()),'resolved':str(target),'sha256':sha(target)}
        if p.is_file():files[rel.as_posix()]=sha(p)
    return files,aliases
def require_map(actual,expected,label):
    if actual!=expected:
        raise RuntimeError(label+' map differs: '+json.dumps({
            'missing':sorted(set(expected)-set(actual)),
            'added':sorted(set(actual)-set(expected)),
            'changed':sorted(k for k in set(actual)&set(expected) if actual[k]!=expected[k])}))
driver=root/'scripts/run_framework_screen.py'
if sha(driver)!='bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9':raise RuntimeError('driver changed')
base=root/'code/sql-mixed-20261021T080656Z'
reference=root/'scripts/cpu-combination-base-sha256.json'
if reference.is_symlink() or sha(reference)!='cd506fa2ed386df5961a188702a512351829cca59b684f2d47897e57e298c676':raise RuntimeError('base reference changed')
expected=json.loads(reference.read_text(encoding='utf-8'))
if len(expected)!=410 or expected.get('vllm_fl/worker/model_runner.py')!='e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1':raise RuntimeError('unexpected base reference')
base_files,aliases=file_map(base)
require_map(base_files,expected,'base410')
shutil.copyfile(reference,control/'cpu-combination-base-sha256.json')
shutil.copytree(base,source,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
expected=dict(expected)
assets={}
if variant=='combined':
    assets={
        'cpu-combination-model_runner.py':('vllm_fl/worker/model_runner.py','6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141'),
        'biv150_cpu_metadata.py':('vllm_fl/patches/biv150_cpu_metadata.py','0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f'),
        'biv150_async_token_update.py':('vllm_fl/patches/biv150_async_token_update.py','1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc'),
    }
    for name,(destination,digest) in assets.items():
        path=root/'scripts'/name
        if path.is_symlink() or sha(path)!=digest:raise RuntimeError('reviewed source differs: '+name)
        shutil.copyfile(path,source/destination)
        expected[destination]=digest
if len(expected)!=(410 if variant=='baseline' else 412):raise RuntimeError('unexpected source count')
files,_=file_map(source)
require_map(files,expected,'isolated source')
shutil.copytree(source,control/'plugin-source')
archive,_=file_map(control/'plugin-source')
require_map(archive,expected,'archived source')
require_map(file_map(base)[0],base_files,'base after copy')
(control/'source-sha256.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf-8')
(control/'purpose.json').write_text(json.dumps({'kind':'single paired short screening; not official','variant':variant,'base':str(base),'source':str(source),'base_reference_sha256':sha(reference),'base_source_count':410,'expected_source_count':len(expected),'aliases_dereferenced':aliases,'preflight_gpu':query,'ixsmi':table},indent=2)+'\n',encoding='utf-8')
PY
cp "$root/scripts/snapshot_tuning_db.py" "$control/"
python3 "$control/snapshot_tuning_db.py" --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db --output "$control/db-before" > "$control/db-before.log"
command=(python3 "$root/scripts/run_framework_screen.py" "$run" --source-dir "$source_dir" --decode-screen --seed 721201 --require-log-marker BIV150_SQL_REFLECTION_INSTALLED)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\n' "$run" "$control" "$source_dir" "$runner_pid"
