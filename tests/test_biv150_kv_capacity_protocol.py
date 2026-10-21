"""一项CPU合同：实际Request AST、快路边界与原digest/allocator回退。"""
import ast
import enum
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "kv_capacity_cpu"
package = ModuleType(PACKAGE)
package.__path__ = [str(ROOT / "patches/framework")]
sys.modules[PACKAGE] = package
SPEC = importlib.util.spec_from_file_location(PACKAGE + ".biv150_kv_protocol",
    ROOT / "patches/framework/candidates/biv150_kv_capacity_protocol.py")
R = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = R
SPEC.loader.exec_module(R)
P = R.protocol


class Contract(unittest.TestCase):
    def test_capacity_guard_and_preserved_fallback(self):
        # 仅exec已审Request/RequestStatus定义，不import其torch/框架依赖或跑init。
        source = ROOT / "experiments/source-audits/20261021T170854Z-scheduler-kv-c3/source/vllm/v1/request.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
        actual = ModuleType("vllm.v1.request")
        actual.__file__ = str(source.resolve())
        actual.__dict__["enum"] = enum
        module = ast.Module(body=[ast.ImportFrom(module="__future__",
            names=[ast.alias(name="annotations")], level=0),
            classes["RequestStatus"], classes["Request"]], type_ignores=[])
        ast.fix_missing_locations(module)
        exec(compile(module, str(source.resolve()), "exec"), actual.__dict__)
        events, operations = [], []

        def rpc(state, victim, operation):
            self.assertEqual(operation.kind, "DROP")
            operations.append(operation)
            victim["host_held"] = False
            return P.Receipt(operation, 0, True, True)

        class WatchedList(list):
            def __init__(self, values, counts, field):
                super().__init__(values)
                self.counts, self.field = counts, field
            def __iter__(self):
                self.counts[self.field] += 1
                return super().__iter__()

        def make(free):
            counts = dict.fromkeys(("tokens", "history", "digest", "allocator"), 0)
            request = actual.Request.__new__(actual.Request)
            request.request_id = "victim"
            request.status = actual.RequestStatus.PREEMPTED
            request.num_output_placeholders = request.num_computed_tokens = 0
            request.num_preemptions = 1
            request.resumable, request.streaming_queue = False, None
            request._all_token_ids = list(range(36))
            request.all_token_ids = WatchedList(request._all_token_ids, counts, "tokens")
            tx = P.Transaction(P.plan_snapshot(P.Key("session", "victim", 1, 1),
                35, request._all_token_ids, [5, 6, 7], {}), P.HostSlot(1 << 30))
            save = tx.submit_save()
            tx.acknowledge(P.Receipt(save, save.nbytes, True, True))
            tx.source_free_committed()
            single = NS(req_to_blocks={}, num_cached_block={},
                        new_block_ids=WatchedList([99], counts, "history"))
            def allocate(*args, **kwargs):
                counts["allocator"] += 1
                self.assertEqual(args, (request, 0))
                self.assertEqual(kwargs["num_external_computed_tokens"], 32)
                self.assertTrue(kwargs["delay_cache_blocks"])
                self.assertTrue(kwargs["full_sequence_must_fit"])
                return None
            manager = NS(max_model_len=131072, coordinator=NS(single_type_managers=[single]),
                block_pool=NS(get_num_free_blocks=lambda: free), allocate_slots=allocate)
            scheduler = NS(requests={"victim": request}, running=[], kv_cache_manager=manager,
                scheduler_reserve_full_isl=True)
            victim = {"tx": tx, "request": request, "host_held": True}
            state = {"engine": NS(scheduler=scheduler), "victim": victim,
                     "counts": {"restore_skips": 0, "fast_rejects": 0}}
            return state, scheduler, request, single, counts

        def call(env):
            state, scheduler, request, _, counts = env
            digest = P.prefix_digest
            def checked_digest(*args):
                counts["digest"] += 1
                return digest(*args)
            token = R._ACTIVE.set(state)
            try:
                with patch.object(P, "prefix_digest", checked_digest):
                    R._try_restore(scheduler, request, 64)
            finally:
                R._ACTIVE.reset(token)

        with patch.dict(sys.modules, {"vllm.v1.request": actual}), \
                patch.object(R, "_emit", lambda state, event, **kw: events.append((event, kw))), \
                patch.object(R, "_rpc", rpc):
            R._CAPACITY_REQUEST_CHECKED, R._CAPACITY_REQUEST_CLASS = False, None
            self.assertIs(R._capacity_request_class(), actual.Request)
            env = make(1)  # P=2，F=P-1只快速拒绝，不复制/哈希/读历史或调allocator。
            call(env)
            call(env)
            self.assertEqual(env[-1], dict.fromkeys(env[-1], 0))
            self.assertEqual(env[0]["counts"], {"restore_skips": 2, "fast_rejects": 2})
            self.assertIsNotNone(env[0]["victim"])
            self.assertEqual(env[0]["victim"]["tx"].phase, "HOST_RESIDENT")
            self.assertEqual([e for e, _ in events].count("RESTORE_DEFERRED"), 1)
            # 原FCFS output恰好返回：未发work持有，真普通准入后才DROP。
            output = NS(num_scheduled_tokens={})
            original_calls = []
            schedule = R._wrap_schedule(lambda *a: self.fail("unexpected unscoped"),
                lambda *a: original_calls.append(1) or output)
            token = R._ACTIVE.set(env[0])
            try:
                self.assertIs(schedule(env[1]), output)
                self.assertIsNotNone(env[0]["victim"])
                output.num_scheduled_tokens["victim"] = 1
                self.assertIs(schedule(env[1]), output)
                self.assertIsNone(env[0]["victim"])
            finally:
                R._ACTIVE.reset(token)
            self.assertEqual(len(original_calls), 2)
            for reason in ("equal_free", "owned", "cached", "streaming", "queued_input", "over_max", "source", "missing"):
                with self.subTest(reason=reason):
                    env = make(2 if reason == "equal_free" else 1)
                    state, scheduler, request, single, counts = env
                    if reason == "owned":
                        single.req_to_blocks["victim"] = [object()]
                    elif reason == "cached":
                        single.num_cached_block["victim"] = 1
                    elif reason == "streaming":
                        request.resumable = True
                    elif reason == "queued_input":
                        request.streaming_queue = []
                    elif reason == "over_max":
                        scheduler.kv_cache_manager.max_model_len = 16
                    R._CAPACITY_REQUEST_CHECKED, R._CAPACITY_REQUEST_CLASS = False, None
                    if reason == "source":
                        with patch.object(R, "EXPECTED_CAPACITY_REQUEST", "0" * 64):
                            call(env)
                    elif reason == "missing":
                        saved = sys.modules.pop("vllm.v1.request")
                        try:
                            call(env)
                        finally:
                            sys.modules["vllm.v1.request"] = saved
                    else:
                        call(env)
                    self.assertEqual(counts, dict.fromkeys(counts, 1))
                    self.assertEqual(state["counts"]["fast_rejects"], 0)
                    self.assertIsNotNone(state["victim"])
            # 身份/取消/epoch先行；长度不足不能因F<P延迟释放。
            for reason in ("identity", "cancel", "epoch", "length"):
                with self.subTest(reason=reason):
                    env = make(1)
                    state, scheduler, request, _, counts = env
                    R._CAPACITY_REQUEST_CHECKED, R._CAPACITY_REQUEST_CLASS = False, None
                    if reason == "identity":
                        scheduler.requests["victim"] = object()
                    elif reason == "cancel":
                        request.status = actual.RequestStatus.FINISHED_ABORTED
                    elif reason == "epoch":
                        request.num_preemptions += 1
                    else:
                        request._all_token_ids = list(range(32))
                        request.all_token_ids = WatchedList(request._all_token_ids, counts, "tokens")
                    call(env)
                    self.assertIsNone(state["victim"])
                    self.assertEqual(counts, dict.fromkeys(counts, 0))
        self.assertFalse(any(name in sys.modules for name in ("torch", "numpy", "vllm")))


if __name__ == "__main__":
    unittest.main()
