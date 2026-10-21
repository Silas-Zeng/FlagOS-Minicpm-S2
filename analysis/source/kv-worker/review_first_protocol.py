"""只读200957首次实际事务原件；确认SAVE/DROP，不冒称恢复或性能通过。"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/framework/20261021T200957Z-kv-protocol-context16k-long"
CONTROL = RUN.with_name(RUN.name + "-control")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


manifest = read(RUN / "manifest.json")
sources = read(CONTROL / "source-sha256.json")
assert len(sources) == 416 and all(sha(CONTROL / "plugin-source" / name) == value for name, value in sources.items())
assert sources["vllm_fl/patches/biv150_kv_worker.py"] == "31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf"
assert sources["vllm_fl/patches/biv150_kv_protocol.py"] == "50375e899acbdcee15d3cdec2ecd77875fb355c56ccbfa663271509982ddc19a"
assert sources["vllm_fl/patches/biv150_kv_transaction.py"] == "616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13"
assert sources["vllm_fl/worker/model_runner.py"] == "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
assert sources["vllm_fl/__init__.py"] == "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8"
assert sha(CONTROL / "prepare_kv_protocol_source.py") == "89191b57542e8c2e44eb03b8ebee876f083f3e399e1085149ff0b6a36b49fa42"
assert sha(CONTROL / "launch.sh") == "e738b736829172a6cbd525cd0d5e5f9dc343a21e0ffe8bcf1c113bbe4a5db47c"
assert sha(RUN / "screen-driver.py") == "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9"
pack = read(CONTROL / "plugin-source/innovation-source.json")
assert len(pack["input_sha256"]) == 410 and len(pack["changes"]) == 6
assert {k: v for k, v in sources.items() if k != "innovation-source.json"} == pack["output_sha256_excluding_this_manifest"]
assert (RUN / "exit-code").read_text().strip() == "0"
assert read(RUN / "launch-command.json") == manifest["server_command"]
assert manifest["context_long_screen"] and manifest["seed"] == 721201
assert not any(manifest[k] for k in ("native_profile", "host_profile", "decode_screen", "context_screen", "smoke_only"))
assert "BIV150_KV_VERIFY_RESTORE=1" in (CONTROL / "command.txt").read_text()
load, = read(RUN / "load-commands.json")
assert load[3:] == ["context-16k-long", "16384", "1024", "64", "32", "721201"]
raw_path, = (RUN / "context-16k-long/results").glob("*.json")
raw = read(raw_path)
assert [raw[k] for k in ("completed", "failed", "total_input_tokens", "total_output_tokens")] == [32, 0, 524288, 32768]
for phase in ("before", "after"):
    cpu = read(RUN / ("cpu-" + phase + "-context-16k-long.json"))
    assert int(cpu["cpu.cfs_quota_us"]) / int(cpu["cpu.cfs_period_us"]) == 6
with (RUN / "gpu.csv").open(encoding="utf-8") as stream:
    gpu = list(csv.DictReader(stream))
assert gpu and all(row["memory.total"].strip() == "32768 MiB" for row in gpu)
log = (RUN / "server.log").read_text(encoding="utf-8", errors="replace")
events = [json.loads(line.split("BIV150_KV_PROTOCOL ", 1)[1]) for line in log.splitlines() if "BIV150_KV_PROTOCOL {" in line]
assert [row["event"] for row in events] == ["FIRST_CHECKED", "RPC_ACK", "SAVE_ACK_FREE", "RPC_ACK"]
assert events[0]["eligible"] is True
save, free, drop = events[1:]
assert save["command"]["kind"] == "SAVE" and drop["command"]["kind"] == "DROP"
for row in (save, drop):
    assert row["worker_response"]["completed"] is True and row["worker_response"]["successful"] is True
    assert row["worker_response"]["worker_pid"] == row["pid"] == 215606
    assert all(row["command"][k] == row["worker_response"][k] for k in ("key", "operation_serial", "kind", "pages", "nbytes"))
assert save["command"]["key"] == drop["command"]["key"]
assert [save["command"]["operation_serial"], drop["command"]["operation_serial"]] == [1, 2]
pages = save["command"]["pages"]
assert len(pages) == len(set(pages)) == 1044 and min(pages) > 0
assert save["command"]["prefix_tokens"] == 16704
assert save["command"]["nbytes"] == save["worker_response"]["transferred_bytes"] == 16704 * 43008 == 718405632
runs = sum(i == 0 or pages[i] != pages[i - 1] + 1 for i in range(len(pages)))
assert runs == 24 and save["worker_response"]["copy_calls"] == runs * 42 == 1008
assert save["worker_response"]["diagnostic_verify_requested"] is True
assert save["worker_response"]["diagnostic_extra_pinned_bytes"] == 718405632 // 42 == 17104896
assert free["saved"] == 1 and drop["restore_skips"] == 1 and drop["restored"] == drop["published"] == 0
assert drop["command"]["nbytes"] == 0 and drop["command"]["pages"] == []
assert drop["worker_response"]["host_held"] is False and drop["worker_response"]["host_payload_bytes"] == 0
assert "GPU KV cache size: 521,936 tokens" in log
metrics = {}
for phase in ("before", "after"):
    text = (RUN / ("metrics-" + phase + "-context-16k-long.prom")).read_text(encoding="utf-8")
    metrics[phase] = sum(map(float, re.findall(r'^vllm:num_preemptions_total\{[^\n]*\} ([\d.e+\-]+)$', text, re.M)))
hp = ROOT / "scripts/remote/snapshot_tuning_db.py"
assert sha(hp) == "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2"
spec = importlib.util.spec_from_file_location("first_protocol_db", hp)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
database = {}
for phase in ("before", "after"):
    directory = CONTROL / ("db-" + phase)
    saved = read(directory / "manifest.json")
    fingerprint = helper.fingerprint((directory / "snapshot.sqlite").resolve())
    value = {"snapshot_sha256": sha(directory / "snapshot.sqlite"),
             **{k: fingerprint[k] for k in ("schema_sha256", "logical_content_sha256", "table_count", "row_count")}}
    assert all(value[k] == saved[k] for k in value)
    database[phase] = value
post = read(RUN / "postflight-full.json")
assert post["source_count"] == 416 and post["source_failures"] == []
assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values())
assert "No running processes found" in post["ixsmi"]
assert all(value is None or "\nState:\tZ " in value for value in post["owned_process_status"].values())
assert sha(RUN / "postflight-sources/triton_unified_attention.py") == "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
report = {"status": "verified_save_and_drop_only_no_restore", "run": RUN.name,
          "source_count_rehashed": 416, "source_manifest_sha256": sha(CONTROL / "source-sha256.json"),
          "manifest_sha256": sha(RUN / "manifest.json"), "raw_sha256": sha(raw_path), "server_log_sha256": sha(RUN / "server.log"),
          "saved_prefix_tokens": 16704, "save_bytes": 718405632, "logical_pages": 1044,
          "physical_runs": runs, "copy_calls": 1008, "saved_then_source_free_recorded": True,
          "drop_host_released": True, "restore_skip_count_at_drop": 1,
          "no_zero_restore_verification_or_consumer_events": True,
          "save_memory_observations": {k: save["worker_response"][k] for k in ("memory_before", "memory_after_pin", "host_payload_bytes", "diagnostic_extra_pinned_bytes")},
          "database": database, "database_unchanged": database["before"] == database["after"],
          "cpu_quota": 6, "physical_memory_mib": 32768, "kv_tokens": 521936, "preemptions": metrics,
          "completed": 32, "failed": 0, "tokens": [524288, 32768],
          "diagnostic_duration_s": raw["duration"], "diagnostic_total_tps": raw["total_token_throughput"],
          "diagnostic_ttft_ms": raw["mean_ttft_ms"], "postflight_utc": post["utc"], "idle_verified": True,
          "shutdown_error_lines": [line for line in log.splitlines() if "ERROR" in line or "EngineDeadError" in line],
          "rejection_cause": "仅知restore_skips1：冻结代码复合precheck或external-prefix allocation None，日志不能继续区分。",
          "limits": ["真实SAVE提交/完成与原free已记录，不是实际恢复/回读/consumer通过。",
                     "临时拒绝直接DROP会丢失后续机会；先保留旧负例，不能反推未记录guard值。",
                     "诊断含ENV1/日志/copy，不作为性能结论；无新accuracy或默认合并。"]}
destination = Path(__file__).with_name("first-protocol-review.json")
destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ("status", "source_count_rehashed", "saved_prefix_tokens", "save_bytes", "copy_calls", "preemptions", "database_unchanged", "postflight_utc")}, ensure_ascii=True, indent=2))
