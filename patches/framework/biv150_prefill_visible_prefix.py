"""Explicit, uninstalled 2D prefix-mask candidate for one audited source.

The original kernel remains the fallback (including the installed C2 3D
proxy). Only complete ordinary BF16 GQA query blocks may omit a mask whose
every element is true. No tile/dot/softmax ordering or load address changes.
"""
import hashlib
import importlib.util
from pathlib import Path
import sys


EXPECTED_ATTENTION = "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
EXPECTED_HELPERS = "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
EXPECTED_BACKEND = "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605"
EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"

_SIGNATURE = b"    Q_IS_FP8: tl.constexpr = False,\n"
_LOOP = b"    # iterate through tiles (now limited to the sliding window range)\n"
_MASK = b"""        query_abs_pos = context_len + query_pos[:, None]
        seq_mask = compute_kv_seq_mask(
            query_abs_pos,
            seq_offset,
            seq_idx,
            seq_len,
            mm_prefix_range_ptr,
            SLIDING_WINDOW,
            USE_MM_PREFIX,
            MAX_MM_RANGES,
            USE_CAUSAL,
            USE_PER_SEQ_CAUSAL,
            per_seq_causal_ptr,
            CHUNK_LOOKBACK,
            CHUNK_SIZE,
        )
"""
_SELECT = b"""        S = tl.where(
            query_mask_1[:, None] & query_mask_0[:, None] & seq_mask, S, float("-inf")
        )
"""
_PREFIX = b"""    # BIV150_VISIBLE_PREFIX_V1: do not change iteration or FP arithmetic.
    if BIV150_VISIBLE_PREFIX:
        tl.static_assert(not IS_3D and BLOCK_M == 128 and BLOCK_Q == 16)
        tl.static_assert(TILE_SIZE == 64 and BLOCK_SIZE == 16)
        tl.static_assert(HEAD_SIZE == 128 and HEAD_SIZE_PADDED == 128)
        tl.static_assert(num_query_heads == 16 and num_queries_per_kv == 8)
        tl.static_assert(USE_CAUSAL and not USE_PER_SEQ_CAUSAL)
        tl.static_assert(not USE_MM_PREFIX and not SLIDING_WINDOW)
        tl.static_assert(not USE_ALIBI_SLOPES and not USE_ALIBI_SQRT)
        tl.static_assert(not USE_QQ_BIAS and not USE_SOFTCAP and not USE_SINKS)
        tl.static_assert(not USE_FP8 and not Q_IS_FP8 and KV_QUANT_MODE == 0)
        tl.static_assert(not USE_TD and not USE_TD_QO)
        tl.static_assert(CHUNK_LOOKBACK == -1 and CHUNK_SIZE == -1)
        qpos_first = q_block_local_idx * BLOCK_Q
        # Zero/invalid/partial query blocks never enter the unmasked prefix.
        complete_qblock = ((q_block_local_idx >= 0) & (qpos_first >= 0)
                           & (qpos_first + BLOCK_Q <= cur_batch_query_len)
                           & (context_len >= 0))
        full_visible_tiles = tl.where(
            complete_qblock,
            tl.minimum(loop_hi, tl.maximum(loop_lo, (context_len + qpos_first + 1) // TILE_SIZE)),
            0,
        )

"""


def _indent(block, count):
    return b"".join(b" " * count + line if line.strip() else line
                    for line in block.splitlines(keepends=True))


def transform_source(source: bytes, helpers: bytes) -> bytes:
    """Fail closed; only the one kernel signature/mask region is changed."""
    for label, raw, expected in (("attention", source, EXPECTED_ATTENTION),
                                 ("helpers", helpers, EXPECTED_HELPERS)):
        actual = hashlib.sha256(raw).hexdigest()
        if actual != expected:
            raise RuntimeError("unaudited visible-prefix " + label + ": " + actual)
    for anchor in (_SIGNATURE, _LOOP, _MASK, _SELECT):
        if source.count(anchor) != 1:
            raise RuntimeError("unexpected visible-prefix source anchor")
    changed = source.replace(_SIGNATURE, _SIGNATURE + b"    BIV150_VISIBLE_PREFIX: tl.constexpr = False,\n", 1)
    changed = changed.replace(_LOOP, _PREFIX + _LOOP, 1)
    # The generic path retains the original order. The selected path moves
    # only integer mask construction immediately before its original select;
    # QK scaling, softcap, online-softmax and PV expressions are untouched.
    changed = changed.replace(_MASK, b"        if not BIV150_VISIBLE_PREFIX:\n" + _indent(_MASK, 4), 1)
    selected = (b"        if BIV150_VISIBLE_PREFIX:\n"
                b"            if j >= full_visible_tiles:\n" + _indent(_MASK + _SELECT, 8)
                + b"        else:\n" + _indent(_SELECT, 4))
    return changed.replace(_SELECT, selected, 1)


def _require(module, expected):
    if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != expected:
        raise RuntimeError("unaudited visible-prefix dependency: " + module.__name__)


