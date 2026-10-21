"""固定两种 MiniCPM MLP 形状的隔离 CTA 枚举候选，不安装任何补丁。

精确提取已审计 Iluvatar mm_kernel 的 JIT 体；baseline 保留原源码，group8
只改整数 PID 映射。外层 autotuner/heuristics 不导入，所有参数显式固定。
只有调用 create/prepare 的设备进程才导入 Torch/Triton/FlagGems。
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
from pathlib import Path
import sys


EXPECTED_MM = "4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090"
EXPECTED_LIBENTRY = "414e8a3f74e2522e40659e7fccd84e301f4517220837a87af0311f050bbf3025"
GROUP_M = 8
CONFIGS = {
    (2048, 12288, 2048): {"BLOCK_M": 256, "BLOCK_N": 256, "BLOCK_K": 32,
                          "SPLIT_K": 1, "num_warps": 16, "num_stages": 2, "num_ctas": 1},
    (2048, 2048, 6144): {"BLOCK_M": 256, "BLOCK_N": 128, "BLOCK_K": 32,
                         "SPLIT_K": 1, "num_warps": 8, "num_stages": 2, "num_ctas": 1},
}
PARAMETERS = (
    "A", "B", "C", "M", "N", "K", "stride_am", "stride_ak", "stride_bk",
    "stride_bn", "stride_cm", "stride_cn", "acc_dtype", "input_precision",
    "fp8_fast_accum", "BLOCK_M", "BLOCK_N", "BLOCK_K", "GROUP_M", "SPLIT_K",
    "EVEN_K", "AB_DTYPE", "UPGRADE", "UPGRADE_A_OFFS", "UPGRADE_B_OFFS", "UPGRADE_C_OFFS",
)
_ORIGINAL = b"""    # grid_m = tl.cdiv(M, BLOCK_M)
    grid_n = tl.cdiv(N, BLOCK_N)
    # # re-order program ID for better L2 performance
    # width = GROUP_M * grid_n
    # group_id = pid // width
    # group_size = min(grid_m - group_id * GROUP_M, GROUP_M)
    # pid_m = group_id * GROUP_M + (pid % group_size)
    # pid_n = (pid % width) // (group_size)
    pid_m = pid // grid_n
    pid_n = pid % grid_n
"""
_GROUPED = b"""    grid_m = tl.cdiv(M, BLOCK_M)
    grid_n = tl.cdiv(N, BLOCK_N)
    width = GROUP_M * grid_n
    group_id = pid // width
    first_m = group_id * GROUP_M
    group_size = tl.minimum(grid_m - first_m, GROUP_M)
    local_pid = pid % width
    pid_m = first_m + local_pid % group_size
    pid_n = local_pid // group_size
