"""合并4个split-major FP32 partial；每CTA处理一token的8个Q heads。"""
import triton
import triton.language as tl


@triton.jit
def reduce_panel4(output_ptr, partial_ptr, max_ptr, sum_ptr,
                  OUTPUT_STRIDE_TOKEN: tl.constexpr, OUTPUT_STRIDE_HEAD: tl.constexpr,
                  TOKENS: tl.constexpr, HEADS: tl.constexpr = 16,
                  D: tl.constexpr = 128, PANELS: tl.constexpr = 4,
                  GROUP: tl.constexpr = 8):
    token = tl.program_id(0)
    head_group = tl.program_id(1)
    panels = tl.arange(0, PANELS)
    heads = head_group * GROUP + tl.arange(0, GROUP)
    dims = tl.arange(0, D)
    scalar = ((panels[:, None] * TOKENS + token) * HEADS + heads[None, :])
    m = tl.load(max_ptr + scalar)
    l = tl.load(sum_ptr + scalar)
    live = l > 0
    overall = tl.max(tl.where(live, m, -float('inf')), axis=0)
    any_live = tl.sum(live.to(tl.int32), axis=0) > 0
    overall = tl.where(any_live, overall, 0.0)
    weights = tl.exp(tl.where(live, m - overall[None, :], -float('inf')))
    denom = tl.sum(l * weights, axis=0)
    partials = tl.load(partial_ptr + scalar[:, :, None] * D + dims[None, None, :])
    numerator = tl.sum(partials * weights[:, :, None], axis=0)
    result = tl.where(denom[:, None] > 0, numerator / denom[:, None], 0.0)
    destination = token * OUTPUT_STRIDE_TOKEN + heads[:, None] * OUTPUT_STRIDE_HEAD + dims[None, :]
    tl.store(output_ptr + destination, result)
