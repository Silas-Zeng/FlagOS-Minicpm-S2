"""冻结本组件资产，不导入加速器。"""
import ast
import hashlib
import json
from pathlib import Path
import tarfile
HERE = Path(__file__).resolve().parent
for file in HERE.glob("*.py"):
    ast.parse(file.read_text(encoding="utf-8"), filename=file.name)
names = sorted(p.name for p in HERE.iterdir() if p.is_file()
    and p.name not in ("asset-pins.json", "entry.tar.gz", "package-receipt.json"))
hashes = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}
(HERE / "asset-pins.json").write_bytes((json.dumps(hashes, indent=2)+"\n").encode())
with tarfile.open(HERE / "entry.tar.gz", "w:gz") as tar:
    for n in [*names, "asset-pins.json"]:
        tar.add(HERE / n, arcname=n)
with tarfile.open(HERE / "entry.tar.gz", "r:gz") as tar:
    for n, expected in hashes.items():
        assert hashlib.sha256(tar.extractfile(n).read()).hexdigest() == expected
rec = dict(sha256=hashlib.sha256((HERE / "entry.tar.gz").read_bytes()).hexdigest(),
    bytes=(HERE / "entry.tar.gz").stat().st_size, pins=len(hashes),
    worker=hashes["worker.py"], prototype=hashes["prototype.py"], candidate=hashes["candidate.kernel.py"])
(HERE / "package-receipt.json").write_bytes((json.dumps(rec, indent=2)+"\n").encode())
print(json.dumps(rec))
