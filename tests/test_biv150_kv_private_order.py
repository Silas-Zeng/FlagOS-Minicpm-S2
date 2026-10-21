"""一项CPU合同：私有Block原地映射/host逻辑顺序/拒绝共享与已发布。"""
import importlib
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
PACKAGE = "kv_private_order_cpu"
package = ModuleType(PACKAGE)
package.__path__ = [str(Path(__file__).resolve().parents[1] / "patches/framework")]
sys.modules[PACKAGE] = package
R = importlib.import_module(PACKAGE + ".biv150_kv_protocol")
P = R.protocol


class Contract(unittest.TestCase):
    def test_private_list_mapping_and_guards(self):
        def make():
            tokens = list(range(68))
            key = P.Key("session", "victim", 1, 1)
            tx = P.Transaction(P.plan_snapshot(key, 67, tokens, [1, 2, 3, 4, 5], {}),
                               P.HostSlot(1 << 30))
            op = tx.submit_save()
            tx.acknowledge(P.Receipt(op, op.nbytes, True, True))
            tx.source_free_committed()
            request = NS(request_id="victim")
            pages = [NS(block_id=i, ref_cnt=1, block_hash=None, is_null=False)
                     for i in (12, 11, 7, 8)]
            single = NS(req_to_blocks={"victim": pages}, num_cached_block={"victim": 0},
                        new_block_ids=[99, 12, 11, 7, 8])
            return tx, tokens, {"tx": tx, "request": request}, single, pages

        events = []
        with patch.object(R, "_emit", lambda state, event, **kw: events.append((event, kw))):
            tx, tokens, victim, single, pages = make()
            identity, objects = id(pages), {id(b): b.block_id for b in pages}
            history = tuple(single.new_block_ids)
            old_payload_ids = [b.block_id for b in pages]
            host = tuple(tuple(tokens[i:i + 16]) for i in range(0, 64, 16))
            self.assertTrue(R._order_private_pages({}, victim, single, (pages,)))
            self.assertEqual(id(single.req_to_blocks["victim"]), identity)
            self.assertEqual([b.block_id for b in pages], [7, 8, 11, 12])
            self.assertEqual({id(b): b.block_id for b in pages}, objects)
            self.assertTrue(all(b.ref_cnt == 1 and b.block_hash is None for b in pages))
            self.assertEqual(tuple(single.new_block_ids), history)
            self.assertEqual(old_payload_ids, [12, 11, 7, 8])
            self.assertEqual(tx.snapshot.source_pages, (1, 2, 3, 4))
            self.assertEqual(events[-1][1]["increasing_runs_before"], 3)
            self.assertEqual(events[-1][1]["increasing_runs_after"], 2)
            # host行i仍是逻辑token页i，不能排序host本身；新表与恢复映射统一。
            destination = tuple(b.block_id for b in pages)
            _, fresh = P.split_fresh_zero_ids([99], single.new_block_ids, destination,
                                              pending_zero=False)
            tx.bind_private_allocation(tx.snapshot.key, tokens, destination, fresh)
            zero = tx.submit_zero()
            self.assertEqual(zero.pages, destination)
            tx.acknowledge(P.Receipt(zero, zero.nbytes, True, True))
            restore = tx.submit_restore()
            fake_storage = dict(zip(restore.pages, host))
            self.assertEqual(tuple(t for b in pages for t in fake_storage[b.block_id]), tuple(tokens[:64]))
            tx.acknowledge(P.Receipt(restore, restore.nbytes, True, True))
            tx.publish(tx.snapshot.key, tokens)
            self.assertFalse(R._order_private_pages({}, victim, single, (pages,)))
            self.assertEqual(tuple(tuple(tokens[i:i + 16]) for i in range(0, 64, 16)), host)
            # 排序的必要所有权/生命周期条件任一不满足，保旧路径且不改list。
            for invalid in ("alias", "cached", "shared", "hashed", "pending", "bound", "duplicate"):
                with self.subTest(invalid=invalid):
                    tx, tokens, victim, single, pages = make()
                    if invalid == "alias":
                        single.req_to_blocks["victim"] = list(pages)
                    elif invalid == "cached":
                        single.num_cached_block["victim"] = 1
                    elif invalid == "shared":
                        pages[0].ref_cnt = 2
                    elif invalid == "hashed":
                        pages[0].block_hash = b"cached"
                    elif invalid == "pending":
                        tx.pending_frames.add(9)
                    elif invalid == "bound":
                        tx.bind_private_allocation(tx.snapshot.key, tokens, [12, 11, 7, 8], [12, 11, 7, 8])
                    else:
                        pages[-1].block_id = pages[0].block_id
                    before = tuple(id(b) for b in pages)
                    self.assertFalse(R._order_private_pages({}, victim, single, (pages,)))
                    self.assertEqual(tuple(id(b) for b in pages), before)
        self.assertFalse(any(name in sys.modules for name in ("torch", "numpy", "vllm")))


if __name__ == "__main__":
    unittest.main()
