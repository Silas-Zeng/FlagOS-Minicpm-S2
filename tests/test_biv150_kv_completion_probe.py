"""只验证观察器的不干预合同；不代替真实 EngineCore 触发证据。"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS
import unittest


PATH = Path(__file__).resolve().parents[1] / "patches/framework/biv150_kv_completion_probe.py"
SPEC = importlib.util.spec_from_file_location("kv_probe_contract", PATH)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class Contract(unittest.TestCase):
    def test_observe_failure_preempt_resume_without_future_access(self):
        self.assertFalse(probe.install())
        counts = dict.fromkeys(("running_allocation_failures", "failure_steps",
                               "failure_with_terminal_frame", "reclaim_covers_deficit_events",
                               "preemptions", "resumed_requests", "resumed_cache_hit_tokens",
                               "resumed_processed_prefix_floor_tokens", "resumed_prefix_gap_exposure_tokens",
                               "dropped_pending_lifecycles", "observation_errors", "schedule_calls"), 0)
        state = {"counts": counts, "pending": {}, "last_failed_step": None, "public": {}}
        request = NS(request_id="r", status=NS(name="RUNNING"), num_computed_tokens=34,
                     num_tokens=34, num_prompt_tokens=32, max_tokens=4, num_output_placeholders=1)
        terminal = NS(request_id="t", num_computed_tokens=35, num_prompt_tokens=32,
                      max_tokens=4, num_output_placeholders=1)
        blocks = [NS(block_id=1, ref_cnt=1, is_null=False),
                  NS(block_id=2, ref_cnt=2, is_null=False),
                  NS(block_id=3, ref_cnt=1, is_null=True)]
        predictor_calls = []
        def predictor(**kwargs):
            predictor_calls.append(kwargs)
            return 2
        manager = NS(max_model_len=65536, empty_kv_cache_blocks=NS(blocks=([],)),
                     block_pool=NS(get_num_free_blocks=lambda: 1),
                     coordinator=NS(get_num_blocks_to_allocate=predictor,
                                    single_type_managers=[NS(req_to_blocks={"t": blocks})]))
        scheduler = NS(running=[request, terminal], requests={"r": request}, kv_cache_manager=manager)
        class ForbiddenFuture:
            def __getattribute__(self, name):
                raise AssertionError("observer touched future: " + name)
        future = ForbiddenFuture()
        engine = NS(scheduler=scheduler, batch_queue=[
            (future, NS(num_scheduled_tokens={"r": 2, "t": 1}), future)])
        frame = {"state": state, "engine": engine}
        token = probe._ACTIVE.set(frame)
        calls = []
        try:
            def allocate(self, *args, **kwargs):
                calls.append((args, kwargs))
                return None
            self.assertIsNone(probe._wrap_allocate(allocate)(manager, request, 1, num_lookahead_tokens=0))
            self.assertEqual(len(calls), 1)
            self.assertEqual(predictor_calls[0]["num_tokens_main_model"], 35)
            self.assertEqual(counts["reclaim_covers_deficit_events"], 1)
            self.assertEqual(state["public"]["first_failure"]["terminal_single_ref_private_blocks"], 1)
            def preempt(self, req, timestamp):
                req.num_computed_tokens = 0
                req.status = NS(name="PREEMPTED")
                return "original"
            self.assertEqual(probe._wrap_preempt(preempt)(scheduler, request, 0), "original")
            self.assertEqual(state["pending"]["r"]["processed_prefix_floor"], 32)
            output = NS(scheduled_new_reqs=[NS(req_id="r", num_computed_tokens=16)],
                        scheduled_cached_reqs=NS(req_ids=[], num_computed_tokens=[]))
            self.assertIs(probe._wrap_schedule(lambda self: output)(scheduler), output)
            self.assertEqual(counts["resumed_prefix_gap_exposure_tokens"], 16)
            self.assertFalse(state["pending"])
            # 诊断读取异常仍返回原结果，原方法只执行一次；原方法异常原样传播。
            manager.coordinator = None
            request.status = NS(name="RUNNING")
            self.assertIsNone(probe._wrap_allocate(allocate)(manager, request, 1))
            self.assertEqual(len(calls), 2)
            self.assertEqual(counts["observation_errors"], 1)
            error = RuntimeError("original error")
            def failing(*args, **kwargs):
                calls.append("failure")
                raise error
            with self.assertRaises(RuntimeError) as caught:
                probe._wrap_allocate(failing)(manager, request, 1)
            self.assertIs(caught.exception, error)
            self.assertEqual(len(calls), 3)
        finally:
            probe._ACTIVE.reset(token)
        self.assertIsNone(probe._ACTIVE.get())


if __name__ == "__main__":
    unittest.main()
