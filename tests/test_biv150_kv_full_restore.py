"""唯一联合CPU合同：真operation状态/覆盖元数据/adapter分支，非GPU证明。"""
from dataclasses import replace
import importlib.util
import os
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PKG = "kv_full_restore_cpu"
package = ModuleType(PKG)
package.__path__ = [str(ROOT / "patches/framework")]
sys.modules[PKG] = package


def load(name, relative):
    spec = importlib.util.spec_from_file_location(PKG + "." + name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


P = load("biv150_kv_transaction", "patches/framework/candidates/biv150_kv_full_restore_transaction.py")
W = load("biv150_kv_worker", "patches/framework/candidates/biv150_kv_full_restore_worker.py")
C = load("biv150_kv_page_copy", "patches/framework/biv150_kv_page_copy.py")
R = load("biv150_kv_protocol", "patches/framework/candidates/biv150_kv_full_restore_protocol.py")


class Contract(unittest.TestCase):
    def test_full_restore_operation_coverage_and_fallback(self):
        class TensorDescriptor:
            def __init__(self, device, rows, pointer):
                self.dtype, self.device, self.shape = "torch.uint8", device, (rows, 16384)
                self.pointer = pointer
            def is_contiguous(self): return True
            def is_pinned(self): return self.device == "cpu"
            def storage_offset(self): return 0
            def untyped_storage(self):
                return NS(data_ptr=lambda: self.pointer, nbytes=lambda: self.shape[0] * 16384)
        packet = W._command(dict(key=["cpu", "victim", 1, 1], operation_serial=2,
            kind="RESTORE_FULL", prefix_tokens=32, pages=[11, 12], nbytes=32 * 43008))
        host = [TensorDescriptor("cpu", 2, i + 1) for i in range(42)]
        raw = [TensorDescriptor("cuda:0", 64, i + 101) for i in range(42)]
        torch_descriptor = NS(Tensor=TensorDescriptor)
        plan = W._full_restore_plan(torch_descriptor, C, {"host": host}, raw, 64, packet)
        self.assertEqual((plan.logical_pages, sum(n for _, _, n in plan.runs)), (2, 2))
        with self.assertRaises(ValueError):
            W._command({**packet, "pages": [11, 11]})
        with self.assertRaises(RuntimeError):
            W._full_restore_plan(torch_descriptor, C, {"host": host[:-1]}, raw, 64, packet)
        with self.assertRaises(RuntimeError):
            W._full_restore_plan(torch_descriptor, C, {"host": [host[0]] * 42}, raw, 64, packet)
        with self.assertRaises(RuntimeError):
            W._full_restore_plan(torch_descriptor, C, {"host": host, "destination_pages": (11, 12)}, raw, 64, packet)

        def make(mode):
            request = NS(request_id="victim", all_token_ids=list(range(36)), num_tokens=36,
                status=NS(name="PREEMPTED"), num_computed_tokens=0, num_preemptions=1,
                num_output_placeholders=0, num_output_tokens=4, is_finished=lambda: False)
            tx = P.Transaction(P.plan_snapshot(P.Key("cpu", "victim", 1, 1), 35,
                request.all_token_ids, [5, 6, 7], {}), P.HostSlot(1 << 30))
            single = NS(req_to_blocks={}, num_cached_block={}, new_block_ids=[99])
            freed, commands = [], []
            def allocate(*args, **kwargs):
                single.req_to_blocks["victim"] = [NS(block_id=i, ref_cnt=1, is_null=False,
                                                    block_hash=None) for i in (12, 11)]
                single.num_cached_block["victim"] = 0
                single.new_block_ids.extend([12, 11])
                return object()
            def free(req):
                freed.append(req)
                single.req_to_blocks.pop(req.request_id)
                single.num_cached_block.pop(req.request_id)
            manager = NS(coordinator=NS(single_type_managers=[single]), max_model_len=131072,
                block_pool=NS(get_num_free_blocks=lambda: 64), allocate_slots=allocate,
                get_blocks=lambda rid: NS(blocks=(single.req_to_blocks[rid],)), free=free)
            scheduler = NS(requests={"victim": request}, kv_cache_manager=manager,
                           running=[], scheduler_reserve_full_isl=True)
            state = {"engine": NS(scheduler=scheduler), "victim": None,
                "counts": dict.fromkeys(("saved", "restored", "published", "rollbacks",
                                         "save_skips", "restore_skips", "fast_rejects"), 0)}
            victim = {"tx": tx, "request": request, "original_computed": 0, "host_held": False}
            state["victim"] = victim
            def rpc(function, *, args, single_value):
                self.assertIs(function, W.rpc)
                self.assertTrue(single_value)
                command = args[0]
                parsed = W._command(command)
                kind = parsed["kind"]
                commands.append(kind)
                # 这是CPU transport stub；不执行worker GPU、copy或事件。
                reply = {**command, "worker_pid": os.getpid(), "completed": True,
                    "successful": True, "transferred_bytes": command["nbytes"],
                    "host_held": kind != "DROP"}
                if kind == "SAVE" and mode != "fallback":
                    reply.update(full_restore_supported=True, saved_layers=42,
                        saved_page_bytes=16384, saved_prefix_pages=2, saved_bytes=32 * 43008)
                if kind == "RESTORE_FULL":
                    self.assertEqual(tx.phase, "RESTORE_FULL_PENDING")
                    with self.assertRaises(RuntimeError): tx.publish(tx.snapshot.key, request.all_token_ids)
                    with self.assertRaises(RuntimeError): tx.release_private_allocation()
                    with self.assertRaises(RuntimeError):
                        tx.acknowledge(P.Receipt(replace(tx.inflight, serial=tx.inflight.serial + 1),
                                                command["nbytes"], True, True))
                    reply.update(zero_stage_executed=False, zero_calls=0, destination_bound=True,
                                 full_coverage=True, full_coverage_bytes=command["nbytes"])
                    if mode in ("failed", "unsettled"):
                        reply.update(successful=False, completed=mode == "failed", transferred_bytes=0)
                    if mode == "badproof": reply["full_coverage"] = False
                return reply
            state["engine"].model_executor = NS(collective_rpc=rpc)
            tx.acknowledge(R._rpc(state, victim, tx.submit_save()))
            tx.source_free_committed()
            return state, victim, request, single, commands, freed

        with patch.object(R, "_emit", lambda *a, **k: None):
            for mode in ("full", "fallback", "failed", "unsettled", "badproof"):
                with self.subTest(mode=mode):
                    state, victim, request, single, commands, freed = make(mode)
                    tx = victim["tx"]
                    token = R._ACTIVE.set(state)
                    try:
                        if mode in ("unsettled", "badproof"):
                            with self.assertRaises(RuntimeError):
                                R._try_restore(state["engine"].scheduler, request, 64)
                            self.assertIsNotNone(tx.inflight)
                            self.assertEqual(request.num_computed_tokens, 0)
                            self.assertFalse(freed)
                            with self.assertRaises(RuntimeError): tx.close()
                        else:
                            R._try_restore(state["engine"].scheduler, request, 64)
                    finally:
                        R._ACTIVE.reset(token)
                    if mode == "failed":
                        self.assertIsNone(state["victim"])
                        self.assertEqual((len(freed), request.num_computed_tokens), (1, 0))
                        self.assertEqual(commands, ["SAVE", "RESTORE_FULL", "DROP"])
                    elif mode in ("full", "fallback"):
                        self.assertEqual(tx.phase, "RESTORE_DONE")
                        self.assertEqual(request.num_computed_tokens, 32)
                        self.assertEqual(commands, ["SAVE", "RESTORE_FULL"] if mode == "full"
                                         else ["SAVE", "ZERO", "RESTORE"])
                        tx.publish(tx.snapshot.key, request.all_token_ids)
                        R._drop(state, victim)
                        self.assertEqual(tx.slot.used_bytes, 0)
                    else:
                        self.assertEqual(commands, ["SAVE", "RESTORE_FULL"])
            # FULL提交后取消：settle之前不能释放，真ACK后沿原CANCELLED回滚。
            state, victim, request, single, commands, freed = make("full")
            state["engine"].scheduler.kv_cache_manager.allocate_slots(request, 0)
            tx = victim["tx"]
            tx.bind_private_allocation(tx.snapshot.key, request.all_token_ids, [12, 11], [12, 11])
            op = tx.submit_restore_full()
            tx.cancel()
            with self.assertRaises(RuntimeError): tx.release_private_allocation()
            tx.acknowledge(P.Receipt(op, op.nbytes, True, True))
            self.assertEqual(tx.phase, "CANCELLED")
            R._rollback(state, victim)
            self.assertEqual((len(freed), tx.slot.used_bytes), (1, 0))
        self.assertFalse(any(name in sys.modules for name in ("torch", "numpy", "vllm")))


if __name__ == "__main__":
    unittest.main()