"""


def transform_source(source: bytes, *, grouped: bool) -> bytes:
    """仅提取原 JIT 体，候选仅替换唯一 PID 区域；输入漂移即拒绝。"""
    if hashlib.sha256(source).hexdigest() != EXPECTED_MM:
        raise RuntimeError("unaudited Iluvatar mm.py source")
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "mm_kernel"]
    if len(nodes) != 1 or tuple(a.arg for a in nodes[0].args.args) != PARAMETERS:
        raise RuntimeError("unexpected original mm_kernel signature")
    fn = nodes[0]
    lines = source.splitlines(keepends=True)
    if lines[fn.lineno - 2] != b"@triton.jit\n":
        raise RuntimeError("expected immediate triton.jit decorator")
    kernel = b"".join(lines[fn.lineno - 2:fn.end_lineno])
    if kernel.count(_ORIGINAL) != 1:
        raise RuntimeError("unexpected original PID mapping")
    if grouped:
        kernel = kernel.replace(_ORIGINAL, _GROUPED, 1)
    license_header = source[:source.index(b"import logging\n")]
    imports = (b"import triton\nimport triton.language as tl\n"
               b"from flag_gems.utils import triton_lang_extension as tle\n\n\n")
    return license_header + imports + kernel + b"\n"


def mapping_coverage():
    """必要的纯 CPU 一一覆盖检查，含末组、partial M/N 和 M 不足一 tile。"""
    checked = []
    for m, n, bm, bn in ((2048, 12288, 256, 256), (2048, 2048, 256, 128),
                          (2049, 12301, 256, 256), (2305, 2051, 256, 128),
                          (4097, 513, 256, 128), (17, 129, 256, 128)):
        rows, cols = (m + bm - 1) // bm, (n + bn - 1) // bn
        actual = []
        for pid in range(rows * cols):
            width = GROUP_M * cols
            group, local = divmod(pid, width)
            first = group * GROUP_M
            height = min(rows - first, GROUP_M)
            actual.append((first + local % height, local // height))
        expected = {(r, c) for r in range(rows) for c in range(cols)}
        if len(set(actual)) != len(actual) or set(actual) != expected:
            raise AssertionError("group8 mapping omitted or duplicated a tile")
        checked.append({"M": m, "N": n, "BLOCK_M": bm, "BLOCK_N": bn,
                        "row_tiles": rows, "column_tiles": cols, "tiles": len(actual),
                        "partial_M": bool(m % bm), "partial_N": bool(n % bn), "bijection": True})
    return checked


def _load(path, raw):
    path = Path(path)
    with path.open("xb") as stream:
        stream.write(raw)
    name = "_biv150_fixed_mm_" + hashlib.sha256(raw).hexdigest()[:16]
    if name in sys.modules:
        raise RuntimeError("isolated fixed-mm module already loaded")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        del sys.modules[name]
        raise
    if tuple(module.mm_kernel.arg_names) != PARAMETERS:
        raise RuntimeError("loaded JIT signature differs")
    return module.mm_kernel


class FixedTilePair:
    """只为设备门构造固定调用；不替换 FlagGems 全局或写调优 DB。"""
    def __init__(self, baseline, candidate):
        self.baseline, self.candidate = baseline, candidate

    def prepare(self, a, b, out, *, grouped):
        """检查严格 scope，编译/首调在计时外；返回实际 LibEntry 式热 launcher。"""
        import torch
        import triton
        import triton.language as tl
        if not str(triton.__version__).startswith("3.6."):
            raise RuntimeError("fixed compiled-launch contract requires Triton 3.6")
        if (any(t.ndim != 2 or t.dtype != torch.bfloat16 or t.device.type != "cuda"
                for t in (a, b, out)) or b.device != a.device or out.device != a.device):
            raise ValueError("fixed-mm gate requires same-device BF16 matrices")
        m, k = a.shape
        kb, n = b.shape
        config = CONFIGS.get((m, n, k))
        if (config is None or kb != k or tuple(out.shape) != (m, n)
                or tuple(a.stride()) != (k, 1) or tuple(b.stride()) != (1, k)
                or tuple(out.stride()) != (n, 1)):
            raise ValueError("unsupported MLP shape/stride; no alternative dispatch")
        if len({t.untyped_storage().data_ptr() for t in (a, b, out)}) != 3:
            raise ValueError("fixed-mm operands must have disjoint storage")
        props = torch.cuda.get_device_properties(a.device)
        if "BI-V150" not in props.name or props.multi_processor_count != 16:
            raise RuntimeError("fixed-mm gate only covers the audited BI-V150 slice")
        config = dict(config)
        meta = {name: config[name] for name in ("BLOCK_M", "BLOCK_N", "BLOCK_K", "SPLIT_K")}
        meta.update(acc_dtype=tl.float32, input_precision=None, fp8_fast_accum=True,
                    GROUP_M=GROUP_M, EVEN_K=True, AB_DTYPE=tl.bfloat16,
                    UPGRADE=False, UPGRADE_A_OFFS=False, UPGRADE_B_OFFS=False,
                    UPGRADE_C_OFFS=False)
        args = (a, b, out, m, n, k, *a.stride(), *b.stride(), *out.stride())
        grid = ((m + config["BLOCK_M"] - 1) // config["BLOCK_M"]
                * ((n + config["BLOCK_N"] - 1) // config["BLOCK_N"]), 1, 1)
        kernel = self.candidate if grouped else self.baseline
        with torch.cuda.device(a.device):
            compiled = kernel[grid](*args, **meta, num_warps=config["num_warps"],
                                    num_stages=config["num_stages"], num_ctas=config["num_ctas"])
        # Exact 3.6 warm path in audited libentry.py:1777 passes all arguments,
        # including constexpr placeholders, to CompiledKernel[grid].
        all_args = args + tuple(meta[name] for name in PARAMETERS[len(args):])
        def launch():
            compiled[grid](*all_args)
        details = {"M": m, "N": n, "K": k, "a_stride": list(a.stride()),
                   "b_stride": list(b.stride()), "out_stride": list(out.stride()),
                   "config": config, "GROUP_M": GROUP_M, "grid": list(grid),
                   "grouped": grouped, "compiled_hash": getattr(compiled, "hash", None),
                   "registers": getattr(compiled, "n_regs", None),
                   "spills": getattr(compiled, "n_spills", None),
                   "shared_bytes": getattr(getattr(compiled, "metadata", None), "shared", None)}
        return launch, details


def create(source: bytes, directory):
    """在新实验目录生成独立双模块；不导入完整 mm.py 的 autotuner。"""
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError("caller must provide a new experiment source directory")
    baseline = transform_source(source, grouped=False)
    candidate = transform_source(source, grouped=True)
    return FixedTilePair(_load(directory / "mm_baseline.py", baseline),
                         _load(directory / "mm_group8.py", candidate))
