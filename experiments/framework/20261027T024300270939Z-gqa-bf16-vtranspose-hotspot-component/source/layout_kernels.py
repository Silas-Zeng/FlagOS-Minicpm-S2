"""纯BF16页内V转置；仅独立组件，不安装生产。K原NHD，V[head,dim,slot]。"""
import triton
import triton.language as tl


@triton.jit
def encode_cache(source, packed):
    page = tl.program_id(0)
    slot = tl.program_id(1)
    d = tl.arange(0, 256)
    original = page.to(tl.int64) * 8192 + slot * 256 + d
    target_v = page.to(tl.int64) * 8192 + 4096 + (d // 128) * 2048 + (d % 128) * 16 + slot
    k = tl.load(source + original)
    v = tl.load(source + original + 4096)
    tl.store(packed + original, k)
    tl.store(packed + target_v, v)


@triton.jit
def decode_cache(packed, output):
    page = tl.program_id(0)
    slot = tl.program_id(1)
    d = tl.arange(0, 256)
    original = page.to(tl.int64) * 8192 + slot * 256 + d
    target_v = page.to(tl.int64) * 8192 + 4096 + (d // 128) * 2048 + (d % 128) * 16 + slot
    k = tl.load(packed + original)
    v = tl.load(packed + target_v)
    tl.store(output + original, k)
    tl.store(output + original + 4096, v)


@triton.jit
def write_rows(key, value, slots, packed, INPUT_STRIDE: tl.constexpr):
    # 与原writer一样每token一个CTA，直接写新布局；无每步整池transpose。
    token = tl.program_id(0)
    slot_id = tl.load(slots + token).to(tl.int64)
    if slot_id < 0:
        return
    d = tl.arange(0, 256)
    page = slot_id // 16
    slot = slot_id % 16
    k = tl.load(key + token.to(tl.int64) * INPUT_STRIDE + d)
    v = tl.load(value + token.to(tl.int64) * INPUT_STRIDE + d)
    original = page * 8192 + slot * 256 + d
    target_v = page * 8192 + 4096 + (d // 128) * 2048 + (d % 128) * 16 + slot
    tl.store(packed + original, k)
    tl.store(packed + target_v, v)
