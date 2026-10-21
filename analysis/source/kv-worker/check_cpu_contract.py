"""唯一最小CPU合同：命令/预算/epoch/DROP，无Tensor或GPU模拟。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "patches/framework/biv150_kv_worker.py"
spec = importlib.util.spec_from_file_location("kv_worker_cpu_contract", PATH)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
compile(PATH.read_bytes(), str(PATH), "exec")
assert "torch" not in sys.modules and not any(name.startswith("vllm") for name in sys.modules)
key = ["engine", "r0", 1, 1]
command = {"key": key, "kind": "SAVE", "operation_serial": 1,
           "prefix_tokens": 16, "pages": [9], "nbytes": 16 * worker.TOKEN_BYTES}
packet = worker._command(command)
assert packet["pages"] == (9,) and packet["key"] == tuple(key)
for changes in ({"pages": [0]}, {"prefix_tokens": 17}, {"nbytes": 0}, {"operation_serial": 0}):
    try:
        worker._command({**command, **changes})
        raise AssertionError("invalid packet accepted")
    except (ValueError, TypeError):
        pass
worker._budget(command["nbytes"], 16384, {"headroom_bytes": command["nbytes"] + 16384 + worker.HEADROOM_GUARD})
try:
    worker._budget(command["nbytes"], 16384, {"headroom_bytes": command["nbytes"] + 16384 + worker.HEADROOM_GUARD - 1})
    raise AssertionError("insufficient headroom accepted")
except BufferError:
    pass
owner = object()
drop = {**command, "kind": "DROP", "operation_serial": 4, "pages": [], "nbytes": 0}
worker._SLOT = {"key": tuple(key), "nbytes": command["nbytes"], "owner_id": id(owner),
                "last_serial": 3, "settled": True, "phase": "RESTORED"}
held = worker._SLOT
reply = worker.rpc(owner, {**drop, "key": ["engine", "r0", 2, 1]})
assert reply["successful"] is False and worker._SLOT is held and held["phase"] == "RESTORED"
reply = worker.rpc(owner, drop)
assert reply["completed"] is True and reply["successful"] is True and reply["host_held"] is False
assert reply["transferred_bytes"] == 0 and reply["nbytes"] == 0
assert worker._SLOT is None
assert worker.rpc(owner, {"kind": "invalid"})["completed"] is False
assert "torch" not in sys.modules and not any(name.startswith("vllm") for name in sys.modules)
report = {"status": "one_cpu_contract_passed", "worker_sha256": hashlib.sha256(PATH.read_bytes()).hexdigest(),
          "command_and_budget_guards": True, "zero_byte_drop_supported": True,
          "wrong_epoch_does_not_mutate_active_slot": True, "module_imports_no_framework": True,
          "limits": "No Tensor/copy/event/synchronization simulation or GPU execution; needs independent source review and actual device gate."}
Path(__file__).with_name("cpu-contract.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
