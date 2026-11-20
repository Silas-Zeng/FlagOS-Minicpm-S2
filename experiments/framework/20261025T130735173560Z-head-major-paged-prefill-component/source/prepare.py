"""CPU 生成真正的 FlagGems 分页 loader 改动并封包；不导入加速器。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ORIGINAL_SHA = "eef0202e6c0ed08bef8098adede1a603c63354c54b54a19414e210b675157265"
raw = (HERE / "flash_kernel_original.py").read_bytes()
assert hashlib.sha256(raw).hexdigest() == ORIGINAL_SHA
original = raw.decode()
tree = ast.parse(original)
kernel = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "flash_varlen_fwd_kernel")
calls = [n for n in ast.walk(kernel) if isinstance(n, ast.Call)
         and isinstance(n.func, ast.Name) and n.func.id == "load_from_kvcache"]
assert len(calls) == 2
lines = original.splitlines(keepends=True)
offsets = [0]
for line in lines:
    offsets.append(offsets[-1] + len(line))
candidate = original
for call in sorted(calls, key=lambda n: n.lineno, reverse=True):
    start = offsets[call.lineno - 1] + call.col_offset
    end = offsets[call.end_lineno - 1] + call.end_col_offset
    replacement = ("load_paged_kv16_rows(\n"
        "                n_block * BLOCK_N, k_len, page_table_ptr, k_ptr_base, v_ptr_base,\n"
        "                k_row_stride, k_page_stride, BLOCK_N=BLOCK_N, BLOCK_K=BLOCK_K,\n"
        "                block_size=block_size, d=d,\n"
        "            )")
    candidate = candidate[:start] + replacement + candidate[end:]
helper = '''
@triton.jit
def load_paged_kv16_rows(
    start_n, k_len, page_table_ptr, k_ptr_base, v_ptr_base,
    k_row_stride, k_page_stride, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr,
    block_size: tl.constexpr, d: tl.constexpr,
):
    # 按物理页的连续 token/channel 读取，再将 K 转成 QK 点积布局。
    # 仅验证 page16/D128；V 与 K 的 stride 相等由真实入口核实。
    tl.static_assert(block_size == 16 and d == 128 and BLOCK_K == 128)
    tl.static_assert(BLOCK_N % 16 == 0)
    page = start_n // 16 + tl.arange(0, BLOCK_N // 16)
    token = tl.arange(0, 16)
    channel = tl.arange(0, 128)
    physical = tl.load(page_table_ptr + page, mask=page * 16 < k_len, other=0).to(tl.int64)
    offsets = (physical[:, None, None] * k_page_stride
               + token[None, :, None] * k_row_stride + channel[None, None, :])
    valid = page[:, None, None] * 16 + token[None, :, None] < k_len
    k_rows = tl.load(k_ptr_base + offsets, mask=valid, other=0.0)
    v_rows = tl.load(v_ptr_base + offsets, mask=valid, other=0.0)
    k_rows = tl.reshape(k_rows, (BLOCK_N, 128))
    v_rows = tl.reshape(v_rows, (BLOCK_N, 128))
    return tl.trans(k_rows), v_rows


'''
# helper 放到原 varlen 的装饰器之前，原库数学、反向 loop、输出原样保留。
anchor = "@libentry()\n@triton.jit(\n    do_not_specialize=[\n        \"q_batch_stride\","
assert candidate.count(anchor) == 1
candidate = candidate.replace(anchor, helper + anchor)
(HERE / "flash_kernel_candidate.py").write_text(candidate, encoding="utf-8")
(HERE / "candidate.diff").write_text("".join(difflib.unified_diff(
    original.splitlines(True), candidate.splitlines(True),
    fromfile="FlagGems-v5.3.5/ops/flash_kernel.py", tofile="candidate/ops/flash_kernel.py")), encoding="utf-8")
for file in HERE.glob("*.py"):
    ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
# CPU 只核分页地址等价，不将它称作编译/数值门。
pages = list(range(1024))
pages[:8] = reversed(pages[:8])
for start in (0, 64, 14336, 16320):
    scalar = [pages[t // 16] * 8192 + (t % 16) * 256 + d
              for t in range(start, start + 64) for d in (0, 63, 127)]
    tiled = [pages[start // 16 + p] * 8192 + t * 256 + d
             for p in range(4) for t in range(16) for d in (0, 63, 127)]
    assert scalar == tiled
names = sorted(p.name for p in HERE.iterdir() if p.is_file()
    and p.name not in ("asset-pins.json", "entry.tar.gz", "cpu-results.json"))
hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names}
(HERE / "asset-pins.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
with tarfile.open(HERE / "entry.tar.gz", "w:gz") as archive:
    for name in [*names, "asset-pins.json"]:
        archive.add(HERE / name, arcname=name)
result = dict(status="CPU_AST_AND_PAGED_ADDRESS_ONLY", files=len(names),
    original_sha256=ORIGINAL_SHA, replaced_load_calls=len(calls),
    candidate_sha256=hashes["flash_kernel_candidate.py"],
    archive_sha256=hashlib.sha256((HERE / "entry.tar.gz").read_bytes()).hexdigest())
(HERE / "cpu-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
