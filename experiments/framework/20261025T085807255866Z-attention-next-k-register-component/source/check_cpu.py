"""只执行新增源块的整数地址/读取序列和结构门；不是 Triton/GPU 验证。"""
import ast
import hashlib
import json
from pathlib import Path
import textwrap
import numpy as np
import next_k
import prototype

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


class Scalar(int):
    def to(self, dtype):
        return dtype(self)


class TL:
    int1, int64 = np.bool_, np.int64
    def __init__(self):
        self.reads = []
    def full(self, shape, value, dtype):
        return np.full(shape, value, dtype=dtype)
    def zeros(self, shape, dtype):
        return np.zeros(shape, dtype=dtype)
    def load(self, address, mask, other):
        self.reads.append(address[mask].copy())
        return np.where(mask, address + 1, other)


_, source = prototype.sources(ROOT / "tmp/remote-source/triton_unified_attention.py")
changed = next_k.transform(source)
assert changed == (HERE / "candidate.kernel.py").read_text(encoding="utf-8")
ast.parse(changed)
assert source.count("for j in range(loop_lo, loop_hi):") == changed.count("for j in range(loop_lo, loop_hi):") == 1
for exact in ("K = _cast_kv_tile(K_load, Q, k_scale, KV_QUANT_MODE)",
              "V = _cast_kv_tile(V_load, Q, v_scale, KV_QUANT_MODE)",
              "S += score_scale * tl.dot(Q, K)", "M, L, P, alpha = softmax_step(S, M, L)",
              "acc += tl.dot(P.to(V.dtype), V)"):
    assert source.count(exact) == changed.count(exact) == 1

initial = compile(textwrap.dedent(next_k.INITIAL), "<actual-nextK-initial>", "exec")
current = compile(textwrap.dedent(next_k.CURRENT_K), "<actual-nextK-current>", "exec")
prefetch = compile(textwrap.dedent(next_k.PREFETCH), "<actual-nextK-prefetch>", "exec")
cases = tiles = words = 0
for length in (1, 15, 16, 63, 64, 65, 127, 128, 129, 2047, 4095, 4096, 16383, 16384):
    page_count = (length + 15) // 16
    for geometry in ("continuous", "middle", "fragmented"):
        row = list(range(300, 300 + page_count))
        if geometry == "middle" and page_count > 8:
            row[:3] = row[:3][::-1]
            row[-3:] = row[-3:][::-1]
        if geometry == "fragmented":
            row = [300 + 2 * j for j in range(page_count)]
        desc = prototype.longest(row)
        hi = (length + 63) // 64
        for lo, end in ((0, hi), (hi, hi), (max(0, hi - 2), hi), (0, min(2, hi))):
            tl = TL()
            ns = dict(tl=tl, Q=np.empty((), dtype=np.int64), HEAD_SIZE_PADDED=128,
                TILE_SIZE=64, BLOCK_SIZE=16, offs_d=np.arange(128), offs_t=np.arange(64),
                dim_mask=np.ones(128, dtype=bool), key_cache_ptr=0, kv_head_idx=1,
                stride_k_cache_0=4096, stride_k_cache_1=256, stride_k_cache_2=128,
                stride_k_cache_3=1, affine_lo=Scalar(desc[0]), affine_hi=Scalar(desc[1]),
                affine_base=Scalar(desc[2]), loop_hi=end, max_seq_prefix_len=length)
            exec(initial, ns)
            expected_reads = []
            for j in range(lo, end):
                seq = j * 64 + np.arange(64)
                mask = np.broadcast_to(seq[None, :] < length, (128, 64))
                physical = np.array([row[min(int(t // 16), page_count - 1)] for t in seq])
                offset = physical[None, :] * 4096 + 128 + np.arange(128)[:, None] + (seq % 16)[None, :] * 256
                ns.update(j=j, k_offset=offset, tile_mask=seq < length)
                exec(current, ns)
                assert np.array_equal(ns["K_load"], np.where(mask, offset + 1, 0))
                expected_reads.append(offset[mask].copy())
                exec(prefetch, ns)
                tiles += 1
                words += int(mask.sum())
            assert len(tl.reads) == end - lo
            assert all(np.array_equal(a, b) for a, b in zip(tl.reads, expected_reads))
            assert not bool(ns["next_k_valid"])
            cases += 1

src = changed.splitlines()
load = next(i + 1 for i, x in enumerate(src) if "next_k_value = tl.load(" in x)
pv = next(i + 1 for i, x in enumerate(src) if "acc += tl.dot(P.to(V.dtype), V)" in x)
ir = "    %carry = scf.for %x = %lo to %hi step %one iter_args(%k = %init) -> (tensor<128x64xbf16, #blocked>) {"
filename = "<affine-pages-component-" + hashlib.sha256(changed.encode()).hexdigest() + ".py>"
machine = (f'.file 1 "{filename}"\nBB0_1:\n .loc 1 {load} 1\n ml_lsa_blkload_x1 v80, null\n sl_jump BB0_3\n'
           f"BB0_2:\n sl_exit\nBB0_3:\n .loc 1 {pv} 1\n" +
           " ml_matrix_mad_f32_bf16_m16n16k16 v0\n" * 32)
assert next_k.mechanism(ir, machine, changed)["pass_"]
negative = [machine.replace("sl_jump BB0_3", "sl_wait vmcnt(0)\n sl_jump BB0_3"),
            machine.replace("sl_jump BB0_3", "sl_barrier\n sl_jump BB0_3"),
            machine.replace("sl_jump BB0_3", "sl_jump BB0_1"),
            machine.replace("sl_jump BB0_3", "sl_jump BB0_2"),
            machine.replace(f".loc 1 {load} 1", f".loc 2 {load} 1")]
for case in negative:
    try:
        next_k.mechanism(ir, case, changed)
    except ValueError:
        pass
    else:
        raise AssertionError("结构负例漏拒")
receipt = dict(status="CPU_SOURCE_ADDRESS_CHECKS_ONLY", cases=cases, tiles=tiles, addresses=words,
    asm_parser_positive=1, asm_parser_negative=len(negative),
    source_sha256=hashlib.sha256(changed.encode()).hexdigest(),
    base_sha256=hashlib.sha256(source.encode()).hexdigest(),
    limits="NumPy执行实际新增源块并对照页表地址；ASM parser fixture仅验证拒绝逻辑，不是编译、浮点或性能证据。")
(HERE / "cpu-check.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, ensure_ascii=False))
