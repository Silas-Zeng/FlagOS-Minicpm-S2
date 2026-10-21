"""CPU state-machine comparison against the exact remote BlockTable source.

Run: python -m unittest discover -s tests -p test_biv150_block_table.py -v
No vLLM installation, accelerator, server, or GPU kernel is used.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
from pathlib import Path
import random
import types
import unittest

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests/fixtures/block_table_vllm_0_24.py"
SPEC = importlib.util.spec_from_file_location(
    "biv150_block_table_candidate", ROOT / "patches/framework/biv150_block_table.py"
)
candidate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(candidate)


class CpuGpuBuffer:
    """Two separate CPU tensors stand in for the host and device buffers."""

    def __init__(self, *size, dtype, device, pin_memory):
        self.cpu = torch.zeros(*size, dtype=dtype)
        self.gpu = torch.zeros(*size, dtype=dtype)
        self.np = self.cpu.numpy()
        self.copy_calls = []
        self.fail_copy = False

    def copy_to_gpu(self, n=None):
        if self.fail_copy:
            raise RuntimeError("injected copy failure")
        self.copy_calls.append(n)
        if n is None:
            return self.gpu.copy_(self.cpu)
        return self.gpu[:n].copy_(self.cpu[:n])


def load_original_module():
    if not SOURCE.is_file():
        raise RuntimeError(f"Audited remote source snapshot is required: {SOURCE}")
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != candidate.EXPECTED_BLOCK_TABLE_SHA256:
        raise RuntimeError(f"Source snapshot hash mismatch: {digest}")
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name in ("BlockTable", "MultiGroupBlockTable")
    ]
    module = types.ModuleType("audited_vllm_block_table")
    module.__file__ = str(SOURCE)
    module.__dict__.update({
        "np": np,
        "torch": torch,
        "CpuGpuBuffer": CpuGpuBuffer,
        "get_dcp_group": lambda: types.SimpleNamespace(world_size=1, rank_in_group=0),
        "get_pcp_group": lambda: types.SimpleNamespace(world_size=1, rank_in_group=0),
        "get_total_cp_world_size": lambda: 1,
        "cdiv": lambda a, b: (a + b - 1) // b,
    })
    exec(compile(ast.Module(body=classes, type_ignores=[]), str(SOURCE), "exec"), module.__dict__)
    return module


def install(module):
    class Runner:
        def __init__(self, table):
            self.table = table

        def _prepare_inputs(self, num_reqs):
            self.table.commit_block_table(num_reqs)

        def _dummy_run(self, num_reqs):
            self.table.commit_block_table(num_reqs)

    candidate.install_dirty_block_table_patch(Runner, module=module)
    return Runner


def make_table(module, hybrid=False):
    return module.BlockTable(
        block_size=32 if hybrid else 16,
        max_num_reqs=8,
        max_num_blocks_per_req=16,
        max_num_batched_tokens=64,
        pin_memory=False,
        device=torch.device("cpu"),
        kernel_block_size=16,
        cp_kv_cache_interleave_size=1,
    )


class DirtyBlockTableTests(unittest.TestCase):
    def setUp(self):
        self.original = load_original_module()
        self.patched = load_original_module()
        self.Runner = install(self.patched)

    def pair(self, hybrid=False):
        reference = make_table(self.original, hybrid)
        table = make_table(self.patched, hybrid)
        return reference, table, self.Runner(table)

    def assert_host_equal(self, reference, table):
        np.testing.assert_array_equal(reference.num_blocks_per_row, table.num_blocks_per_row)
        self.assertTrue(torch.equal(reference.block_table.cpu, table.block_table.cpu))

    def test_skip_and_single_full_prefix_copy(self):
        _, table, runner = self.pair()
        pointer = table.block_table.gpu.data_ptr()
        stride = table.block_table.gpu.stride()
        runner._prepare_inputs(4)
        runner._prepare_inputs(4)
        self.assertEqual(table.block_table.copy_calls, [4])
        table.append_row([21], 2)
        runner._prepare_inputs(4)
        runner._prepare_inputs(4)
        self.assertEqual(table.block_table.copy_calls, [4, 4])
        self.assertEqual(table.block_table.gpu.data_ptr(), pointer)
        self.assertEqual(table.block_table.gpu.stride(), stride)
        runner._dummy_run(3)
        table.commit_block_table(4)
        stats = candidate.snapshot_stats(table)
        self.assertEqual(stats["scoped"], {
            "commits": 4, "skipped": 2, "copied": 2, "copied_bytes": 512,
        })
        self.assertEqual(stats["non_scope"], {
            "commits": 2, "skipped": 0, "copied": 2, "copied_bytes": 448,
        })
        self.assertEqual(stats["total"], {
            "commits": 6, "skipped": 2, "copied": 4, "copied_bytes": 960,
        })
        stats["total"]["commits"] = -1
        stats["scoped"]["commits"] = -1
        self.assertEqual(candidate.snapshot_stats(table)["total"]["commits"], 6)
        self.assertEqual(candidate.snapshot_stats(table)["scoped"]["commits"], 4)

    def test_inactive_dirty_row_survives_prefix_commit(self):
        _, table, runner = self.pair()
        runner._prepare_inputs(8)
        table.add_row([31, 32], 6)
        runner._prepare_inputs(4)
        self.assertEqual(table.block_table.copy_calls, [8])
        self.assertEqual(table._biv150_dirty_rows[6], 1)
        runner._prepare_inputs(7)
        self.assertEqual(table.block_table.copy_calls, [8, 7])
        self.assertTrue(torch.equal(table.block_table.cpu[:7], table.block_table.gpu[:7]))

    def test_clear_preserves_upstream_counts(self):
        reference, table, runner = self.pair()
        for obj in (reference, table):
            obj.add_row([8, 9], 1)
            obj.clear()
        self.assert_host_equal(reference, table)
        self.assertEqual(int(table.num_blocks_per_row[1]), 2)
        self.assertFalse(any(table._biv150_dirty_rows))
        for obj in (reference, table):
            obj.append_row([10], 1)
        reference.commit_block_table(4)
        runner._prepare_inputs(4)
        self.assert_host_equal(reference, table)
        self.assertTrue(torch.equal(reference.block_table.gpu[:4], table.block_table.gpu[:4]))

    def test_padding_is_restored_by_dummy_commit(self):
        reference, table, runner = self.pair()
        for obj in (reference, table):
            obj.add_row([71, 72], 6)
            obj.commit_block_table(8)
            # Same external device write as graph padding outside real active rows.
            obj.block_table.gpu[4:8].fill_(0)
        runner._prepare_inputs(4)
        reference.commit_block_table(4)
        runner._dummy_run(8)
        reference.commit_block_table(8)
        self.assertTrue(torch.equal(reference.block_table.gpu, table.block_table.gpu))
        self.assertEqual(table.block_table.copy_calls[-1], 8)

    def test_padding_reactivation_through_add_and_move(self):
        for operation in ("add", "move"):
            with self.subTest(operation=operation):
                reference, table, runner = self.pair()
                for obj in (reference, table):
                    obj.add_row([81, 82], 1)
                    obj.commit_block_table(8)
                    obj.block_table.gpu[4:8].fill_(0)
                    if operation == "add":
                        obj.add_row([91, 92], 5)
                    else:
                        obj.move_row(1, 5)
                reference.commit_block_table(6)
                runner._prepare_inputs(6)
                self.assertTrue(torch.equal(reference.block_table.gpu[:6], table.block_table.gpu[:6]))

    def test_failed_copy_retains_dirty_prefix(self):
        _, table, runner = self.pair()
        table.block_table.fail_copy = True
        with self.assertRaisesRegex(RuntimeError, "injected"):
            runner._prepare_inputs(3)
        self.assertEqual(list(table._biv150_dirty_rows[:3]), [1, 1, 1])
        self.assertEqual(candidate.snapshot_stats(table)["total"], {
            "commits": 1, "skipped": 0, "copied": 0, "copied_bytes": 0,
        })
        table.block_table.fail_copy = False
        runner._prepare_inputs(3)
        self.assertEqual(list(table._biv150_dirty_rows[:3]), [0, 0, 0])
        self.assertEqual(candidate.snapshot_stats(table)["total"], {
            "commits": 2, "skipped": 0, "copied": 1, "copied_bytes": 192,
        })

    def test_scope_resets_on_prepare_exception(self):
        class FailingRunner:
            def _prepare_inputs(self, n):
                raise RuntimeError("prepare failed")
        candidate.install_dirty_block_table_patch(FailingRunner, module=self.patched)
        with self.assertRaisesRegex(RuntimeError, "prepare failed"):
            FailingRunner()._prepare_inputs(4)
        table = make_table(self.patched)
        table.commit_block_table(4)
        table.commit_block_table(4)
        self.assertEqual(table.block_table.copy_calls, [4, 4])

    def test_install_is_idempotent_and_multigroup_uses_subclass(self):
        cls = self.patched.BlockTable
        wrapped = self.Runner._prepare_inputs
        candidate.install_dirty_block_table_patch(self.Runner, module=self.patched)
        self.assertIs(self.patched.BlockTable, cls)
        self.assertIs(self.Runner._prepare_inputs, wrapped)
        groups = self.patched.MultiGroupBlockTable(
            max_num_reqs=8, max_model_len=256, max_num_batched_tokens=64,
            pin_memory=False, device=torch.device("cpu"),
            block_sizes=[16, 32], kernel_block_sizes=[16, 16],
        )
        self.assertTrue(all(isinstance(t, cls) for t in groups.block_tables))
        groups.add_row(([1, 2], [3]), 0)
        runner = self.Runner(groups)
        runner._prepare_inputs(4)
        runner._prepare_inputs(4)
        self.assertEqual([t.block_table.copy_calls for t in groups.block_tables], [[4], [4]])

    def test_rejects_unaudited_source_before_mutating_classes(self):
        module = load_original_module()
        module.__file__ = __file__
        cls = module.BlockTable
        class Runner:
            def _prepare_inputs(self):
                pass
        original_prepare = Runner._prepare_inputs
        with self.assertRaisesRegex(RuntimeError, "audited source"):
            candidate.install_dirty_block_table_patch(Runner, module=module)
        self.assertIs(module.BlockTable, cls)
        self.assertIs(Runner._prepare_inputs, original_prepare)

    def test_random_state_machine_against_original(self):
        for hybrid in (False, True):
            with self.subTest(hybrid=hybrid):
                reference, table, runner = self.pair(hybrid)
                rng = random.Random(6301 + hybrid)
                active = 8
                for step in range(2500):
                    row, other = rng.randrange(8), rng.randrange(8)
                    op = rng.choice(("add", "append", "clear_row", "move", "swap", "clear", "commit", "dummy"))
                    count = int(reference.num_blocks_per_row[row])
                    factor = reference.blocks_per_kv_block
                    capacity = reference.max_num_blocks_per_req
                    if op == "add":
                        ids = [rng.randrange(1, 100) for _ in range(rng.randrange(6))]
                        for obj in (reference, table):
                            obj.add_row(ids, row)
                    elif op == "append":
                        room = (capacity - count) // factor
                        ids = [rng.randrange(1, 100) for _ in range(rng.randrange(min(3, room) + 1))]
                        for obj in (reference, table):
                            obj.append_row(ids, row)
                    elif op == "clear_row":
                        for obj in (reference, table):
                            obj.clear_row(row)
                    elif op == "move":
                        for obj in (reference, table):
                            obj.move_row(row, other)
                    elif op == "swap":
                        for obj in (reference, table):
                            obj.swap_row(row, other)
                    elif op == "clear":
                        for obj in (reference, table):
                            obj.clear()
                    else:
                        active = rng.randrange(9)
                        reference.commit_block_table(active)
                        if op == "dummy":
                            runner._dummy_run(active)
                        else:
                            runner._prepare_inputs(active)
                        self.assertTrue(torch.equal(reference.block_table.gpu[:active], table.block_table.gpu[:active]), (hybrid, step, op))
                    self.assert_host_equal(reference, table)


if __name__ == "__main__":
    unittest.main()
