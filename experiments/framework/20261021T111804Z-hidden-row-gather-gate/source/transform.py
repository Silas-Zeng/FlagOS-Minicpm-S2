"""Fail-closed byte transformer for the two exact final-hidden gather sites."""

import hashlib


EXPECTED_RUNNER_SHA256 = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
ANCHOR = b"import torch\n"
ORIGINAL = b"                sample_hidden_states = hidden_states[logits_indices]\n"
IMPORT = b"from vllm_fl.patches.biv150_hidden_row_gather import try_gather_hidden_rows as _biv150_try_hidden_row_gather\n"
REPLACEMENT = b"""                # BIV150_FINAL_HIDDEN_ROW_GATHER_V1
                sample_hidden_states = _biv150_try_hidden_row_gather(
                    self, hidden_states, logits_indices, num_scheduled_tokens_np)
                if sample_hidden_states is None:
                    sample_hidden_states = hidden_states[logits_indices]
"""


def transform_source(source: bytes) -> bytes:
    actual = hashlib.sha256(source).hexdigest()
    if actual != EXPECTED_RUNNER_SHA256:
        raise RuntimeError("unaudited final-hidden gather runner source: " + actual)
    if source.count(ANCHOR) != 1 or source.count(ORIGINAL) != 2:
        raise RuntimeError("unexpected final-hidden gather source anchors")
    changed = source.replace(ANCHOR, ANCHOR + IMPORT, 1)
    return changed.replace(ORIGINAL, REPLACEMENT)
