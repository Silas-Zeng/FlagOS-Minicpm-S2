"""固定T32/w1/s1原型；不改变split。需复用现有组件门后才接服务。"""
import triton
import triton.language as tl
LN2 = tl.constexpr(0.6931471805599453)

@triton.jit
def _gqa_decode_attention_two_page(
    segm_output_ptr,
    segm_max_ptr,
    segm_expsum_ptr,
    query_ptr,
    key_cache_ptr,
    value_cache_ptr,
    seq_lens_ptr,
    block_table_ptr,
    softmax_scale_log2e,
    queries_per_kv: tl.constexpr,
    block_table_stride: tl.int64,
    query_stride_token: tl.int64,
    query_stride_head: tl.constexpr,
    k_stride_block: tl.int64,
    k_stride_slot: tl.int64,
    k_stride_head: tl.int64,
    v_stride_block: tl.int64,
    v_stride_slot: tl.int64,
    v_stride_head: tl.constexpr,
    segment_stride_token: tl.constexpr,
    segment_stride_head: tl.constexpr,
    segment_stride_segment: tl.constexpr,
    max_stride_token: tl.constexpr,
    max_stride_head: tl.constexpr,
    HEAD_SIZE: tl.constexpr,
    PAGE_SIZE: tl.constexpr,
    ROWS: tl.constexpr,
    SEGMENTS: tl.constexpr,
):
    seq_idx = tl.program_id(0)
    kv_head_idx = tl.program_id(1)
    segment_idx = tl.program_id(2)

    seq_len = tl.load(seq_lens_ptr + seq_idx)
    steps_per_segment = tl.cdiv(seq_len, SEGMENTS * PAGE_SIZE)
    lower = segment_idx * steps_per_segment * PAGE_SIZE
    if lower >= seq_len:
        return
    upper = tl.minimum(lower + steps_per_segment * PAGE_SIZE, seq_len)

    offs_row = tl.arange(0, ROWS)
    offs_dim = tl.arange(0, HEAD_SIZE)
    offs_step = tl.arange(0, 2 * PAGE_SIZE)
    # ROWS equals queries_per_kv, so every row is a real head; the padding that
    # the generic kernel carries does not exist here.
    row_valid = offs_row < queries_per_kv

    token_idx = seq_idx.to(tl.int64)
    head_idx = kv_head_idx * queries_per_kv + offs_row
    query_offsets = (
        token_idx * query_stride_token
        + head_idx[:, None] * query_stride_head
        + offs_dim[None, :]
    )
    Q = tl.load(query_ptr + query_offsets, mask=row_valid[:, None], other=0.0)

    block_table_row = block_table_ptr + seq_idx * block_table_stride
    column_slot = offs_step % PAGE_SIZE

    running_max = tl.full([ROWS], float("-inf"), dtype=tl.float32)
    running_sum = tl.zeros([ROWS], dtype=tl.float32)
    accumulator = tl.zeros([ROWS, HEAD_SIZE], dtype=tl.float32)

    full_upper = lower + ((upper - lower) // (2 * PAGE_SIZE)) * (2 * PAGE_SIZE)
    position = lower
    while position < full_upper:
        # 一个计算tile跨两个独立物理页；不假设页号相邻。
        page = tl.load(block_table_row + (position + offs_step) // PAGE_SIZE).to(tl.int64)
        k_offsets = (
            page[None, :] * k_stride_block
            + column_slot[None, :] * k_stride_slot
            + kv_head_idx * k_stride_head
            + offs_dim[:, None]
        )
        v_offsets = (
            page[:, None] * v_stride_block
            + column_slot[:, None] * v_stride_slot
            + kv_head_idx * v_stride_head
            + offs_dim[None, :]
        )
        K = tl.load(key_cache_ptr + k_offsets)
        V = tl.load(value_cache_ptr + v_offsets)

        scores = tl.dot(Q, K) * softmax_scale_log2e
        new_max = tl.maximum(running_max, tl.max(scores, 1))
        probability = tl.math.exp2(scores - new_max[:, None])
        rescale = tl.math.exp2(running_max - new_max)
        running_sum = running_sum * rescale + tl.sum(probability, 1)
        accumulator = accumulator * rescale[:, None] + tl.dot(
            probability.to(V.dtype), V
        )
        running_max = new_max
        position += 2 * PAGE_SIZE

    if full_upper < upper:
        # 末tile可能含一页或两页；页表和KV均按有效token掩码。
        column_valid = full_upper + offs_step < upper
        page = tl.load(block_table_row + (full_upper + offs_step) // PAGE_SIZE,
                       mask=column_valid, other=0).to(tl.int64)
        k_offsets = (
            page[None, :] * k_stride_block
            + column_slot[None, :] * k_stride_slot
            + kv_head_idx * k_stride_head
            + offs_dim[:, None]
        )
        v_offsets = (
            page[:, None] * v_stride_block
            + column_slot[:, None] * v_stride_slot
            + kv_head_idx * v_stride_head
            + offs_dim[None, :]
        )
        K = tl.load(key_cache_ptr + k_offsets, mask=column_valid[None, :], other=0.0)
        V = tl.load(value_cache_ptr + v_offsets, mask=column_valid[:, None], other=0.0)

        scores = tl.dot(Q, K) * softmax_scale_log2e
        scores = tl.where(column_valid[None, :], scores, float("-inf"))
        new_max = tl.maximum(running_max, tl.max(scores, 1))
        probability = tl.math.exp2(scores - new_max[:, None])
        rescale = tl.math.exp2(running_max - new_max)
        running_sum = running_sum * rescale + tl.sum(probability, 1)
        accumulator = accumulator * rescale[:, None] + tl.dot(
            probability.to(V.dtype), V
        )
        running_max = new_max

    output_offsets = (
        token_idx * segment_stride_token
        + head_idx[:, None] * segment_stride_head
        + segment_idx * segment_stride_segment
        + offs_dim[None, :]
    )
    tl.store(segm_output_ptr + output_offsets, accumulator, mask=row_valid[:, None])
    scalar_offsets = (
        token_idx * max_stride_token + head_idx * max_stride_head + segment_idx
    )
    # The scores were scaled by log2(e) so the loop is exp2-based; exp2 of a
    # log2-domain difference equals exp of the natural difference, so the sums and
    # the accumulator are already natural. reduce_segments however combines segments
    # with tl.exp, so hand back the maxima in natural units.
    tl.store(segm_max_ptr + scalar_offsets, running_max * LN2, mask=row_valid)
    tl.store(segm_expsum_ptr + scalar_offsets, running_sum, mask=row_valid)


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