def _eligible(values):
    """Descriptor-only checks. No D2H, .item(), RNG or metadata mutation."""
    exact = {"IS_3D": False, "HEAD_SIZE": 128, "HEAD_SIZE_PADDED": 128,
             "num_query_heads": 16, "num_queries_per_kv": 8,
             "BLOCK_M": 128, "BLOCK_Q": 16, "BLOCK_SIZE": 16, "TILE_SIZE": 64,
             "NUM_SEGMENTS_PER_SEQ": 1, "KV_QUANT_MODE": 0,
             "USE_CAUSAL": True, "SLIDING_WINDOW": 0,
             "CHUNK_LOOKBACK": -1, "CHUNK_SIZE": -1,
             "num_warps": 8, "num_stages": 1}
    if any(values.get(name) != expected for name, expected in exact.items()):
        return False
    if any(values.get(name, False) for name in (
            "USE_FP8", "Q_IS_FP8", "USE_TD", "USE_TD_QO", "USE_ALIBI_SLOPES",
            "USE_ALIBI_SQRT", "USE_QQ_BIAS", "USE_SOFTCAP", "USE_SINKS",
            "USE_PER_SEQ_CAUSAL", "USE_MM_PREFIX")):
        return False
    q, k, v, out = (values.get(name) for name in (
        "query_ptr", "key_cache_ptr", "value_cache_ptr", "output_ptr"))
    if any(x is None for x in (q, k, v, out)):
        return False
    if (str(q.dtype) != "torch.bfloat16" or not all(x.dtype == q.dtype for x in (k, v, out))
            or q.device.type != "cuda" or not all(x.device == q.device for x in (k, v, out))
            or q.ndim != 3 or out.ndim != 3 or q.shape != out.shape
            or tuple(q.shape[1:]) != (16, 128)
            or k.ndim != 4 or v.shape != k.shape or tuple(k.shape[1:]) != (16, 2, 128)
            or min(q.shape[0], k.shape[0]) <= 0):
        return False
    if any(x.stride(-1) != 1 or any(s <= 0 for s in x.stride()) for x in (q, k, v, out)):
        return False
    if (q.stride(1) != 128 or out.stride(1) != 128
            or q.stride(0) < 2048 or out.stride(0) < 2048
            or any(tuple(x.stride()[1:]) != (256, 128, 1) or x.stride(0) < 4096 for x in (k, v))):
        return False
    readers = {x.untyped_storage().data_ptr() for x in (q, k, v)}
    if out.untyped_storage().data_ptr() in readers:
        return False
    count = values.get("num_seqs")
    if not isinstance(count, int) or count <= 0:
        return False
    for name, length in (("query_start_len_ptr", count + 1), ("seq_lens_ptr", count)):
        tensor = values.get(name)
        if (tensor is None or tensor.device != q.device or str(tensor.dtype) != "torch.int32"
                or tensor.ndim != 1 or tensor.shape[0] != length or tensor.stride(0) != 1):
            return False
    table = values.get("block_tables_ptr")
    return (table is not None and table.device == q.device and str(table.dtype) == "torch.int32"
            and table.ndim == 2 and table.shape[0] == count and table.shape[1] > 0
            and table.stride(1) == 1 and table.stride(0) >= table.shape[1])


class VisiblePrefix:
    """Explicit proxy; creating it does not modify globals, classes or files."""
    def __init__(self, original, candidate_kernel):
        self.original, self.candidate = original, candidate_kernel
        self.selected_launches, self.fallback_launches = 0, 0

    def __getattr__(self, name):
        return getattr(self.original, name)

    def __getitem__(self, grid):
        original, candidate = self.original[grid], self.candidate[grid]

        def invoke(*args, **kwargs):
            if not args and "BIV150_VISIBLE_PREFIX" not in kwargs and _eligible(kwargs):
                self.selected_launches += 1
                return candidate(**kwargs, BIV150_VISIBLE_PREFIX=True)
            self.fallback_launches += 1
            return original(*args, **kwargs)

        return invoke


def create(attention, helpers, backend, generated_path):
    """Generate/load isolated source; return proxy without installing it."""
    _require(attention, EXPECTED_ATTENTION)
    _require(helpers, EXPECTED_HELPERS)
    _require(backend, EXPECTED_BACKEND)
    original = attention.kernel_unified_attention
    cls, runtime = type(original), sys.modules.get(type(original).__module__)
    if (attention.current_platform.vendor_name != "iluvatar"
            or backend.unified_attention is not attention.unified_attention
            or attention.unified_attention.__globals__ is not vars(attention)
            or runtime is None or getattr(runtime, "DecodeLaunch", None) is not cls):
        raise RuntimeError("visible prefix requires audited original bindings and installed C2")
    _require(runtime, EXPECTED_C2)
    if isinstance(original.original, cls):
        raise RuntimeError("unexpected nested C2 proxy")
    generated_path = Path(generated_path)
    changed = transform_source(Path(attention.__file__).read_bytes(), Path(helpers.__file__).read_bytes())
    with generated_path.open("xb") as stream:
        stream.write(changed)
    name = "_biv150_visible_prefix_" + hashlib.sha256(changed).hexdigest()[:16]
    if name in sys.modules:
        raise RuntimeError("isolated visible-prefix module already loaded")
    spec = importlib.util.spec_from_file_location(name, generated_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        del sys.modules[name]
        raise
    return VisiblePrefix(original, module.kernel_unified_attention)
