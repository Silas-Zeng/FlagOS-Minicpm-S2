import triton
import triton.language as tl

@triton.jit
def _reduce_partials(
    output_ptr,
    segm_output_ptr,
    segm_max_ptr,
    segm_expsum_ptr,
    seq_lens_ptr,
    segment_stride_token,
    segment_stride_head,
    segment_stride_segment,
    segment_stride_dim: tl.constexpr,
    max_stride_token,
    max_stride_head,
    max_stride_segment: tl.constexpr,
    output_stride_token: tl.constexpr,
    output_stride_head: tl.constexpr,
    page_size: tl.constexpr,
    num_segments: tl.constexpr,
    HEAD_SIZE: tl.constexpr,
):
    """Combine the per-segment partials for one (token, query head).

    vLLM's own reduction derives the head stride from its segment count, which is
    only valid when the buffers were allocated for exactly that width. This kernel
    takes strides, so a step may use fewer segments than the builder allocated by
    handing this reduction a prefix view.
    """
    token_idx = tl.program_id(0)
    head_idx = tl.program_id(1)

    seq_len = tl.load(seq_lens_ptr + token_idx)
    # Each program covers ceil(seq_len / (num_segments * page)) tiles, so the number
    # of segments that actually hold data is derived from that span, not from
    # seq_len / (num_segments * page) directly. The difference matters for short
    # sequences: with 16 segments and a 100-token sequence the span is one page, so
    # 7 segments are live, while the naive formula would read 1 and silently drop
    # seven eighths of the keys and values.
    tiles_per_segment = tl.maximum(tl.cdiv(seq_len, num_segments * page_size), 1)
    active = tl.cdiv(seq_len, tiles_per_segment * page_size)

    offs_seg = tl.arange(0, num_segments)
    offs_dim = tl.arange(0, HEAD_SIZE)
    seg_valid = offs_seg < active

    max_base = segm_max_ptr + token_idx * max_stride_token + head_idx * max_stride_head
    segm_max = tl.load(max_base + offs_seg * max_stride_segment,
                       mask=seg_valid, other=float("-inf"))
    # A CUDA-graph padded row can carry seq_len == 0, where no segment is live:
    # folding -inf through exp would give NaN, so the empty case reduces to 0.
    overall_max = tl.where(active > 0, tl.max(segm_max, 0), 0.0)

    expsum_base = (
        segm_expsum_ptr + token_idx * max_stride_token + head_idx * max_stride_head
    )
    segm_expsum = tl.load(expsum_base + offs_seg * max_stride_segment,
                          mask=seg_valid, other=0.0)
    weights = tl.exp(tl.where(seg_valid, segm_max, 0.0) - overall_max)
    overall_expsum = tl.sum(segm_expsum * weights, 0)

    out_base = (
        segm_output_ptr
        + token_idx * segment_stride_token
        + head_idx * segment_stride_head
    )
    partial_offsets = (
        offs_seg[:, None] * segment_stride_segment + offs_dim[None, :] * segment_stride_dim
    )
    partials = tl.load(out_base + partial_offsets, mask=seg_valid[:, None], other=0.0)
    acc = tl.sum(partials * weights[:, None], 0)
    acc = tl.where(overall_expsum == 0.0, 0.0, acc / overall_expsum)

    tl.store(
        output_ptr + token_idx * output_stride_token + head_idx * output_stride_head
        + offs_dim,
        acc,
    )
