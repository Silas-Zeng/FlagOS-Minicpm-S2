"""CPU 派生单个 .cg 候选；不触生产目录、远端或 GPU。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "gqa-identity-rescale-v3-20261025"
INHERITED = ("legacy_gate.py", "validate_hidden_row_gather.py", "validate_mixed_decode.py",
             "validate_block_table_candidate.py", "monitor_gpu.sh", "distributed_bootstrap.py",
             "dispatch_bootstrap.py", "source_identity.py", "base-source-manifest.json",
             "base-source-sha256.json", "padding-source.json", "baseline.py")


def once(text, before, after):
    assert text.count(before) == 1, before[:90]
    return text.replace(before, after, 1)


def prepare():
    pins = json.loads((BASE / "asset-pins.json").read_text())
    for name in (*INHERITED, "worker.py", "entry.py"):
        assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == pins[name], name
    for name in INHERITED:
        shutil.copyfile(BASE / name, HERE / name)
    baseline = (HERE / "baseline.py").read_text(encoding="utf-8")
    candidate = baseline
    for pointer, offset in (("key_cache_ptr", "k_offsets"), ("value_cache_ptr", "v_offsets")):
        candidate = once(candidate, f"tl.load({pointer} + {offset})",
                         f'tl.load({pointer} + {offset}, cache_modifier=".cg")')
        mask = "column_valid[None, :]" if pointer == "key_cache_ptr" else "column_valid[:, None]"
        candidate = once(candidate, f"tl.load({pointer} + {offset}, mask={mask}, other=0.0)",
                         f'tl.load({pointer} + {offset}, mask={mask}, other=0.0, cache_modifier=".cg")')
    (HERE / "candidate.py").write_bytes(candidate.encode())
    owner_old = (BASE / "entry.py").read_text(encoding="utf-8")
    owner = once(owner_old, '"-gqa-identity-rescale-v2-"', '"-gqa-kv-cg-"')
    (HERE / "entry.py").write_bytes(owner.encode())
    worker_old = (BASE / "worker.py").read_text(encoding="utf-8")
    worker = worker_old
    begin, end = worker.index("def branch_evidence("), worker.index("def worker(")
    worker = worker[:begin] + "from cache_policy import cache_evidence\n\n\n" + worker[end:]
    worker = once(worker, 'load("strict_identity_gqa_candidate",', 'load("gqa_kv_cg_candidate",')
    worker = once(worker, '''        # 静态资源只记录；是否值得保留由通过数值门后的净性能判断。
        # 不因新增分支的 private/spill/寄存器变化跳过实际 ABBA。
        result["branch"] = branch_evidence(first["candidate"].asm["ttgir"])
''', '''        # 只确认 .cg 落到机器访存指令；提示被忽略时不做计时。
        # 寄存器/shared 仅记录，不另增资源阈值。
        result["cache_policy"] = cache_evidence(first["baseline"].asm["asm"], first["candidate"].asm["asm"])
''')
    worker = worker.replace("S16 也确实执行恒等快支", "S16 也覆盖多个完整页与尾页")
    (HERE / "worker.py").write_bytes(worker.encode())
    for name, old, new in (("kernel", baseline, candidate), ("worker", worker_old, worker),
                            ("owner", owner_old, owner)):
        (HERE / (name + ".diff")).write_bytes("".join(difflib.unified_diff(
            old.splitlines(True), new.splitlines(True), fromfile="frozen-v3/" + name,
            tofile="gqa-kv-cg/" + name)).encode())
    for path in HERE.glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def seal():
    names = sorted(p.name for p in HERE.iterdir() if p.is_file()
                   and p.name not in ("entry.tar.gz", "asset-pins.json"))
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names}
    (HERE / "asset-pins.json").write_text(json.dumps(hashes, indent=2) + "\n")
    with tarfile.open(HERE / "entry.tar.gz", "w:gz") as archive:
        for name in [*names, "asset-pins.json"]:
            archive.add(HERE / name, arcname=name)
    print(json.dumps(dict(files=len(names), archive_sha256=hashlib.sha256(
        (HERE / "entry.tar.gz").read_bytes()).hexdigest(), bytes=(HERE / "entry.tar.gz").stat().st_size)))


if __name__ == "__main__":
    prepare()
    seal()
