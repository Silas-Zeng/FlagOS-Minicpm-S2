"""一项CPU合同：暂态保留→原FIFO→普通work准入释放；无框架/设备。"""
import importlib
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
PACKAGE = "kv_protocol_defer_cpu"
package = ModuleType(PACKAGE)
package.__path__ = [str(Path(__file__).resolve().parents[1] / "patches/framework")]
sys.modules[PACKAGE] = package
R = importlib.import_module(PACKAGE + ".biv150_kv_protocol")
P = R.protocol


class Contract(unittest.TestCase):
    def test_transient_retention_and_original_admission(self):
        events, operations = [], []

        def emit(state, event, **fields):
            events.append((event, fields))

        def rpc(state, victim, operation):
            self.assertEqual(operation.kind, "DROP")
            operations.append(operation)
            victim["host_held"] = False
            return P.Receipt(operation, 0, True, True)

        def make(pending=False):
            request = NS(request_id="victim", num_output_placeholders=0,
                status=NS(name="PREEMPTED"), num_computed_tokens=0,
                num_preemptions=1, all_token_ids=list(range(36)), num_tokens=36,
                terminal=False)
            request.is_finished = lambda: request.terminal
            tx = P.Transaction(P.plan_snapshot(P.Key("session", "victim", 1, 1),
                35, request.all_token_ids, [5, 6, 7], {9: 1} if pending else {}), P.HostSlot(1 << 30))
            save = tx.submit_save()
            tx.acknowledge(P.Receipt(save, save.nbytes, True, True))
            tx.source_free_committed()
            allocations = []
            def allocate(*args, **kwargs):
                allocations.append((args, kwargs))
                return None
            manager = NS(block_pool=NS(get_num_free_blocks=lambda: 7),
                coordinator=NS(single_type_managers=[NS(new_block_ids=[77])]), allocate_slots=allocate)
            scheduler = NS(requests={"victim": request}, running=[], kv_cache_manager=manager,
                scheduler_reserve_full_isl=True)
            victim = {"tx": tx, "request": request, "host_held": True, "frames": {}}
            state = {"engine": NS(scheduler=scheduler), "victim": victim,
                "counts": {"restore_skips": 0}}
            return state, scheduler, request, victim, allocations

        with patch.object(R, "_emit", emit), patch.object(R, "_rpc", rpc):
            state, scheduler, request, victim, allocations = make(pending=True)
            token = R._ACTIVE.set(state)
            try:
                # 未消费frame不触allocator/释放；重复等待只输出一次reason。
                R._try_restore(scheduler, request, 64)
                R._try_restore(scheduler, request, 64)
                self.assertEqual(victim["tx"].phase, "HOST_RESIDENT")
                self.assertEqual(allocations, [])
                self.assertEqual([e for e, _ in events].count("RESTORE_DEFERRED"), 1)
                output = NS(num_scheduled_tokens={})
                calls = []
                wrapped = R._wrap_schedule(lambda *a: self.fail("unexpected unscoped call"),
                    lambda *a: calls.append("original_schedule") or output)
                request.status.name = "RUNNING"  # status本身不能冒称本output已准入。
                self.assertIs(wrapped(scheduler), output)
                self.assertIs(state["victim"], victim)
                self.assertEqual(calls, ["original_schedule"])
                request.status.name = "PREEMPTED"
                frame = NS()
                victim["frames"][id(frame)] = (9, frame)
                update_calls = []
                update = R._wrap_update(lambda *a: update_calls.append("original_update") or "result")
                self.assertEqual(update(scheduler, frame), "result")
                self.assertEqual(update_calls, ["original_update"])
                self.assertEqual(victim["tx"].pending_frames, set())
                request.num_output_placeholders = 1
                R._try_restore(scheduler, request, 64)
                self.assertEqual(allocations, [])
                request.num_output_placeholders = 0
                R._try_restore(scheduler, request, 64)
                self.assertEqual(len(allocations), 1)
                self.assertEqual(victim["tx"].phase, "HOST_RESIDENT")
                self.assertTrue(victim["host_held"])
                output.num_scheduled_tokens[request.request_id] = 1
                self.assertIs(wrapped(scheduler), output)
                self.assertIsNone(state["victim"])
                self.assertEqual(victim["tx"].slot.used_bytes, 0)
                self.assertEqual(len(operations), 1)
                self.assertEqual(events[-1][1]["reason"], "ordinary_recompute_admitted")
            finally:
                R._ACTIVE.reset(token)
            # 真正失效立即DROP；不将对象、epoch或prefix变化当暂态。
            for invalid in ("identity", "attempt", "digest", "terminal"):
                with self.subTest(invalid=invalid):
                    state, scheduler, request, victim, allocations = make()
                    if invalid == "identity":
                        scheduler.requests[request.request_id] = object()
                    elif invalid == "attempt":
                        request.num_preemptions += 1
                    elif invalid == "digest":
                        request.all_token_ids[0] = 99
                    else:
                        request.terminal = True
                    token = R._ACTIVE.set(state)
                    try:
                        R._try_restore(scheduler, request, 64)
                    finally:
                        R._ACTIVE.reset(token)
                    self.assertIsNone(state["victim"])
                    self.assertEqual(victim["tx"].slot.used_bytes, 0)
                    self.assertEqual(allocations, [])
        self.assertFalse(any(name in sys.modules for name in ("torch", "numpy", "vllm")))


if __name__ == "__main__":
    unittest.main()
