"""Pure launch-only transformation for the audited retained attention pair.

No torch/vLLM imports, file writes or device work. Write the returned bytes
only to a fresh experiment module; never apply this to site-packages in place.
"""

from __future__ import annotations

import hashlib


EXPECTED_ATTENTION_SHA256 = (
    "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
)
EXPECTED_HELPERS_SHA256 = (
    "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
)
MARKER = "# _biv150_decode_launch_policy_v1"
_ANCHOR = '''    if launch_num_stages is not None:
        launch_kwargs["num_stages"] = launch_num_stages

    kernel_unified_attention[grid](
'''


def transform_source(
    attention_source: bytes,
    helpers_source: bytes,
    num_warps: int,
    num_stages: int,
) -> bytes:
    """Set only 3D launch options; preserve tiles, grid and all arithmetic.

    The experiment is restricted to w4s3, w4s1, w2s3 and w2s1. Exact hashes
    reject drift, including a previously transformed/direct-decode module.
    """
    if type(num_warps) is not int or num_warps not in (2, 4):
        raise ValueError("audited launch screen requires num_warps in (2, 4)")
    if type(num_stages) is not int or num_stages not in (1, 3):
        raise ValueError("audited launch screen requires num_stages in (1, 3)")
    for label, data, expected in (
        ("attention", attention_source, EXPECTED_ATTENTION_SHA256),
        ("helpers", helpers_source, EXPECTED_HELPERS_SHA256),
    ):
        if not isinstance(data, bytes):
            raise TypeError(f"{label} source must be bytes")
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise RuntimeError(f"unaudited {label} source: expected {expected}, got {actual}")
    source = attention_source.decode("utf-8")
    if MARKER in source or source.count(_ANCHOR) != 1:
        raise RuntimeError("unexpected retained wrapper launch anchor")
    replacement = _ANCHOR.replace(
        '    kernel_unified_attention[grid](\n',
        f'    {MARKER}\n'
        '    if use_3d:\n'
        f'        launch_kwargs["num_warps"] = {num_warps}\n'
        f'        launch_kwargs["num_stages"] = {num_stages}\n'
        '\n'
        '    kernel_unified_attention[grid](\n',
    )
    return source.replace(_ANCHOR, replacement, 1).encode("utf-8")


transform = transform_source
