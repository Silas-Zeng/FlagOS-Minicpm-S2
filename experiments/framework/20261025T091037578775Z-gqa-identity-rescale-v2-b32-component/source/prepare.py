"""仅修v2验证器空padding切片；原包与失败证据保持不动。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "gqa-identity-rescale-v2-20261025"


def prepare():
    pins = json.loads((BASE / "asset-pins.json").read_text())
    for name, expected in pins.items():
        if hashlib.sha256((BASE / name).read_bytes()).hexdigest() != expected:
            raise ValueError("冻结v2资产变化：" + name)
        if name not in ("prepare.py", "README.md", "check_cpu.py", "cpu-check.json", "worker.diff"):
            shutil.copyfile(BASE / name, HERE / name)
    old = (BASE / "worker.py").read_text(encoding="utf8")
    before = '''            checks["padded_output_zero"] = all(bool((arm.out[active:B] == 0).all()) for arm in arms.values())
            checks["padded_partials_untouched"] = all(bool((t[active:B] == -17).all())
                for arm in arms.values() for t in (arm.partial, arm.maxima, arm.sums))
'''
    after = '''            if active < B:
                checks["padded_output_zero"] = all(bool((arm.out[active:B] == 0).all()) for arm in arms.values())
                checks["padded_partials_untouched"] = all(bool((t[active:B] == -17).all())
                    for arm in arms.values() for t in (arm.partial, arm.maxima, arm.sums))
            else:
                checks["padded_output_zero"] = True
                checks["padded_partials_untouched"] = True
'''
    if old.count(before) != 1:
        raise ValueError("padding检查锚点不唯一")
    new = old.replace(before, after, 1)
    ast.parse(new)
    (HERE / "worker.py").write_bytes(new.encode())
    (HERE / "worker.diff").write_bytes("".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
        fromfile="frozen-v2/worker.py", tofile="empty-padding-fix-v3/worker.py")).encode())


def seal():
    names = sorted(p.name for p in HERE.iterdir() if p.is_file() and p.name not in ("entry.tar.gz", "asset-pins.json"))
    hashes = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}
    (HERE / "asset-pins.json").write_text(json.dumps(hashes, indent=2) + "\n")
    with tarfile.open(HERE / "entry.tar.gz", "w:gz") as tar:
        for name in [*names, "asset-pins.json"]:
            tar.add(HERE / name, arcname=name)
    print(json.dumps(dict(pins=len(names), bytes=(HERE / "entry.tar.gz").stat().st_size,
                         sha256=hashlib.sha256((HERE / "entry.tar.gz").read_bytes()).hexdigest())))


if __name__ == "__main__":
    prepare()
    seal()
