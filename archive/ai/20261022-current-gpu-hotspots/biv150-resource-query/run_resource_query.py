from pathlib import Path
import base64, hashlib, subprocess, sys

source=Path('tmp/current-biv150-sdk-source/query_biv150_resources.cpp').read_bytes()
assert hashlib.sha256(source).hexdigest()=='57326c2e1f2298654c3c0fa7fffbe2e5597dc6658775499c1f49262220a72e4b'
script=r'''set -euo pipefail
root=/workspace/experiments/minicpm-s2
exec 9>"$root/framework-device.lock"
flock -n 9
stamp=$(date -u +%Y%m%dT%H%M%SZ)
name="$stamp-biv150-resource-query"
run="$root/framework/$name"
mkdir "$run"
printf '%s\n' "$$" > "$run/owner.pid"
date -u +%FT%TZ > "$run/started-at.txt"
check_idle() {
python3 - "$run/$1.json" <<'PY'
import json,socket,subprocess,sys,datetime
query=subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
table=subprocess.check_output(['ixsmi'],text=True)
ports={}
for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
 with socket.socket(family) as sock:
  sock.settimeout(2);ports[host]=sock.connect_ex((host,9031))!=0
with open(sys.argv[1],'x') as f:json.dump(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),query=query,ixsmi=table,ports_closed=ports),f,indent=2)
assert query.strip()=='68, 0' and 'No running processes found' in table and all(ports.values())
PY
}
check_idle before
printf '%s' '__SOURCE__' | base64 -d > "$run/query_biv150_resources.cpp"
command=(g++ -std=c++17 -O2 -I/usr/local/corex-4.5.0/include "$run/query_biv150_resources.cpp" -ldl -o "$run/query_biv150_resources")
printf '%q ' "${command[@]}" > "$run/compile-command.txt"
g++ --version > "$run/compiler-version.txt"
sha256sum /usr/local/corex/include/IX/mapping_cudart.h /usr/local/corex/include/IX/ixrt/ix.h /usr/local/corex/include/IX/ixrt/driver_types.h /usr/local/corex/include/IX/ixrt/ix_runtime_api.h > "$run/sdk-sha256.txt"
set +e
"${command[@]}" > "$run/compile.stdout" 2> "$run/compile.stderr"
compile_rc=$?
printf '%s\n' "$compile_rc" > "$run/compile-exit-code"
rc=$compile_rc
if [ "$compile_rc" -eq 0 ]; then
 printf '%q\n' "$run/query_biv150_resources" > "$run/run-command.txt"
 "$run/query_biv150_resources" > "$run/resources.json" 2> "$run/query.stderr"
 rc=$?
fi
set -e
printf '%s\n' "$rc" > "$run/exit-code"
check_idle after
date -u +%FT%TZ > "$run/finished-at.txt"
python3 - "$run" <<'PY'
import hashlib,json,sys,tarfile
from pathlib import Path
p=Path(sys.argv[1]);files={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(p.iterdir()) if x.is_file()}
(p/'seal.json').write_text(json.dumps({'files':files},indent=2)+'\n')
a=p.with_suffix('.tgz')
assert not a.exists()
with tarfile.open(a,'w:gz') as t:t.add(p,arcname=p.name)
print(json.dumps({'run':str(p),'archive':str(a),'sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'bytes':a.stat().st_size,'files':len(files)}))
if (p/'resources.json').exists():print((p/'resources.json').read_text())
else:print((p/'compile.stderr').read_text())
PY
exit "$rc"
'''.replace('__SOURCE__',base64.b64encode(source).decode())
args=['ssh','-F','NUL','-i','C:/Users/Administrator/.ssh/id_ed25519_flagos_s2','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','-p','2224','lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io','bash']
r=subprocess.run(args,input=script.encode(),capture_output=True,timeout=80)
sys.stdout.buffer.write(r.stdout);sys.stderr.buffer.write(r.stderr)
raise SystemExit(r.returncode)
