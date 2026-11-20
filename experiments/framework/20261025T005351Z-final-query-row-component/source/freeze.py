"""封存已审组件资产；不执行模型/设备。"""
import ast
from datetime import datetime,timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parent
names=['README.md','base-source-manifest.json','check_cpu.py','component.py','cpu-check.json',
       'freeze.py','owner.diff','prepare_assets.py','query_candidate.py','run_component.py','source_identity.py']
pins={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
for name in names:
    if name.endswith('.py'):ast.parse((ROOT/name).read_bytes())
cpu=json.loads((ROOT/'cpu-check.json').read_bytes())
assert cpu['passed']==8 and not cpu['gpu_executed']
assert cpu['component_sha256']==pins['component.py'] and cpu['owner_sha256']==pins['run_component.py']
assert cpu['query_candidate_sha256']==pins['query_candidate.py']
(ROOT/'asset-pins.json').write_bytes((json.dumps(pins,ensure_ascii=False,indent=2)+'\n').encode())
payload=io.BytesIO()
with tarfile.open(fileobj=payload,mode='w',format=tarfile.PAX_FORMAT) as tar:
    for name in sorted([*pins,'asset-pins.json']):
        raw=(ROOT/name).read_bytes()
        info=tarfile.TarInfo(name);info.size=len(raw);info.mtime=0;info.mode=0o644
        tar.addfile(info,io.BytesIO(raw))
with (ROOT/'package.tar.gz').open('wb') as output:
    with gzip.GzipFile(filename='',mode='wb',fileobj=output,mtime=0) as compressed:
        compressed.write(payload.getvalue())
raw=(ROOT/'package.tar.gz').read_bytes()
receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),package='package.tar.gz',
    package_sha256=hashlib.sha256(raw).hexdigest(),package_bytes=len(raw),pinned_files=len(pins),
    member_count=len(pins)+1,component_sha256=pins['component.py'],owner_sha256=pins['run_component.py'],
    query_candidate_sha256=pins['query_candidate.py'],cpu_new_checks=8,independent_review='resume新增路径窄审通过；复用原f72生命周期',
    gpu_executed=False)
(ROOT/'package-receipt.json').write_bytes((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(receipt,ensure_ascii=False,indent=2))
