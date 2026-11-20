"""从冻结组件入口派生原生产基线上的单一 stride 特化，不修改生产或旧封包。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "gqa-kv-cg-20261025"
STRIDES = ("k_stride_block", "k_stride_slot", "k_stride_head", "v_stride_block", "v_stride_slot")
INHERITED = ("legacy_gate.py", "validate_hidden_row_gather.py", "validate_mixed_decode.py",
             "validate_block_table_candidate.py", "monitor_gpu.sh", "distributed_bootstrap.py",
             "dispatch_bootstrap.py", "source_identity.py", "base-source-manifest.json",
             "base-source-sha256.json", "padding-source.json")


def once(text, before, after):
    assert text.count(before) == 1, before[:120]
    return text.replace(before, after, 1)


def prepare():
    pins = json.loads((BASE / "asset-pins.json").read_text())
    for name in (*INHERITED, "baseline.py", "worker.py", "entry.py"):
        assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == pins[name], name
    for name in INHERITED:
        shutil.copyfile(BASE / name, HERE / name)
    baseline = (BASE / "baseline.py").read_text(encoding="utf-8")
    assert hashlib.sha256(baseline.encode()).hexdigest() == "2596cc09caf9b5b38b49755ae9af41ebdcf59a1d5ad889fc8e9319d1584438d1"
    (HERE / "baseline.py").write_bytes(baseline.encode())
    candidate = baseline
    for name in STRIDES:
        candidate = once(candidate, f"    {name}: tl.int64,", f"    {name}: tl.constexpr,")
    # 常量特化不可顺带让 slot*stride 退化成 int32；保留原完整 i64 语义。
    typed = "    # Keep the original int64 arithmetic while specializing immutable strides.\n"
    typed += "".join(f"    {name}_i64 = tl.full((), {name}, tl.int64)\n" for name in STRIDES)
    for name in STRIDES:
        assert candidate.count("* " + name + "\n") == 2, name
        candidate = candidate.replace("* " + name + "\n", "* " + name + "_i64\n")
    candidate = once(candidate, "    seq_idx = tl.program_id(0)\n", typed + "    seq_idx = tl.program_id(0)\n")
    (HERE / "candidate.py").write_bytes(candidate.encode())
    owner_old = (BASE / "entry.py").read_text(encoding="utf-8")
    owner = once(owner_old, '"-gqa-kv-cg-"', '"-gqa-kv-stride-main-"')
    (HERE / "entry.py").write_bytes(owner.encode())
    worker_old = (BASE / "worker.py").read_text(encoding="utf-8")
    worker = once(worker_old, "from cache_policy import cache_evidence", "from stride_evidence import specialization_evidence\nfrom alternate_stride import check_alternate_stride")
    worker = once(worker, 'if digest(Path(gqa.__file__)) != SOURCE_SHA or digest(HERE / "baseline.py") != SOURCE_SHA:',
                  'if digest(Path(gqa.__file__)) != SOURCE_SHA or digest(HERE / "baseline.py") != "2596cc09caf9b5b38b49755ae9af41ebdcf59a1d5ad889fc8e9319d1584438d1":')
    worker = once(worker, 'candidate = load("gqa_kv_cg_candidate", HERE / "candidate.py")',
                  'baseline = load("gqa_stride_control", HERE / "baseline.py")\n        candidate = load("gqa_stride_candidate", HERE / "candidate.py")')
    worker = once(worker, 'dict(baseline=SOURCE_SHA, candidate=digest(HERE / "candidate.py"))',
                  'dict(production=SOURCE_SHA, baseline=digest(HERE / "baseline.py"), candidate=digest(HERE / "candidate.py"))')
    worker = once(worker, '(("baseline", original_producer), ("candidate", candidate._gqa_decode_attention))',
                  '(("baseline", baseline._gqa_decode_attention), ("candidate", candidate._gqa_decode_attention))')
    worker = once(worker, 'tensors=(out, partial, maxima, sums))',
                  'tensors=(out, partial, maxima, sums), pk=pk, kernel=kernel)')
    worker = once(worker, '''        # 只确认 .cg 落到机器访存指令；提示被忽略时不做计时。
        # 寄存器/shared 仅记录，不另增资源阈值。
        result["cache_policy"] = cache_evidence(first["baseline"].asm["asm"], first["candidate"].asm["asm"])
''', '''        # 双臂共同原生产无 cg，只度量新增 stride 特化；机器码未消除页乘法就不计时。
        result["stride_specialization"] = specialization_evidence(
            first["baseline"].asm["asm"], first["candidate"].asm["asm"],
            (HERE / "baseline.py").read_text(), (HERE / "candidate.py").read_text())
''')
    worker = once(worker, '        initial_output = check("dense-random")\n', '''        initial_output = check("dense-random")
        result["alternate_stride"] = check_alternate_stride(
            torch, arms, cache, query, common, grid, first, same_bits, dump, run)
        write(run / "results.json", result)
''')
    (HERE / "worker.py").write_bytes(worker.encode())
    for name, old, new in (("kernel", baseline, candidate), ("worker", worker_old, worker),
                            ("owner", owner_old, owner)):
        (HERE / (name + ".diff")).write_bytes("".join(difflib.unified_diff(
            old.splitlines(True), new.splitlines(True), fromfile="frozen-main/" + name,
            tofile="stride-constexpr/" + name)).encode())
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
