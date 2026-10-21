"""Exact byte transforms for the isolated mapped mixed-Attention candidate.

No file writes or accelerator imports. The original runner and Attention
remain untouched. The derived JIT keeps its ordinary branches as fallbacks.
"""
import hashlib

EXPECTED_RUNNER = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
EXPECTED_ATTENTION = "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
EXPECTED_HELPERS = "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
RUNNER_FOOTER = b"\n# _biv150_mapped_decode_v1\nfrom vllm_fl.patches.biv150_mapped_decode import install as _install_mapped_decode\n_install_mapped_decode(ModelRunnerFL, enabled=True)\n"


def _once(source, old, new):
    if source.count(old) != 1:
        raise RuntimeError("unexpected mapped-decode source anchor: " + old[:80].decode())
    return source.replace(old, new, 1)


def transform_runner(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != EXPECTED_RUNNER:
        raise RuntimeError("mapped decode requires the exact SQL+C3 runner")
    return source + RUNNER_FOOTER


def transform_attention(source: bytes, helpers: bytes) -> bytes:
    if (hashlib.sha256(source).hexdigest() != EXPECTED_ATTENTION
            or hashlib.sha256(helpers).hexdigest() != EXPECTED_HELPERS):
        raise RuntimeError("mapped decode requires exact 54c Attention / 59d9 helpers")
    changed = _once(source, b"    Q_IS_FP8: tl.constexpr = False,\n",
                    b"    Q_IS_FP8: tl.constexpr = False,\n"
                    b"    decode_req_indices_ptr=None,\n"
                    b"    MAPPED_DECODE: tl.constexpr = False,\n"
                    b"    SKIP_SINGLE_QUERY: tl.constexpr = False,\n")
    resolve = b"""    (
        seq_idx,
        q_block_local_idx,
        cur_batch_in_all_start_index,
        cur_batch_query_len,
        seq_len,
    ) = resolve_seq_and_query_len(
        query_start_len_ptr, seq_lens_ptr, q_block_global_idx, num_seqs, BLOCK_Q
    )
"""
    mapped = b"""    if MAPPED_DECODE:
        tl.static_assert(IS_3D and BLOCK_M == 16 and BLOCK_Q == 2)
        tl.static_assert(TILE_SIZE == 16 and BLOCK_SIZE == 16)
        tl.static_assert(HEAD_SIZE == 128 and HEAD_SIZE_PADDED == 128)
        tl.static_assert(num_query_heads == 16 and num_queries_per_kv == 8)
        tl.static_assert(NUM_SEGMENTS_PER_SEQ == 16)
        tl.static_assert(not USE_TD and not USE_TD_QO and not SKIP_SINGLE_QUERY)
        tl.static_assert(USE_CAUSAL and not USE_PER_SEQ_CAUSAL)
        tl.static_assert(not USE_MM_PREFIX and SLIDING_WINDOW == 0)
        tl.static_assert(not USE_ALIBI_SLOPES and not USE_ALIBI_SQRT)
        tl.static_assert(not USE_QQ_BIAS and not USE_SOFTCAP and not USE_SINKS)
        tl.static_assert(not USE_FP8 and not Q_IS_FP8 and KV_QUANT_MODE == 0)
        tl.static_assert(CHUNK_LOOKBACK == -1 and CHUNK_SIZE == -1)
        # d=program id indexes scratch; r indexes requests; t=cu[r] indexes Q/out.
        seq_idx = tl.load(decode_req_indices_ptr + q_block_global_idx)
        q_block_local_idx = 0
        cur_batch_in_all_start_index = tl.load(query_start_len_ptr + seq_idx)
        cur_batch_query_len = 1  # CPU plan proves every selected query length.
        seq_len = tl.load(seq_lens_ptr + seq_idx)
    else:
""" + b"".join(b"    " + line if line.strip() else line for line in resolve.splitlines(keepends=True))
    changed = _once(changed, resolve, mapped)
    early = b"""    if q_block_local_idx * BLOCK_Q >= cur_batch_query_len:
        return
"""
    changed = _once(changed, early, early + b"""
    if SKIP_SINGLE_QUERY:
        tl.static_assert(not IS_3D and BLOCK_M == 128 and BLOCK_Q == 16)
        tl.static_assert(TILE_SIZE == 64 and BLOCK_SIZE == 16)
        if cur_batch_query_len == 1:
            return
""")
    anchor = b"    query_offset_0 = cur_batch_in_all_start_index + query_pos\n"
    changed = _once(changed, anchor, anchor + b"""    scratch_query_offset_0 = (q_block_global_idx + query_pos) if MAPPED_DECODE else query_offset_0
""")
    changed = _once(changed, b"""            segm_output_offset = (
                query_offset_0[:, None].to(tl.int64)
""", b"""            segm_output_offset = (
                scratch_query_offset_0[:, None].to(tl.int64)
""")
    changed = _once(changed, b"""        store_segm_reduce_scalars(
            segm_max_ptr,
            segm_expsum_ptr,
            query_offset_0,
""", b"""        store_segm_reduce_scalars(
            segm_max_ptr,
            segm_expsum_ptr,
            scratch_query_offset_0,
""")
    changed = _once(changed, b"""    FP8_MAX: tl.constexpr = float8_info.max,
):
    query_token_idx = tl.program_id(0)
""", b"""    FP8_MAX: tl.constexpr = float8_info.max,
    decode_req_indices_ptr=None,
    MAPPED_DECODE: tl.constexpr = False,
):
    query_token_idx = tl.program_id(0)
""")
    changed = _once(changed, b"""    seq_idx = find_seq_idx(
        query_start_len_ptr, query_token_idx, num_seqs, BLOCK_Q, False
    )
""", b"""    if MAPPED_DECODE:
        tl.static_assert(BLOCK_Q == 2 and TILE_SIZE == 16 and NUM_SEGMENTS_PER_SEQ == 16)
        tl.static_assert(HEAD_SIZE == 128 and HEAD_SIZE_PADDED == 128 and not USE_FP8)
        seq_idx = tl.load(decode_req_indices_ptr + query_token_idx)
        output_token_idx = tl.load(query_start_len_ptr + seq_idx)
    else:
        seq_idx = find_seq_idx(
            query_start_len_ptr, query_token_idx, num_seqs, BLOCK_Q, False
        )
        output_token_idx = query_token_idx
""")
    changed = _once(changed, b"""    output_offset = (
        query_token_idx * output_stride_0
""", b"""    output_offset = (
        output_token_idx * output_stride_0
""")
    changed = _once(changed, b"""    use_td: bool = False,
):
    # Resolve causal: bool or per-seq tensor.
""", b"""    use_td: bool = False,
    biv150_decode_req_indices=None,
    biv150_skip_single_query: bool = False,
):
    biv150_mapped_decode = biv150_decode_req_indices is not None
    if biv150_mapped_decode or biv150_skip_single_query:
        assert not (biv150_mapped_decode and biv150_skip_single_query)
        assert q.dtype == k.dtype == v.dtype == out.dtype == torch.bfloat16
        assert q.shape[1:] == out.shape[1:] == (16, 128)
        assert k.shape[1:] == v.shape[1:] == (16, 2, 128)
        assert max_seqlen_q > 1 and causal is True and window_size == (-1, -1)
        assert softcap == 0 and alibi_slopes is None and qq_bias is None and sinks is None
        assert mm_prefix_range is None and not use_alibi_sqrt and not use_td
        assert kv_quant_mode == KVQuantMode.NONE and output_scale is None and chunk_lookback == -1
    if biv150_mapped_decode:
        assert biv150_decode_req_indices.dtype == torch.int32
        assert biv150_decode_req_indices.device == q.device and biv150_decode_req_indices.ndim == 1
        assert biv150_decode_req_indices.is_contiguous()
        assert 0 < len(biv150_decode_req_indices) <= seq_threshold_3D
        assert num_par_softmax_segments == 16
        assert all(t is not None and t.shape[0] >= len(biv150_decode_req_indices)
                   for t in (softmax_segm_output, softmax_segm_max, softmax_segm_expsum))
    # Resolve causal: bool or per-seq tensor.
""")
    changed = _once(changed, b"    total_num_q_blocks = q.shape[0] // BLOCK_Q + num_seqs\n",
                    b"""    if biv150_mapped_decode:
        BLOCK_M, BLOCK_Q = 16, 2
        launch_num_warps, launch_num_stages = 2, 1
    total_num_q_blocks = q.shape[0] // BLOCK_Q + num_seqs
""")
    changed = _once(changed, b"    use_3d = not (\n", b"    use_3d = biv150_mapped_decode or not (\n")
    changed = _once(changed, b"        grid = (total_num_q_blocks, num_kv_heads, num_par_softmax_segments)\n",
                    b"        grid = (len(biv150_decode_req_indices) if biv150_mapped_decode else total_num_q_blocks, num_kv_heads, num_par_softmax_segments)\n")
    changed = _once(changed, b"        Q_IS_FP8=(q.dtype == current_platform.fp8_dtype()),\n",
                    b"""        Q_IS_FP8=(q.dtype == current_platform.fp8_dtype()),
        decode_req_indices_ptr=biv150_decode_req_indices if biv150_mapped_decode else cu_seqlens_q,
        MAPPED_DECODE=biv150_mapped_decode,
        SKIP_SINGLE_QUERY=biv150_skip_single_query,
""")
    changed = _once(changed, b"        reduce_segments[(q.shape[0], num_query_heads)](\n",
                    b"        reduce_segments[(len(biv150_decode_req_indices) if biv150_mapped_decode else q.shape[0], num_query_heads)](\n")
    changed = _once(changed, b"""            NUM_SEGMENTS_PER_SEQ=num_par_softmax_segments,
            USE_FP8=output_scale is not None,
""", b"""            NUM_SEGMENTS_PER_SEQ=num_par_softmax_segments,
            USE_FP8=output_scale is not None,
            decode_req_indices_ptr=biv150_decode_req_indices if biv150_mapped_decode else cu_seqlens_q,
            MAPPED_DECODE=biv150_mapped_decode,
""")
    return changed + b"\n# _biv150_mapped_attention_v1\n"
