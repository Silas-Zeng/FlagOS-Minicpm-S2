"""SQL+C3-only adapter of the already-gated integer token update transform.

The original 446f adapter and runtime stay byte-identical. This independent
adapter accepts only exact e155; kernel, mapping and replacement are unchanged.
"""

import hashlib


EXPECTED_RUNNER_SHA256 = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
MARKER = "# _biv150_async_token_update_v1"
ORIGINAL = b"""        self.input_ids.gpu.scatter_(
            dim=0,
            index=sampled_tokens_index_tensor,
            src=self.input_batch.prev_sampled_token_ids[
                prev_common_req_indices_tensor, 0
            ],
        )
"""
REPLACEMENT = b"""        # _biv150_async_token_update_v1
        if not _biv150_fused_sampled_token_update(
            self, self.input_batch.prev_sampled_token_ids, self.input_ids.gpu,
            prev_common_req_indices_tensor, sampled_tokens_index_tensor,
            prev_indices, sample_flattened_indices, total_num_scheduled_tokens,
        ):
            self.input_ids.gpu.scatter_(
                dim=0,
                index=sampled_tokens_index_tensor,
                src=self.input_batch.prev_sampled_token_ids[
                    prev_common_req_indices_tensor, 0
                ],
            )
"""


def transform_source(source: bytes) -> bytes:
    actual = hashlib.sha256(source).hexdigest()
    if actual != EXPECTED_RUNNER_SHA256:
        raise RuntimeError("unaudited async-token runner source: " + actual)
    anchor = b"import torch\n"
    if source.count(ORIGINAL) != 1 or source.count(anchor) != 1:
        raise RuntimeError("unexpected async-token source anchors")
    changed = source.replace(anchor, anchor + b"from vllm_fl.patches.biv150_async_token_update import fused_sampled_token_update as _biv150_fused_sampled_token_update\n", 1)
    return changed.replace(ORIGINAL, REPLACEMENT, 1)
