"""Pure source transformation for the audited direct 3D decode launch.

This module performs no import of torch/vLLM, no file writes and no device
work. Call transform_source with the actual audited attention/helper bytes,
then write its result only to an isolated experiment module. The existing
wrapper's use_3d gate is essential: every sequence must have at most one query.
"""

from __future__ import annotations

import hashlib
import textwrap


EXPECTED_ATTENTION_SHA256 = (
    "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
)
EXPECTED_HELPERS_SHA256 = (
    "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
)
MARKER = "# _biv150_direct_decode_launch_v1"

_RESOLVER = """    (
        seq_idx,
        q_block_local_idx,
        cur_batch_in_all_start_index,
        cur_batch_query_len,
        seq_len,
    ) = resolve_seq_and_query_len(
        query_start_len_ptr, seq_lens_ptr, q_block_global_idx, num_seqs, BLOCK_Q
    )
"""

_DIRECT_RESOLVER = """    if IS_3D:
        # The wrapper selects 3D only for query lengths 0 or 1. Map one
        # CTA to each sequence; retain the common zero-query early return.
        seq_idx = q_block_global_idx
        q_block_local_idx = 0
        cur_batch_in_all_start_index = tl.load(query_start_len_ptr + seq_idx)
        cur_batch_stop_index = tl.load(query_start_len_ptr + seq_idx + 1)
        cur_batch_query_len = cur_batch_stop_index - cur_batch_in_all_start_index
        seq_len = tl.load(seq_lens_ptr + seq_idx)
    else:
""" + textwrap.indent(_RESOLVER, "    ")

_GRID = "        grid = (total_num_q_blocks, num_kv_heads, num_par_softmax_segments)\n"
_DIRECT_GRID = "        grid = (num_seqs, num_kv_heads, num_par_softmax_segments)\n"


def transform_source(attention_source: bytes, helpers_source: bytes) -> bytes:
    """Return a candidate module from the exact reviewed pair of source files.

    Only the 3D resolver and grid0 change. The 2D path, use_3d gate, arithmetic
    tail, launch settings and token-indexed reducer remain the original code.
    Reject source drift or repeated application instead of guessing anchors.
    """
    for label, data, expected in (
        ("attention", attention_source, EXPECTED_ATTENTION_SHA256),
        ("helpers", helpers_source, EXPECTED_HELPERS_SHA256),
    ):
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise RuntimeError(f"unaudited {label} source: expected {expected}, got {actual}")
    source = attention_source.decode("utf-8")
    if MARKER in source:
        raise RuntimeError("direct decode launch is already patched")
    for label, old, new in (
        ("resolver", _RESOLVER, _DIRECT_RESOLVER),
        ("3D grid", _GRID, _DIRECT_GRID),
    ):
        if source.count(old) != 1:
            raise RuntimeError(f"unexpected {label} anchor count: {source.count(old)}")
        source = source.replace(old, new, 1)
    return (source + "\n" + MARKER + "\n").encode("utf-8")


transform = transform_source
