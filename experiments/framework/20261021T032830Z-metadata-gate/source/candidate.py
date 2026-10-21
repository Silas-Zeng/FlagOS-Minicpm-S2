"""Skip unchanged block-table uploads during real input preparation.

This experiment preserves the upstream buffers, strides, copy operation and
input-preparation event protocol. Install before creating any InputBatch.
Only ModelRunnerFL._prepare_inputs may skip; dummy/capture callers always copy.
"""

from __future__ import annotations

import contextvars
import functools
import hashlib
import importlib
from pathlib import Path


EXPECTED_BLOCK_TABLE_SHA256 = (
    "b3a6649b968fba0b48c333d7ac96e65cc713a86133cc7eef0a8399f5339ec600"
)
_allow_skip = contextvars.ContextVar("biv150_block_table_allow_skip", default=False)
_STAT_KEYS = ("commits", "skipped", "copied", "copied_bytes")


def _dirty_block_table_class(base: type) -> type:
    class DirtyBlockTable(base):
        _biv150_dirty_commit_patch = True

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Force the first upload of every row, including inactive rows.
            self._biv150_dirty_rows = bytearray([1]) * self.max_num_reqs
            self._biv150_row_bytes = (
                self.max_num_blocks_per_req * self.block_table.cpu.element_size()
            )
            # [attempted commits, skipped, successfully enqueued copies, bytes].
            # These are CPU-only cumulative counters, with no per-step I/O.
            self._biv150_commit_stats = {
                "scoped": [0, 0, 0, 0],
                "non_scope": [0, 0, 0, 0],
            }

        def append_row(self, block_ids, row_idx):
            super().append_row(block_ids, row_idx)
            if block_ids:
                self._biv150_dirty_rows[row_idx] = 1

        def add_row(self, block_ids, row_idx):
            super().add_row(block_ids, row_idx)
            self._biv150_dirty_rows[row_idx] = 1

        def clear_row(self, row_idx):
            super().clear_row(row_idx)
            self._biv150_dirty_rows[row_idx] = 1

        def move_row(self, src, tgt):
            super().move_row(src, tgt)
            self._biv150_dirty_rows[tgt] = 1

        def swap_row(self, src, tgt):
            super().swap_row(src, tgt)
            self._biv150_dirty_rows[src] = 1
            self._biv150_dirty_rows[tgt] = 1

        def commit_block_table(self, num_reqs):
            scoped = _allow_skip.get()
            stats = self._biv150_commit_stats["scoped" if scoped else "non_scope"]
            stats[0] += 1
            prefix = self._biv150_dirty_rows[:num_reqs]
            if scoped and not any(prefix):
                stats[1] += 1
                return
            # Keep the original single, contiguous, full-width prefix copy.
            super().commit_block_table(num_reqs)
            stats[2] += 1
            stats[3] += len(prefix) * self._biv150_row_bytes
            # Clear only successfully enqueued rows; retain inactive dirtiness.
            self._biv150_dirty_rows[:num_reqs] = bytes(len(prefix))

        def clear(self):
            # Upstream clears CPU and GPU storage, but deliberately leaves
            # num_blocks_per_row unchanged. Preserve that exact behavior.
            super().clear()
            self._biv150_dirty_rows[:] = bytes(self.max_num_reqs)

    DirtyBlockTable.__name__ = "Biv150DirtyBlockTable"
    DirtyBlockTable.__qualname__ = "Biv150DirtyBlockTable"
    return DirtyBlockTable


def snapshot_stats(table) -> dict[str, dict[str, int]]:
    """Return a detached per-table CPU counter snapshot without synchronizing.

    Pass one patched BlockTable, e.g. a member of MultiGroupBlockTable's
    block_tables. Bytes count successful copy submission, not DMA completion;
    failed attempts are included in commits but not copied/copied_bytes.
    """
    counters = table._biv150_commit_stats
    result = {
        scope: dict(zip(_STAT_KEYS, values))
        for scope, values in counters.items()
    }
    result["total"] = {
        key: result["scoped"][key] + result["non_scope"][key]
        for key in _STAT_KEYS
    }
    return result


def install_dirty_block_table_patch(model_runner_class: type, *, module=None) -> type:
    """Install the opt-in candidate for the exact audited vLLM source.

    The caller owns device/model gating and calls this before runner creation.
    CPU writes must use BlockTable's mutation methods. External CPU writes or
    device writes to active rows require an ordinary (out-of-scope) commit.
    """
    if module is None:
        module = importlib.import_module("vllm.v1.worker.block_table")
    path = Path(module.__file__)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED_BLOCK_TABLE_SHA256:
        raise RuntimeError(
            "BI-V150 block-table candidate requires the audited source: "
            f"expected {EXPECTED_BLOCK_TABLE_SHA256}, got {digest} at {path}"
        )

    prepare_inputs = model_runner_class._prepare_inputs
    if not getattr(prepare_inputs, "_biv150_dirty_commit_scope", False):
        @functools.wraps(prepare_inputs)
        def scoped_prepare_inputs(self, *args, **kwargs):
            token = _allow_skip.set(True)
            try:
                return prepare_inputs(self, *args, **kwargs)
            finally:
                _allow_skip.reset(token)

        scoped_prepare_inputs._biv150_dirty_commit_scope = True
        model_runner_class._prepare_inputs = scoped_prepare_inputs

    if not getattr(module.BlockTable, "_biv150_dirty_commit_patch", False):
        module.BlockTable = _dirty_block_table_class(module.BlockTable)
    return module.BlockTable


# Short entry point for the experiment-only model_runner module footer.
install = install_dirty_block_table_patch
