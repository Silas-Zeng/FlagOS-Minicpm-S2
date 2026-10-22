"""唯一CPU路由/生命周期合同；stub不证明SDK、GPU字节、实际Tensor或stream。"""
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "patches/framework/candidates/biv150_kv_pitched_save_worker.py"
BASE = ROOT / "patches/framework/candidates/biv150_kv_full_restore_worker.py"


def load_worker():
    spec = importlib.util.spec_from_file_location("pitched_save_cpu_contract", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Buffer:
    def __init__(self, data=None):
        self.data = data


class PitchedSaveWorkerContract(unittest.TestCase):
    def test_only_save_routing_refs_verification_and_error_settle(self):
        source = SOURCE.read_text(encoding="utf-8")
        original = BASE.read_text(encoding="utf-8")
        restored = source.replace(
            '"""独立完整R等差SAVE候选worker；只改5d9a的SAVE，显式RPC才启用。',
            '"""独立RESTORE_FULL候选worker；显式RPC才启用，无安装或框架导入。', 1)
        start = restored.index('PITCHED_RUNTIME = "')
        stop = restored.index("def _full_restore_plan(", start)
        restored = restored[:start] + restored[stop:]
        restored = restored.replace(
            '            info = _save_pitched(torch, raw, slot, packet, pool)\n'
            '            _finish(torch, slot)\n'
            '            info.update(_verify_saved_source(torch, policy, raw, slot, packet))\n',
            '            info = _copy(policy, raw, slot["host"], packet["pages"], range(count))\n'
            '            _finish(torch, slot)\n', 1)
        self.assertEqual(restored, original)

        for mode in ("verify", "no_verify", "partial_settled", "partial_unsettled", "verify_mismatch"):
            with self.subTest(mode=mode):
                worker = load_worker()
                raw = [Buffer(index + 10) for index in range(42)]
                calls = []
                wrapper = SimpleNamespace()
                stream = SimpleNamespace(cuda_stream=17)
                cuda = SimpleNamespace(sync_count=0)

                def synchronize():
                    cuda.sync_count += 1
                    calls.append("device_fence")
                    if mode == "partial_unsettled" and cuda.sync_count > 1:
                        raise RuntimeError("stub device cannot settle")

                class Event:
                    def record(self):
                        calls.append("event_record_17")

                    def synchronize(self):
                        calls.append("event_complete")

                cuda.synchronize = synchronize
                cuda.Event = Event
                cuda.current_stream = lambda device: stream if device == 0 else None
                torch = SimpleNamespace(cuda=cuda, uint8="uint8", empty=lambda *a, **kw: Buffer(),
                                        equal=lambda a, b: a.data == b.data)
                runner = SimpleNamespace(requests={"request": SimpleNamespace(block_ids=([2, 3],))})
                worker._context = lambda candidate: (torch, runner, object(), raw, tuple(range(42)), 64)
                worker._memory_headroom = lambda: {"headroom_bytes": 4 << 30}
                plan = SimpleNamespace(segments=(object(),))

                class Runtime:
                    @staticmethod
                    def make_plan(ids, pool):
                        self.assertEqual((ids, pool), ((2, 3), 64))
                        return plan

                    @staticmethod
                    def prepare_save(sources, destinations, actual_plan, *, max_pitch):
                        self.assertIs(sources, raw)
                        self.assertEqual((len(sources), len(destinations), max_pitch), (42, 42, 1 << 30))
                        self.assertIs(actual_plan, plan)
                        self.assertLess(calls.index("device_fence"), calls.index("load_in_save"))
                        return SimpleNamespace(keepalive=tuple(sources) + tuple(destinations), descriptors=object())

                class Bridge:
                    def max_pitch(self, *, device):
                        if device != 0:
                            raise AssertionError("wrong device")
                        return 1 << 30

                    def submit(bridge, prepared, *, stream_handle):
                        calls.append("candidate_submit")
                        self.assertIs(worker._SLOT["save_prepared"], prepared)
                        self.assertIs(worker._SLOT["save_bridge"], bridge)
                        self.assertIs(worker._SLOT["save_stream"], stream)
                        self.assertEqual(stream_handle, 17)
                        for index, saved in enumerate(worker._SLOT["host"]):
                            saved.data = raw[index].data
                        if mode.startswith("partial_"):
                            raise RuntimeError("stub partial native error")
                        return {"submitted_bytes": 32 * worker.TOKEN_BYTES, "copy_calls": 42,
                                "linear_calls": 42, "pitched_calls": 0, "fallback_pitched_segments": 0,
                                "original_c95f_calls": 42, "completion_ack": False}

                bridge = Bridge()

                def assets(slot):
                    calls.append("load_in_save")
                    self.assertIs(slot, worker._SLOT)
                    return Runtime, bridge

                def original_copy(policy, sources, destinations, source_ids, destination_ids):
                    calls.append("source_verify_copy")
                    self.assertEqual((tuple(source_ids), tuple(destination_ids)), ((2, 3), (0, 1)))
                    self.assertEqual((len(sources), len(destinations)), (1, 1))
                    destinations[0].data = -1 if mode == "verify_mismatch" else sources[0].data
                    return {"copy_calls": 1, "submitted_bytes": 2 * worker.PAGE_BYTES}

                worker._pitched_assets = assets  # 只stub native loader；不加载SO/SDK。
                worker._copy = original_copy   # 原c95f byte正确性由实际设备门负责。
                packet = {"key": ["session", "request", 1, 1], "kind": "SAVE", "operation_serial": 1,
                          "prefix_tokens": 32, "pages": [2, 3], "nbytes": 32 * worker.TOKEN_BYTES}
                self.assertEqual(calls, [])
                with patch.dict(os.environ, {worker.VERIFY_ENV: "0" if mode == "no_verify" else "1"}):
                    result = worker.rpc(wrapper, packet)
                slot = worker._SLOT
                self.assertIs(slot["save_bridge"], bridge)
                self.assertEqual(len(slot["save_prepared"].keepalive), 84)
                self.assertEqual(calls.count("load_in_save"), 1)
                self.assertEqual(calls.count("candidate_submit"), 1)

                if mode.startswith("partial_") or mode == "verify_mismatch":
                    self.assertIs(result["successful"], False)
                    self.assertEqual(result["completed"], mode != "partial_unsettled")
                    self.assertEqual(slot["phase"], "FAILED")
                    self.assertIs(slot["save_prepared"].keepalive[0], raw[0])
                    self.assertEqual(calls.count("source_verify_copy"), 1 if mode == "verify_mismatch" else 0)
                    self.assertEqual(calls.count("candidate_submit"), 1)  # 不降级/不重试。
                    if mode == "partial_unsettled":
                        refused = worker.rpc(wrapper, {**packet, "kind": "DROP", "operation_serial": 2,
                                                       "pages": [], "nbytes": 0})
                        self.assertFalse(refused["successful"])
                        self.assertIs(worker._SLOT, slot)
                    continue

                self.assertTrue(result["successful"] and result["completed"])
                self.assertEqual(slot["phase"], "SAVED")
                self.assertIs(result["full_restore_supported"], True)
                self.assertIs(result["save_submission_completion_ack"], False)
                self.assertNotIn("completion_ack", result)
                if mode == "verify":
                    self.assertEqual(calls.count("source_verify_copy"), 42)
                    self.assertTrue(result["save_verification_performed"] and result["save_verification_passed"])
                    self.assertEqual(result["save_verification_bytes"], packet["nbytes"])
                    self.assertEqual(result["save_verification_layers"], 42)
                    self.assertEqual(calls.count("event_complete"), 43)
                    self.assertIsNotNone(slot["verify_buffer"])  # 后继FULL仍复用原buffer。
                else:
                    self.assertIs(result["save_verification_performed"], False)
                    self.assertEqual(calls.count("source_verify_copy"), 0)
                    self.assertEqual(calls.count("event_complete"), 1)
                dropped = worker.rpc(wrapper, {**packet, "kind": "DROP", "operation_serial": 2,
                                               "pages": [], "nbytes": 0})
                self.assertTrue(dropped["successful"] and dropped["completed"])
                self.assertIsNone(worker._SLOT)
                self.assertEqual(calls.count("load_in_save"), 1)


if __name__ == "__main__":
    unittest.main()
