#!/usr/bin/env bash
# 只验证冻结422的新组合资格；原35d Math500 Level3 owner/参数/阈值不变。
set -euo pipefail
test "$#" -eq 0
root=/workspace/experiments/minicpm-s2
assets=$(cd -- "$(dirname -- "$0")" && pwd)
source_dir="$root/code/q-gqa-kv-swap-20261022T213134Z"
reference="$root/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control/source-sha256.json"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
run="$root/accuracy/$stamp-q-gqa-kv-swap"
control="$run-control"
python3 - "$source_dir" "$reference" "$assets" "$control" <<'PY'
from pathlib import Path
import hashlib,json,shutil,socket,subprocess,sys
source,reference,assets,control=map(Path,sys.argv[1:])
root=Path('/workspace/experiments/minicpm-s2')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,pin in {
 root/'scripts/run_accuracy_gate.py':'35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54',
 root/'scripts/run_math500_level3.sh':'6e045c1cda5a6379ddff1bf7c41ab1e4cbaaddd51b2ca9b4b1d2a92cfa8bb5f4',
 root/'scripts/snapshot_tuning_db.py':'0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
 assets/'expected-source-sha256.json':'82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
}.items():
 if sha(path)!=pin:raise RuntimeError('原owner/official脚本/完整map变化: '+str(path))
expected=json.loads((assets/'expected-source-sha256.json').read_text())
if len(expected)!=422 or json.loads(reference.read_text())!=expected:
 raise RuntimeError('不是213134已受测422完整源')
def mapping(folder):
 result={}
 for path in sorted(folder.rglob('*')):
  rel=path.relative_to(folder)
  if any(x in ('.git','__pycache__') for x in rel.parts) or path.suffix in ('.pyc','.pyo'):continue
  if path.is_symlink():
   target=path.resolve(strict=True)
   if not target.is_file() or not target.is_relative_to(folder):raise RuntimeError('源含外部/目录链接')
  if path.is_file():result[rel.as_posix()]=sha(path)
 return result
if mapping(source)!=expected:raise RuntimeError('422现有源变化')
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
if query.strip()!='68, 0' or 'No running processes found' not in table:raise RuntimeError('设备未清理')
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
 with socket.socket(family,socket.SOCK_STREAM) as s:
  s.settimeout(1)
  if s.connect_ex((host,9031))==0:raise RuntimeError('9031占用')
control.mkdir(exist_ok=False)
shutil.copyfile(reference,control/'source-sha256.json')
shutil.copyfile(assets/'expected-source-sha256.json',control/'expected-source-sha256.json')
shutil.copytree(source,control/'plugin-source',ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'))
if mapping(control/'plugin-source')!=expected or mapping(source)!=expected:raise RuntimeError('完整源归档不符或源已变化')
(control/'purpose.json').write_text(json.dumps({'kind':'冻结422独立Math500 Level3准确率；未通过状态不得继承旧414',
 'source':str(source),'source_count':422,'reference':str(reference),'reference_sha256':sha(reference),
 'verify_restore':'0','accuracy_state':'not_started','original_owner_sha256':sha(root/'scripts/run_accuracy_gate.py'),
 'limits':['原35d负责锁/DB-beforeafter/评测/阈值/cleanup，不新增controller','安装marker不是实际事务或accuracy通过']},ensure_ascii=False,indent=2)+'\n')
PY
cp "$0" "$control/launch.sh"
mkdir "$control/q-hoist-artifacts"
command=(env -u BIV150_FINITE_GROWTH_ADMISSION
 "BIV150_KV_VERIFY_RESTORE=0"
 "BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=$control/q-hoist-artifacts"
 python3 "$root/scripts/run_accuracy_gate.py" "$run" --source-dir "$source_dir"
 --require-log-marker BIV150_KV_PROTOCOL_INSTALLED
 --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db)
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
sha256sum "$root/scripts/run_accuracy_gate.py" "$root/scripts/run_math500_level3.sh" "$root/scripts/snapshot_tuning_db.py" > "$control/scripts.sha256"
nohup "${command[@]}" > "$control/runner.log" 2>&1 < /dev/null &
runner_pid=$!
printf '%s\n' "$runner_pid" > "$control/runner.pid"
printf 'RUN=%s\nCONTROL=%s\nSOURCE=%s\nRUNNER_PID=%s\nVERIFY=0\n' "$run" "$control" "$source_dir" "$runner_pid"
