"""Small CPU proof of the old/new decode CTA-to-query mapping; no GPU imports.

Run: python -m unittest discover -s tests -p test_biv150_direct_decode.py -v
"""

from bisect import bisect_right
import importlib.util
from itertools import product
from pathlib import Path
import unittest


def prefix_sums(lengths):
    prefix = [0]
    for length in lengths:
        prefix.append(prefix[-1] + length)
    return prefix


def original_live_ctas(lengths, block_q, grid_limit=None):
    prefix = prefix_sums(lengths)
    # Audited helper formula: search floor(query_start/BLOCK_Q) + seq.
    boundaries = [prefix[seq] // block_q + seq for seq in range(len(lengths))]
    grid = prefix[-1] // block_q + len(lengths) if grid_limit is None else grid_limit
    live = []
    for pid in range(grid):
        seq = bisect_right(boundaries, pid) - 1
        local = pid - boundaries[seq]
        if local * block_q < lengths[seq]:
            live.append((seq, local, prefix[seq], lengths[seq]))
    return live


def direct_live_ctas(lengths):
    if any(length not in (0, 1) for length in lengths):
        raise ValueError("direct mapping requires max query length <= 1")
    prefix = prefix_sums(lengths)
    return [(seq, 0, prefix[seq], length) for seq, length in enumerate(lengths) if length]


class DirectDecodeMappingProof(unittest.TestCase):
    def assert_mapping(self, lengths, block_q):
        old = original_live_ctas(lengths, block_q)
        new = direct_live_ctas(lengths)
        self.assertEqual(old, new, (lengths, block_q))
        prefix = prefix_sums(lengths)
        self.assertEqual(len(new), prefix[-1])
        # Each actual output token still has the same unique sequence owner.
        # This is the reducer's unchanged raw-token binary-search mapping.
        for seq, local, start, length in new:
            self.assertEqual(local, 0)
            self.assertEqual(length, 1)
            self.assertEqual(bisect_right(prefix[:-1], start) - 1, seq)

    def test_exhaustive_zero_one_queries(self):
        for count in range(9):
            for lengths in product((0, 1), repeat=count):
                for block_q in (1, 2, 4, 8):
                    self.assert_mapping(lengths, block_q)

    def test_graph_padding_and_internal_zero_queries(self):
        for lengths in (
            [1] * 55 + [0] * 9,
            [0] * 9 + [1] * 55,
            [0, 1, 0, 0, 1, 0] * 8,
            [0] * 64,
            [1 if i % 5 else 0 for i in range(512)],
        ):
            for block_q in (1, 2, 4, 8):
                self.assert_mapping(lengths, block_q)

    def test_dense_minicpm_holes_cannot_be_truncated(self):
        lengths = [1] * 64
        old_grid = 64 // 2 + 64
        self.assertEqual(old_grid, 96)
        self.assertEqual(len(original_live_ctas(lengths, 2)), 64)
        self.assertEqual(old_grid - len(original_live_ctas(lengths, 2)), 32)
        truncated = original_live_ctas(lengths, 2, grid_limit=64)
        missing = set(range(64)) - {item[0] for item in truncated}
        self.assertEqual(missing, set(range(43, 64)))
        self.assertEqual(len(direct_live_ctas(lengths)), 64)

    def test_minicpm_head_segment_destinations_unchanged(self):
        lengths = [0, 1, 1, 0, 1, 0]
        old, new = original_live_ctas(lengths, 2), direct_live_ctas(lengths)
        def stores(mapping):
            return {
                (start + local * 2 + lane // 8, kv_head * 8 + lane % 8, segment)
                for seq, local, start, length in mapping
                for kv_head in range(2) for segment in range(16) for lane in range(16)
                if local * 2 + lane // 8 < length
            }
        self.assertEqual(stores(old), stores(new))
        self.assertEqual(len(stores(new)), 3 * 16 * 16)

    def test_prefill_is_outside_direct_mapping_precondition(self):
        with self.assertRaises(ValueError):
            direct_live_ctas([1, 3, 0])

    def test_source_transform_rejects_unaudited_bytes(self):
        path = Path(__file__).resolve().parents[1] / "patches/framework/biv150_direct_decode.py"
        spec = importlib.util.spec_from_file_location("direct_decode_transform", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaisesRegex(RuntimeError, "unaudited attention source"):
            module.transform_source(b"unreviewed source", b"unreviewed helpers")


if __name__ == "__main__":
    unittest.main()
