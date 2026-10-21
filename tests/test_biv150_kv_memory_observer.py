"""唯一CPU原调用合同：不执行WorkerFL/GPU，只核包装返回/异常/CM语义。"""
from contextlib import contextmanager
import importlib.util
import logging
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "patches/framework/biv150_kv_memory_observer.py"
spec = importlib.util.spec_from_file_location("memory_observer_cpu_contract", path)
O = importlib.util.module_from_spec(spec)
spec.loader.exec_module(O)


class Contract(unittest.TestCase):
    def test_original_call_return_exception_and_context_suppression(self):
        class Suppressed(Exception): pass
        class Propagated(Exception): pass
        self.assertFalse(O.install())
        for mode in ("return", "suppressed", "propagated", "not_activated"):
            with self.subTest(mode=mode):
                calls = dict(parent=0, method=0, enter=0, exit=0, suppressed=0)
                records = []
                failure = Propagated("same exception object")
                before = NS(torch_peak=10, free_memory=900, total_memory=1024,
                            cuda_memory=124, torch_memory=110, non_torch_memory=14,
                            timestamp=1.0, auto_measure=False)
                profile = NS(before_create=before, before_profile=before,
                             after_profile=before, weights_memory=100,
                             torch_peak_increase=0, non_torch_increase=5,
                             non_kv_cache_memory=105, profile_time=0.1)

                @contextmanager
                def original_profile(snapshot, weights_memory):
                    self.assertIs(snapshot, before)
                    self.assertEqual(weights_memory, 100)
                    calls["enter"] += 1
                    try:
                        yield profile
                    except Suppressed:
                        calls["suppressed"] += 1
                    finally:
                        calls["exit"] += 1

                module = NS(logger=logging.getLogger("biv150_memory_observer_cpu_contract"))
                module.memory_profiling_fl = original_profile
                class Worker: pass
                worker = Worker()
                worker.init_snapshot, worker.requested_memory = before, 1000.75

                def original_method(self, argument):
                    calls["method"] += 1
                    self.assert_argument = argument
                    with module.memory_profiling_fl(self.init_snapshot, weights_memory=100) as p:
                        if mode == "suppressed":
                            raise Suppressed()
                        if mode == "propagated":
                            raise failure
                        p.profile_time = 0.2
                    # 和actual WorkerFL一致：CM退出后还会写回profile结果。
                    profile.torch_peak_increase = 100
                    profile.non_kv_cache_memory = 205
                    self.non_torch_memory = 5
                    self.peak_activation_memory = 100
                    self.cudagraph_memory_estimate = 0
                    self.available_kv_cache_memory_bytes = 795.75
                    return 795

                Worker.determine_available_memory = original_method
                original_list = []
                def original_parent(self, argument):
                    calls["parent"] += 1
                    original_list.append(self.worker.determine_available_memory(argument))
                    return original_list
                class Parent: pass
                Parent.determine_available_memory = original_parent
                parent = Parent()
                parent.worker = worker
                wrapped = O._wrap_parent(original_parent, Parent)
                Parent.determine_available_memory = wrapped
                self.assertIs(wrapped.__wrapped__, original_parent)
                loaded = ((module, Worker, original_method, original_profile, {"cpu_contract": True})
                          if mode != "not_activated" else None)
                with patch.object(O, "_emit", lambda event, **fields: records.append((event, fields))), \
                     patch.object(O, "_loaded_context", return_value=loaded,
                                  side_effect=RuntimeError("not naturally loaded") if loaded is None else None):
                    if mode == "propagated":
                        with self.assertRaises(Propagated) as caught:
                            parent.determine_available_memory("literal argument")
                        self.assertIs(caught.exception, failure)
                    else:
                        self.assertIs(parent.determine_available_memory("literal argument"), original_list)
                        self.assertEqual(original_list, [795])
                self.assertEqual((calls["parent"], calls["method"], calls["enter"], calls["exit"]), (1, 1, 1, 1))
                self.assertEqual(calls["suppressed"], int(mode == "suppressed"))
                self.assertEqual(worker.assert_argument, "literal argument")
                self.assertIsNone(O._ACTIVE.get())
                self.assertIs(Parent.determine_available_memory, original_parent)
                self.assertIs(Worker.determine_available_memory, original_method)
                self.assertIs(module.memory_profiling_fl, original_profile)
                self.assertEqual(len(records), 2)
                final_event, final_data = records[-1]
                self.assertTrue(final_data["restored"]["parent_method"])
                if mode == "not_activated":
                    self.assertEqual(records[0][0], "NOT_ACTIVATED")
                    self.assertEqual(final_event, "PARENT_RETURN")
                    continue
                self.assertTrue(final_data["restored"]["worker_method"])
                self.assertTrue(final_data["restored"]["profiling_context"])
                event, data = records[0]
                self.assertEqual(data["profile_context_calls"], 1)
                self.assertEqual(data["before_profile"]["torch_peak"], 10)
                if mode == "propagated":
                    self.assertEqual((event, data["error_type"]), ("DETERMINE_RAISED", "Propagated"))
                else:
                    self.assertEqual((event, data["returned"]), ("DETERMINE_RETURN", 795))
                    self.assertEqual(data["profile"]["torch_peak_increase"], 100)
                    self.assertEqual(data["derived_only_not_new_samples"], {
                        "profile_torch_peak_reconstructed": 110,
                        "graph_deduction_reconstructed": 0.0})
        self.assertFalse(any(name in sys.modules for name in ("torch", "numpy", "vllm")))


if __name__ == "__main__":
    unittest.main()
