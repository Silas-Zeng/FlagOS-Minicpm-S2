"""一个必要CPU合同：完整1024页映射与连续run不改变逻辑顺序。"""
import importlib.util
from pathlib import Path
import sys
import unittest


PATH = Path(__file__).resolve().parents[1] / "patches/framework/biv150_kv_page_copy.py"
SPEC = importlib.util.spec_from_file_location("page_copy_contract", PATH)
copy = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = copy
SPEC.loader.exec_module(copy)


class Contract(unittest.TestCase):
    def test_full_page_maps_and_rejection(self):
        source = [1 + group * 132 + offset for group in range(8) for offset in range(128)]
        destination = [1 + (7 - group) * 132 + offset for group in range(8) for offset in range(128)]
        plan = copy.make_plan(source, destination, 1058, 1058, 42 * 16384)
        actual = [(s + i, d + i) for s, d, n in plan.runs for i in range(n)]
        self.assertEqual(actual, list(zip(source, destination)))
        self.assertEqual(len(plan.runs), 8)
        self.assertEqual(plan.logical_pages * plan.page_bytes, 704643072)
        self.assertEqual(len(copy.make_plan(range(1, 1025), range(1024), 1058, 1024, 16384).runs), 1)
        for a, b in (([1, 2], [3, 3]), ([1, 1], [2, 3]), ([-1], [1]), ([1058], [1]), ([True], [1])):
            with self.assertRaises(ValueError):
                copy.make_plan(a, b, 1058, 1058, 16384)


if __name__ == "__main__":
    unittest.main()
