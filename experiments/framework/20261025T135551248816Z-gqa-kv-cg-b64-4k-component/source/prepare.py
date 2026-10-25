"""仅新增原 cg 的官方短场景组件形状，保留此前冻结包。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "gqa-kv-cg-20261025"
INHERITED = ("legacy_gate.py", "validate_hidden_row_gather.py", "validate_mixed_decode.py",
             "validate_block_table_candidate.py", "monitor_gpu.sh", "distributed_bootstrap.py",
             "dispatch_bootstrap.py", "source_identity.py", "base-source-manifest.json",
             "base-source-sha256.json", "padding-source.json", "baseline.py", "candidate.py", "cache_policy.py", "kernel.diff")


def once(text, before, after):
    assert text.count(before) == 1, before[:120]
    return text.replace(before, after, 1)


def prepare():
    pins = json.loads((BASE / "asset-pins.json").read_text())
    for name in (*INHERITED, "worker.py", "entry.py"):
        assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == pins[name], name
    for name in INHERITED:
        shutil.copyfile(BASE / name, HERE / name)
    old_worker = (BASE / "worker.py").read_text(encoding="utf8")
    worker = once(old_worker, 'def worker(run, model, shape="hotspot"):', 'def worker(run, model, shape="b64-4k"):')
    worker = once(worker, '默认 N33/bucket40/S16，可显式选择原 B32/S4；split 由实际生产路由选择',
                  '默认 B64/S2、KV4096；原长场景入口保留但不自动运行，split 由实际生产路由选择')
    worker = once(worker, '''        elif shape == "b32":
            B, active, segments = 32, 32, 4
''', '''        elif shape == "b32":
            B, active, segments = 32, 32, 4
        elif shape == "b64-4k":
            B, active, segments = 64, 64, 2
''')
    worker = once(worker, '        L = 16384\n', '        L = 4096 if shape == "b64-4k" else 16384\n')
    worker = once(worker, '        common.block_table_tensor = table.cuda()\n', '''        common.block_table_tensor = table.cuda()
        if shape == "b64-4k":
            # Full active bucket still reserves the runner's null physical page.
            cache = torch.cat((torch.zeros_like(cache[:1]), cache), dim=0)
            common.block_table_tensor[:, :L // 16].add_(1)
            common.slot_mapping.add_(16)
''')
    worker = once(worker, '        if active < B and not bool((cache[0] == 0).all()):',
                  '        if (active < B or shape == "b64-4k") and not bool((cache[0] == 0).all()):')
    worker = once(worker, 'dict(shape=shape, active_requests=active, padded_bucket=B,',
                  'dict(shape=shape, kv_length=L, null_page_reserved=(active < B or shape == "b64-4k"), active_requests=active, padded_bucket=B,')
    worker = once(worker, 'changed_row * (L // 16) + (1 if active < B else 0)',
                  'changed_row * (L // 16) + (1 if active < B or shape == "b64-4k" else 0)')
    worker = once(worker, 'ragged = [ragged_pattern[i % len(ragged_pattern)] for i in range(active)]',
                  'ragged = [min(L, ragged_pattern[i % len(ragged_pattern)]) for i in range(active)]')
    (HERE / "worker.py").write_bytes(worker.encode())
    old_owner = (BASE / "entry.py").read_text(encoding="utf8")
    owner = once(old_owner, 'choices=("hotspot", "b32"), default="hotspot"',
                  'choices=("hotspot", "b32", "b64-4k"), default="b64-4k"')
    # 原后缀已经包含唯一shape，UTC仍唯一；不动owner清理或身份。
    (HERE / "entry.py").write_bytes(owner.encode())
    for name, old, new in (("worker", old_worker, worker), ("owner", old_owner, owner)):
        (HERE / (name + ".diff")).write_bytes("".join(difflib.unified_diff(
            old.splitlines(True), new.splitlines(True), fromfile="frozen-cg/" + name,
            tofile="b64-4k/" + name)).encode())
    for f in HERE.glob("*.py"):
        ast.parse(f.read_text(encoding="utf8"))


def seal():
    names = sorted(p.name for p in HERE.iterdir() if p.is_file() and p.name not in ("entry.tar.gz", "asset-pins.json"))
    pins = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}
    (HERE / "asset-pins.json").write_text(json.dumps(pins, indent=2) + "\n")
    with tarfile.open(HERE / "entry.tar.gz", "w:gz") as t:
        for n in [*names, "asset-pins.json"]:
            t.add(HERE / n, arcname=n)
    print(json.dumps(dict(pins=len(pins), sha256=hashlib.sha256((HERE / "entry.tar.gz").read_bytes()).hexdigest(),
                         bytes=(HERE / "entry.tar.gz").stat().st_size)))


if __name__ == "__main__":
    prepare()
    seal()
