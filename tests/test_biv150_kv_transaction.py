"""一项必要CPU合同：ack/epoch/旧frame/清零/取消/回滚所有权。非设备证明。"""
import importlib.util
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / "patches/framework/biv150_kv_transaction.py"
SPEC = importlib.util.spec_from_file_location("kv_transaction_cpu", PATH)
P = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = P
SPEC.loader.exec_module(P)


class Contract(unittest.TestCase):
    def test_transaction_fences_and_ownership(self):
        key = P.Key("engine-1", "same-id", 1, 1)
        other = P.Key("engine-1", "same-id", 2, 1)
        tokens = tuple(range(36))
        plan = P.plan_snapshot(key, 35, tokens, [5, 6, 7], {9: 1})
        self.assertEqual(plan.prefix_tokens, 32)
        self.assertEqual(plan.source_pages, (5, 6))
        self.assertEqual(plan.nbytes, 32 * 43008)
        preserved, owned = P.split_fresh_zero_ids([88], [88, 102, 101], [101, 102])
        self.assertEqual(preserved, (88,))
        self.assertEqual(owned, (102, 101))
        with self.assertRaises(RuntimeError):
            P.split_fresh_zero_ids([101], [101, 101, 102], [101, 102])
        # FullAttention needs_zero=False不drain，历史ID重复是合法复用。
        self.assertEqual(P.split_fresh_zero_ids([101], [101, 101, 102],
                         [101, 102], pending_zero=False), ((101,), (101, 102)))
        slot = P.HostSlot(plan.nbytes)
        tx = P.Transaction(plan, slot)
        ack = lambda op, ok=True: P.Receipt(op, op.nbytes if ok else 0, True, ok)
        save = tx.submit_save()
        self.assertFalse(tx.source_free_permitted())
        with self.assertRaises(RuntimeError):
            tx.acknowledge(P.Receipt(save, save.nbytes, False, True))
        with self.assertRaises(RuntimeError):
            tx.close()
        stale = P.Operation(other, save.serial, save.kind, save.pages, save.nbytes)
        with self.assertRaises(RuntimeError):
            tx.acknowledge(ack(stale))
        tx.acknowledge(ack(save))
        self.assertTrue(tx.source_free_permitted())
        tx.source_free_committed()
        with self.assertRaises(RuntimeError):
            tx.bind_private_allocation(key, tokens, [101, 102], [101, 102])
        with self.assertRaises(RuntimeError):
            tx.frame_processed(other, 9)
        tx.frame_processed(key, 9)
        changed = (-1,) + tokens[1:]
        with self.assertRaises(ValueError):
            tx.bind_private_allocation(key, changed, [101, 102], [101, 102])
        tx.bind_private_allocation(key, tokens, [101, 102], [101, 102])
        with self.assertRaises(RuntimeError):
            tx.submit_restore()
        tx.acknowledge(ack(tx.submit_zero()))
        restore = tx.submit_restore()
        with self.assertRaises(RuntimeError):
            tx.publish(key, tokens)
        tx.acknowledge(ack(restore))
        committed = tx.publish(key, tokens)
        self.assertEqual(committed["computed_tokens"], 32)
        self.assertEqual(committed["sampling_calls"], 0)
        tx.cancel()  # 发布后只能由原scheduler收回页，禁止协议私有rollback。
        with self.assertRaises(RuntimeError):
            tx.release_private_allocation()
        tx.close()
        self.assertEqual(slot.used_bytes, 0)

        second = P.plan_snapshot(other, 35, tokens, [15, 16, 17], {})
        tx = P.Transaction(second, slot)
        save2 = tx.submit_save()
        tx.cancel()
        self.assertFalse(tx.source_free_permitted())
        with self.assertRaises(RuntimeError):
            tx.close()
        with self.assertRaises(RuntimeError):
            tx.acknowledge(ack(save))  # 相同request ID、旧incarnation不能解锁。
        tx.acknowledge(ack(save2))
        tx.source_free_committed()
        tx.close()

        tx = P.Transaction(second, slot)
        with self.assertRaises(BufferError):
            P.Transaction(plan, slot)
        tx.discard()
        tx.close()
        with self.assertRaises(BufferError):
            P.Transaction(plan, P.HostSlot(plan.nbytes - 1))

        tx = P.Transaction(second, slot)
        retry_save = tx.submit_save()
        with self.assertRaises(RuntimeError):
            tx.acknowledge(ack(save2))  # 即使调用方误复用Key，旧lease ACK也不能解锁。
        tx.acknowledge(ack(retry_save))
        tx.source_free_committed()
        tx.bind_private_allocation(other, tokens, [201, 202], [201, 202])
        tx.acknowledge(ack(tx.submit_zero()))
        failed = tx.submit_restore()
        with self.assertRaises(RuntimeError):
            tx.release_private_allocation()
        tx.acknowledge(ack(failed, False))  # 失败仍须真实完成/settle，才可回滚。
        self.assertEqual(tx.release_private_allocation(), (201, 202))
        with self.assertRaises(RuntimeError):
            tx.close()
        tx.private_allocation_released()
        tx.close()
        self.assertEqual(slot.used_bytes, 0)
        tx = P.Transaction(second, slot)
        tx.acknowledge(ack(tx.submit_save()))
        tx.source_free_committed()
        tx.bind_private_allocation(other, tokens, [301, 302], [301, 302])
        tx.acknowledge(ack(tx.submit_zero()))
        tx.acknowledge(ack(tx.submit_restore()))
        # 原后续allocate失败或没形成SchedulerOutput时，不得提前publish。
        tx.rollback_unpublished()
        self.assertEqual(tx.release_private_allocation(), (301, 302))
        tx.private_allocation_released()
        tx.close()
        self.assertFalse(any(name in sys.modules for name in ("torch", "vllm", "numpy")))


if __name__ == "__main__":
    unittest.main()
