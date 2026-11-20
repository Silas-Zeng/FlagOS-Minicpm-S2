"""两个原S2 segment在同CTA，原page16 online body，末尾原顺序归约。"""
import triton
import triton.language as tl
LN2 = tl.constexpr(0.6931471805599453)


@triton.jit
def _gqa_decode_attention_s2_incta(
    segm_output_ptr, segm_max_ptr, segm_expsum_ptr,
    query_ptr, key_cache_ptr, value_cache_ptr, seq_lens_ptr, block_table_ptr,
    softmax_scale_log2e, queries_per_kv: tl.constexpr,
    block_table_stride: tl.int64, query_stride_token: tl.int64,
    query_stride_head: tl.constexpr, k_stride_block: tl.int64,
    k_stride_slot: tl.int64, k_stride_head: tl.int64,
    v_stride_block: tl.int64, v_stride_slot: tl.int64,
    v_stride_head: tl.constexpr, segment_stride_token: tl.constexpr,
    segment_stride_head: tl.constexpr, segment_stride_segment: tl.constexpr,
    max_stride_token: tl.constexpr, max_stride_head: tl.constexpr,
    HEAD_SIZE: tl.constexpr, PAGE_SIZE: tl.constexpr,
    ROWS: tl.constexpr, SEGMENTS: tl.constexpr,
    output_ptr, output_stride_token: tl.constexpr, output_stride_head: tl.constexpr,
):
    tl.static_assert(SEGMENTS == 2 and ROWS == 8 and HEAD_SIZE == 128 and PAGE_SIZE == 16)
    seq_idx = tl.program_id(0)
    kv_head_idx = tl.program_id(1)
    seq_len = tl.load(seq_lens_ptr + seq_idx)
    steps_per_segment = tl.cdiv(seq_len, SEGMENTS * PAGE_SIZE)
    segment_idx = tl.arange(0, 2)
    lower = segment_idx * steps_per_segment * PAGE_SIZE
    upper = tl.maximum(lower, tl.minimum(lower + steps_per_segment * PAGE_SIZE, seq_len))
    full_upper = lower + ((upper - lower) // PAGE_SIZE) * PAGE_SIZE
    offs_row = tl.arange(0, ROWS)
    offs_dim = tl.arange(0, HEAD_SIZE)
    offs_step = tl.arange(0, PAGE_SIZE)
    token_idx = seq_idx.to(tl.int64)
    head_idx = kv_head_idx * queries_per_kv + offs_row
    row_valid = offs_row < queries_per_kv
    q_offsets = token_idx * query_stride_token + head_idx[:, None] * query_stride_head + offs_dim[None, :]
    Q2 = tl.load(query_ptr + q_offsets, mask=row_valid[:, None], other=0.0)
    Q = tl.broadcast_to(Q2[None, :, :], (2, ROWS, HEAD_SIZE))
    block_table_row = block_table_ptr + seq_idx * block_table_stride
    running_max = tl.full((2, ROWS), float('-inf'), tl.float32)
    running_sum = tl.zeros((2, ROWS), tl.float32)
    accumulator = tl.zeros((2, ROWS, HEAD_SIZE), tl.float32)
    iteration = 0
    full_iterations = tl.minimum(steps_per_segment, seq_len // PAGE_SIZE)
    while iteration < full_iterations:
        position = lower + iteration * PAGE_SIZE
        live = position < full_upper
        page = tl.load(block_table_row + position // PAGE_SIZE, mask=live, other=0).to(tl.int64)
        k_offsets = (page[:, None, None] * k_stride_block
            + offs_step[None, None, :] * k_stride_slot
            + kv_head_idx * k_stride_head + offs_dim[None, :, None])
        v_offsets = (page[:, None, None] * v_stride_block
            + offs_step[None, :, None] * v_stride_slot
            + kv_head_idx * v_stride_head + offs_dim[None, None, :])
        K = tl.load(key_cache_ptr + k_offsets, mask=live[:, None, None], other=0.0)
        V = tl.load(value_cache_ptr + v_offsets, mask=live[:, None, None], other=0.0)
        scores = tl.dot(Q, K) * softmax_scale_log2e
        new_max = tl.maximum(running_max, tl.max(scores, 2))
        probability = tl.math.exp2(scores - new_max[:, :, None])
        rescale = tl.math.exp2(running_max - new_max)
        next_sum = running_sum * rescale + tl.sum(probability, 2)
        next_accumulator = accumulator * rescale[:, :, None] + tl.dot(probability.to(V.dtype), V)
        running_sum = tl.where(live[:, None], next_sum, running_sum)
        accumulator = tl.where(live[:, None, None], next_accumulator, accumulator)
        running_max = tl.where(live[:, None], new_max, running_max)
        iteration += 1
    if seq_len % PAGE_SIZE != 0:
        position = full_upper
        live = position < upper
        page = tl.load(block_table_row + position // PAGE_SIZE, mask=live, other=0).to(tl.int64)
        column_valid = live[:, None] & (position[:, None] + offs_step[None, :] < upper[:, None])
        k_offsets = (page[:, None, None] * k_stride_block
            + offs_step[None, None, :] * k_stride_slot
            + kv_head_idx * k_stride_head + offs_dim[None, :, None])
        v_offsets = (page[:, None, None] * v_stride_block
            + offs_step[None, :, None] * v_stride_slot
            + kv_head_idx * v_stride_head + offs_dim[None, None, :])
        K = tl.load(key_cache_ptr + k_offsets, mask=column_valid[:, None, :], other=0.0)
        V = tl.load(value_cache_ptr + v_offsets, mask=column_valid[:, :, None], other=0.0)
        scores = tl.dot(Q, K) * softmax_scale_log2e
        scores = tl.where(column_valid[:, None, :], scores, float('-inf'))
        new_max = tl.maximum(running_max, tl.max(scores, 2))
        probability = tl.math.exp2(scores - new_max[:, :, None])
        rescale = tl.math.exp2(running_max - new_max)
        next_sum = running_sum * rescale + tl.sum(probability, 2)
        next_accumulator = accumulator * rescale[:, :, None] + tl.dot(probability.to(V.dtype), V)
        running_sum = tl.where(live[:, None], next_sum, running_sum)
        accumulator = tl.where(live[:, None, None], next_accumulator, accumulator)
        running_max = tl.where(live[:, None], new_max, running_max)
    # 保留原store前转natural单位，再按原reducer max/exp/weight/sum/div顺序。
    tiles_per_segment = tl.maximum(tl.cdiv(seq_len, SEGMENTS * PAGE_SIZE), 1)
    active = tl.cdiv(seq_len, tiles_per_segment * PAGE_SIZE)
    seg_valid = segment_idx < active
    segm_max = tl.where(seg_valid[:, None], running_max * LN2, float('-inf'))
    segm_expsum = tl.where(seg_valid[:, None], running_sum, 0.0)
    partials = tl.where(seg_valid[:, None, None], accumulator, 0.0)
    overall_max = tl.where(active > 0, tl.max(segm_max, 0), 0.0)
    weights = tl.exp(tl.where(seg_valid[:, None], segm_max, 0.0) - overall_max[None, :])
    overall_expsum = tl.sum(segm_expsum * weights, 0)
    acc = tl.sum(partials * weights[:, :, None], 0)
    acc = tl.where(overall_expsum[:, None] == 0.0, 0.0, acc / overall_expsum[:, None])
    tl.store(output_ptr + token_idx * output_stride_token + head_idx[:, None] * output_stride_head
        + offs_dim[None, :], acc, mask=row_valid[:, None])
