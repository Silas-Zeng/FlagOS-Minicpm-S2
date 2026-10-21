"""Pure bytes transform of the reviewed SQL+C3 runner; never changes a file."""
import hashlib


EXPECTED_RUNNER = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
ORIGINAL = b"""        self.req_indices.np[:total_num_scheduled_tokens] = req_indices
        self.req_indices.copy_to_gpu(total_num_scheduled_tokens)
        req_indices_gpu = self.req_indices.gpu[:total_num_scheduled_tokens]

        self.query_pos.copy_to_gpu(total_num_scheduled_tokens)
        self.num_scheduled_tokens.np[:num_reqs] = num_scheduled_tokens
        self.num_scheduled_tokens.copy_to_gpu(num_reqs)
        num_scheduled_tokens_gpu = self.num_scheduled_tokens.gpu[:num_reqs]
        self.positions[:total_num_scheduled_tokens] = (
            self.num_computed_tokens[req_indices_gpu].to(torch.int64)
            + self.query_pos.gpu[:total_num_scheduled_tokens]
        )
        self.seq_lens[:num_reqs] = (
            self.num_computed_tokens[:num_reqs] + num_scheduled_tokens_gpu
        )
        self.seq_lens[num_reqs:].fill_(0)
"""
IMPORT = b"from vllm_fl.patches.biv150_cpu_metadata import try_cpu_metadata as _biv150_try_cpu_metadata\n"
CALL = b"""        # _biv150_cpu_metadata_v1
        if not _biv150_try_cpu_metadata(self, positions_np, req_indices, num_scheduled_tokens):
"""
REPLACEMENT = CALL + b"".join(b"    " + line if line.strip() else line
                              for line in ORIGINAL.splitlines(keepends=True))


def transform_source(source: bytes) -> bytes:
    actual = hashlib.sha256(source).hexdigest()
    if actual != EXPECTED_RUNNER:
        raise RuntimeError("unaudited CPU-metadata runner: " + actual)
    anchor = b"import torch\n"
    if source.count(ORIGINAL) != 1 or source.count(anchor) != 1:
        raise RuntimeError("unexpected CPU-metadata transform anchors")
    return source.replace(anchor, anchor + IMPORT, 1).replace(ORIGINAL, REPLACEMENT, 1)
