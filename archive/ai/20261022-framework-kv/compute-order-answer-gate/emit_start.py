"""root单SSH发送冻结辅助门并启动一侧；不自动排另一侧。"""
import base64, hashlib, json, sys
from pathlib import Path
here=Path(__file__).resolve().parent
variant=sys.argv[1]
assert variant in ('baseline','candidate')
pins=json.loads((here/'static-check.json').read_text())['sha256']
payload={}
for name in ('launch_answer_gate.py','run_answer_gate.py','run_answer_load.py','prepare_requests.py'):
    raw=(here/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==pins[name]
    payload[name]={'sha256':pins[name],'data':base64.b64encode(raw).decode()}
print('import base64,hashlib,json,subprocess\nfrom pathlib import Path')
print('payload=json.loads(base64.b64decode('+repr(base64.b64encode(json.dumps(payload).encode()).decode())+'))')
print('variant='+repr(variant))
print("""
assets=Path('/workspace/experiments/minicpm-s2/scripts/compute-order-answer-gate-20261023')
assets.mkdir(exist_ok=True)
for name,item in payload.items():
    assert Path(name).name==name
    raw=base64.b64decode(item['data']);assert hashlib.sha256(raw).hexdigest()==item['sha256']
    path=assets/name
    if path.exists():assert not path.is_symlink() and path.read_bytes()==raw
    else:
        with path.open('xb') as stream:stream.write(raw)
requests=Path('/workspace/experiments/minicpm-s2/diagnostic-inputs/compute-order-answer-20261023T065931Z/requests.jsonl')
assert hashlib.sha256(requests.read_bytes()).hexdigest()=='b35be1461b5af29ffe90f6300e0084ca5de015549ed00fcbdd960e07eaf4e497'
subprocess.run(['python3',str(assets/'launch_answer_gate.py'),variant,'--requests',str(requests)],check=True)
""")
