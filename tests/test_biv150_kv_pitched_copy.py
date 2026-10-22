"""唯一CPU合同：两份真实SAVE页图逐页重建与算术拒绝；不加载SDK/框架/GPU。"""
import ctypes
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


class Contract(unittest.TestCase):
    def test_actual_page_order_preserved_and_boundaries(self):
        spec = importlib.util.spec_from_file_location("pitched_copy_cpu_contract",
            ROOT / "patches/framework/candidates/biv150_kv_pitched_copy.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        with patch.object(ctypes, "CDLL", side_effect=AssertionError("导入/规划禁止载库")):
            spec.loader.exec_module(module)
            evidence = ROOT / "analysis/source/kv-pitched-copy/save-arithmetic-evidence.json"
            self.assertEqual(hashlib.sha256(evidence.read_bytes()).hexdigest(),
                "489f1468956ff96e86188feeb89933df0ab5d35458b8d184b6adbb2729497dbc")
            actual = json.loads(evidence.read_text(encoding="utf-8"))["results"]
            self.assertEqual(len(actual), 2)
            for row in actual:
                with self.subTest(run=row["run_id"]):
                    ids = row["source_page_ids_in_original_order"]
                    plan = module.make_plan(ids, max(ids) + 1)
                    expanded = [s.source_start + j * s.source_step for s in plan.segments for j in range(s.height)]
                    destinations = [s.destination_start + j for s in plan.segments for j in range(s.height)]
                    self.assertEqual(expanded, ids)
                    self.assertEqual(destinations, list(range(len(ids))))
                    self.assertEqual(plan.logical_pages * 16, row["prefix_tokens"])
                    self.assertEqual(plan.logical_pages * 16384 * 42, row["payload_bytes_unchanged"])
                    self.assertEqual(plan.original_c95f_runs, row["actual_current_contiguous_run_count_per_layer"])
                    self.assertEqual(len(plan.segments), row["hypothetical_cover_submission_count_per_layer"])
                    self.assertEqual(sum(s.height > 1 and s.source_step > 1 for s in plan.segments),
                        row["hypothetical_2D_submissions_per_layer"])
                    self.assertTrue(all(s.source_step > 0 for s in plan.segments))
            plan = module.make_plan([0, 1, 3, 5, 7, 8, 9], 10)
            self.assertEqual([(s.source_start, s.destination_start, s.height, s.source_step) for s in plan.segments],
                [(0, 0, 2, 1), (3, 2, 2, 2), (7, 4, 3, 1)])  # 原长连续段不被相邻稀疏区吃端点。
            descending = module.make_plan([9, 7, 5, 8, 11], 12)
            self.assertEqual([(s.height, s.source_step) for s in descending.segments], [(1, 1), (1, 1), (3, 3)])
            one = module.make_plan([0], 1)
            self.assertEqual((one.logical_pages, len(one.segments)), (1, 1))
            for ids, pool in (([], 1), ([1, 1], 2), ([-1], 2), ([2], 2), ([True], 2), ([0], False),
                              ([0], (1 << 64) // 16384 + 1)):
                with self.subTest(ids=ids, pool=pool), self.assertRaises((ValueError, TypeError)):
                    module.make_plan(ids, pool)
            for segments in ((module.Segment(0, 0, 7, 0),),
                             (module.Segment(0, 0, 7, -1),),
                             (module.Segment(0, 1, 7, 1),),
                             (module.Segment(0, 0, 7, 2),),
                             (module.Segment(0, 0, 2, 1),),
                             (module.Segment(0, 0, 7, 1 << 63),)):
                with self.subTest(segments=segments), self.assertRaises(ValueError):
                    replace(plan, segments=segments)
            with self.assertRaises(ValueError): module.make_plan([0], 1, page_bytes=42 * 16384)
            self.assertFalse(any(name in sys.modules for name in ("torch", "numpy", "vllm")))
        self.assertEqual(ctypes.sizeof(module._Descriptor), 72)


if __name__ == "__main__": unittest.main()
