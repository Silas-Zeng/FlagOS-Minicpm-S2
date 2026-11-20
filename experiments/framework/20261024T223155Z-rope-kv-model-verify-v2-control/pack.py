"""封存v2模型门，不执行任何设备操作；生产source.tar独立传输。"""
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

root=Path(__file__).resolve().parent
candidate=root.parent/'rope-kv-model-candidate-v2'
for name in ('cache-cpu-check.json','cache-migration.json'):
    shutil.copyfile(candidate/name,root/name)
names=['verify_service.py','graph_gate.py','rope_graph.py','cache_gate.py','qualification.py','lifecycle.py',
       'base-source-manifest.json','source-manifest.json','source-sha256.json','check_graph_cpu.py',
       'graph-replay-cpu.json','binding-cpu.json','cache-cpu-check.json','cache-migration.json',
       'prepare_binding.py','README.md','pack.py']
pins={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names}
(root/'asset-pins.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
with tarfile.open(root/'assets.tar.gz','w:gz') as archive:
    for name in names+['asset-pins.json']:archive.add(root/name,arcname=name)
digest=hashlib.sha256((root/'assets.tar.gz').read_bytes()).hexdigest()
receipt={'archive':'assets.tar.gz','sha256':digest,'asset_count':len(pins),'device_run':False,
         'source_archive_sha256':json.loads((root/'source-manifest.json').read_bytes())['archive_sha256']}
(root/'package-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
