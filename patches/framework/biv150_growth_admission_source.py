"""Pure-byte opt-in hook transformer for the exact archived plugin __init__.

Apply only to a fresh isolated candidate source. This module never writes files
or imports vLLM; the unchanged register_model() remains the general entry point.
"""

import hashlib


EXPECTED_INIT_SHA256 = "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff"
MARKER = b"# _biv150_growth_admission_general_plugin_v1"
FOOTER = b"""
    # _biv150_growth_admission_general_plugin_v1
    from vllm_fl.patches.biv150_growth_admission import install as _install_growth_admission
    _install_growth_admission(enabled=True)
"""


def transform_source(source: bytes) -> bytes:
    actual = hashlib.sha256(source).hexdigest()
    if actual != EXPECTED_INIT_SHA256:
        raise RuntimeError("unaudited growth-admission plugin init source: " + actual)
    if source.count(b"def register_model():\n") != 1 or MARKER in source:
        raise RuntimeError("unexpected growth-admission register_model source anchors")
    return source + FOOTER
