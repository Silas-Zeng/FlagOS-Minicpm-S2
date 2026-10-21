"""Opt-in pure-byte hook for revision 2, based on untouched 080656 init.

Never append this to the old growth/diagnostic init: both revisions wrap the
same scheduler methods and must be tested in separate isolated source copies.
"""

import hashlib


EXPECTED_INIT_SHA256 = "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff"
FOOTER = b"""
    # _biv150_growth_admission_v2_general_plugin_v1
    from vllm_fl.patches.biv150_growth_admission_v2 import install as _install_growth_admission_v2
    _install_growth_admission_v2(enabled=True)
"""


def transform_source(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != EXPECTED_INIT_SHA256:
        raise RuntimeError("unaudited growth-v2 plugin init; requires untouched 080656")
    return source + FOOTER
