from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,time,urllib.request
control=Path('/workspace/experiments/minicpm-s2/official/20261022T202736Z-q-gqa-framework-official-control')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
rawfile=control/('metrics-observation-'+stamp+'.txt')
receipt=control/('metrics-observation-'+stamp+'.json')
begin=datetime.now(timezone.utc).isoformat()
tick=time.perf_counter()
with urllib.request.urlopen('http://127.0.0.1:9031/metrics',timeout=10) as response:
 raw=response.read(); status=response.status
elapsed=time.perf_counter()-tick
data={'kind':'one read-only existing Prometheus metrics request; no model or source change',
 'started_utc':begin,'finished_utc':datetime.now(timezone.utc).isoformat(),
 'request_seconds':elapsed,'status':status,'raw_file':str(rawfile),
 'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),
 'limits':['累计值含此前4K与当前16K，不能直接归某一轮；非GPU profiler。','官方运行期间多此一次只读HTTP观测，保留时间和原文。']}
with rawfile.open('xb') as out:out.write(raw)
with receipt.open('x') as out:json.dump(data,out,ensure_ascii=False,indent=2);out.write('\n')
lines=[s for s in raw.decode().splitlines() if not s.startswith('#') and any(k in s for k in ('num_preemptions','request_success_total','num_requests_running','num_requests_waiting'))]
print(json.dumps({'observation':data,'selected_lines':lines},ensure_ascii=False))
