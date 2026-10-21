"""FULL214400核心worker/byte/consumer独立审；不重复整树/DB/CPU套件。"""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/framework/20261021T214400Z-kv-full-restore-context16k-long"
CONTROL = RUN.with_name(RUN.name + "-control")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def runs(ids):
    return sum(i == 0 or value != ids[i - 1] + 1 for i, value in enumerate(ids))


pins = {"biv150_kv_worker.py": "5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477",
        "biv150_kv_transaction.py": "84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883",
        "biv150_kv_protocol.py": "1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8",
        "biv150_kv_page_copy.py": "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c"}
for name, expected in pins.items():
    assert sha(CONTROL / "plugin-source/vllm_fl/patches" / name) == expected
assert (RUN / "exit-code").read_text().strip() == "0"
assert "BIV150_KV_VERIFY_RESTORE=1 " in (CONTROL / "command.txt").read_text()
log = (RUN / "server.log").read_text(encoding="utf-8", errors="replace")
events = [json.loads(line.split("BIV150_KV_PROTOCOL ", 1)[1]) for line in log.splitlines() if "BIV150_KV_PROTOCOL {" in line]
acks = [row for row in events if row["event"] == "RPC_ACK"]
assert [row["command"]["kind"] for row in acks] == ["SAVE", "RESTORE_FULL", "DROP"]
assert [row["command"]["operation_serial"] for row in acks] == [1, 2, 3]
save, full, drop = acks
key, prefix = save["command"]["key"], save["command"]["prefix_tokens"]
assert type(prefix) is int and prefix >= 16 and prefix % 16 == 0
pages, nbytes = prefix // 16, prefix * 43008
for row in acks:
    command, response = row["command"], row["worker_response"]
    assert command["key"] == key and command["prefix_tokens"] == prefix
    assert all(response[k] == command[k] for k in ("key", "operation_serial", "kind", "pages", "nbytes", "prefix_tokens"))
    assert response["worker_pid"] == row["pid"] == save["pid"]
    assert response["successful"] is True and response["completed"] is True and response["error"] is None
    assert response["transferred_bytes"] == command["nbytes"]
    if command["kind"] != "DROP":
        assert command["nbytes"] == nbytes and len(command["pages"]) == len(set(command["pages"])) == pages
        assert min(command["pages"]) > 0
saved, restored = save["worker_response"], full["worker_response"]
assert saved["full_restore_supported"] is True
assert [saved[k] for k in ("saved_layers", "saved_page_bytes", "saved_prefix_pages", "saved_bytes")] == [42, 16384, pages, nbytes]
assert saved["copy_calls"] == runs(save["command"]["pages"]) * 42
assert restored["zero_stage_executed"] is False and restored["zero_calls"] == 0
assert restored["destination_bound"] is True and restored["full_coverage"] is True
assert restored["full_coverage_bytes"] == restored["submitted_bytes"] == nbytes
assert restored["copy_calls"] == runs(full["command"]["pages"]) * 42
assert restored["diagnostic_verify_requested"] is True and restored["verification_performed"] is True
assert restored["verification_passed"] is True and restored["verification_readback_bytes"] == nbytes
assert restored["verification_copy_calls"] == restored["copy_calls"]
assert all(row["host_held"] is True and row["host_payload_bytes"] == nbytes for row in (saved, restored))
assert drop["command"]["pages"] == [] and drop["command"]["nbytes"] == 0
assert drop["worker_response"]["host_held"] is False and drop["worker_response"]["host_payload_bytes"] == 0
runner, = [row for row in events if row["event"] == "RUNNER_RESUME_STATE_CHECKED"]
consumer, = [row for row in events if row["event"] == "RESUME_OUTPUT_PROCESSED"]
assert len(runner["checks"]) == 6 and all(value is True for value in runner["checks"].values())
assert runner["key"] == consumer["key"] == key and consumer["after_original_update"] is True
assert consumer["scheduled_tokens"] > 0 and runner["before_attention"] is True
assert consumer["saved"] == consumer["restored"] == consumer["published"] == 1 and consumer["rollbacks"] == 0
post = read(RUN / "postflight-full.json")
assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values())
assert "No running processes found" in post["ixsmi"]
raw_path, = (RUN / "context-16k-long/results").glob("*.json")
raw = read(raw_path)
assert [raw[k] for k in ("completed", "failed", "total_input_tokens", "total_output_tokens")] == [32, 0, 524288, 32768]
report = {"status": "verified_core_full_worker_ack_byte_readback_and_consumer",
          "run": RUN.name, "worker_assets_rehashed": pins, "server_log_sha256": sha(RUN / "server.log"),
          "transaction_key": key, "prefix_tokens": prefix, "logical_pages": pages, "nbytes": nbytes,
          "source_runs": runs(save["command"]["pages"]), "destination_runs": runs(full["command"]["pages"]),
          "save_copy_calls": saved["copy_calls"], "full_copy_calls": restored["copy_calls"], "zero_calls": 0,
          "verification_readback_bytes": nbytes, "verification_copy_calls": restored["verification_copy_calls"],
          "verified_layers_from_pinned_worker": 42, "verification_passed": True,
          "runner_checks": runner["checks"], "consumer_scheduled_tokens": consumer["scheduled_tokens"],
          "fast_rejects": consumer["fast_rejects"], "host_released": True, "diagnostic_only": True,
          "raw_sha256": sha(raw_path), "completed": 32, "failed": 0,
          "finished_utc": (RUN / "finished-at.txt").read_text().strip(), "postflight_utc": post["utc"],
          "limits": ["只独立复核四个核心worker/事务/协议/copy源码和实际ACK/byte/consumer，不重复systems2071整树/DB/系统身份审计。",
                     "无ZERO来自真实命令/ACK和被pin FULL分支，非额外GPU profiling内核计数。",
                     "VERIFY1只证本次恢复，不算性能/完整accuracy或多victim、取消覆盖。"]}
destination = Path(__file__).with_name("full-restore-214400-worker-core-review.json")
with destination.open("x", encoding="utf-8") as output:
    json.dump(report, output, ensure_ascii=False, indent=2)
    output.write("\n")
print(json.dumps({k: report[k] for k in ("status", "prefix_tokens", "nbytes", "zero_calls", "verification_passed", "consumer_scheduled_tokens", "fast_rejects")}, ensure_ascii=True))
