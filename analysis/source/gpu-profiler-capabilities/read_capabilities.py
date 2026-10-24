from pathlib import Path
import subprocess,json,hashlib
remote = '''import subprocess,json,datetime,socket
from pathlib import Path
root=Path('/usr/local/corex-4.5.0/bin')
query=subprocess.run(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=8)
ports=[]
for port in (9031,9032):
 s=socket.socket(); s.settimeout(.2); ports.append(dict(port=port,open=s.connect_ex(('127.0.0.1',port))==0)); s.close()
out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),gpu=query.stdout,ports=ports,binaries=[p.name for p in root.iterdir() if any(x in p.name.lower() for x in ('prof','sys','ncu','perf'))],commands=[])
if query.returncode==0 and query.stdout.strip()=='68, 0' and not any(p['open'] for p in ports):
 for args in ([str(root/'ixsys'),'--gpu-metrics-device','help'],[str(root/'ixsys'),'--gpu-metrics-set','help']):
  try:
   r=subprocess.run(args,capture_output=True,text=True,timeout=12)
   out['commands'].append(dict(args=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  except subprocess.TimeoutExpired:
   out['commands'].append(dict(args=args,status='help_timeout'))
else: out['skipped']='device not in known idle state; inventory only'
print(json.dumps(out))
'''
args=['ssh','-F','NUL','-i','C:/Users/Administrator/.ssh/id_ed25519_flagos_s2','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12','-p','2224','lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io','python3 -']
r=subprocess.run(args,input=remote.encode(),capture_output=True,check=True,timeout=45)
d=json.loads(r.stdout)
out=Path('analysis/source/gpu-profiler-capabilities');out.mkdir(exist_ok=True)
(out/'read_capabilities.py').write_bytes(Path(__file__).read_bytes())
(out/'capabilities.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
