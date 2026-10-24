"""封存本地入口；不执行设备逻辑，生产源码tar单独按manifest上传。"""
import hashlib
import json
from pathlib import Path
import tarfile

root = Path(__file__).resolve().parent
names = ['verify_service.py', 'graph_gate.py', 'rope_graph.py', 'cache_gate.py',
         'qualification.py', 'lifecycle.py', 'base-source-manifest.json',
         'source-manifest.json', 'source-sha256.json', 'check_cpu.py', 'cpu-check.json', 'README.md', 'pack.py']
pins = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
(root / 'asset-pins.json').write_text(json.dumps(pins, indent=2)+'\n', encoding='utf-8')
with tarfile.open(root / 'assets.tar.gz', 'w:gz') as archive:
    for name in names + ['asset-pins.json']:
        archive.add(root / name, arcname=name)
digest = hashlib.sha256((root / 'assets.tar.gz').read_bytes()).hexdigest()
(root / 'package-receipt.json').write_text(json.dumps({'archive':'assets.tar.gz','sha256':digest,
    'asset_count':len(pins),'device_run':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sha256':digest,'asset_count':len(pins)}))
