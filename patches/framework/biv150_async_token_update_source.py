"""Pure-byte, fail-closed transformer of the exact audited plugin runner."""

import hashlib


EXPECTED_RUNNER_SHA256 = "446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64"
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
