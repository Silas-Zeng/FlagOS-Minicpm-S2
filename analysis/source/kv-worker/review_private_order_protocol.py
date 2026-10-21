"""等204159完整原件后运行；核实际排序/回读/consumer，不预设页数或DB不变。"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/framework/20261021T204159Z-kv-page-order-context16k-long"
CONTROL = RUN.with_name(RUN.name + "-control")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def runs(pages):
    return sum(i == 0 or page != pages[i - 1] + 1 for i, page in enumerate(pages))


sources = read(CONTROL / "source-sha256.json")
assert len(sources) == 416
assert all(sha(CONTROL / "plugin-source" / name) == value for name, value in sources.items())
expected = {
    "vllm_fl/patches/biv150_kv_worker.py": "31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf",
    "vllm_fl/patches/biv150_kv_protocol.py": "0e2115d0fbdedea64d1b911c0d6ae3b359f178004d844a8dd8088dfa4388fb86",
    "vllm_fl/patches/biv150_kv_transaction.py": "616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13",
    "vllm_fl/patches/biv150_kv_page_copy.py": "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c",
    "vllm_fl/worker/model_runner.py": "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1",
    "vllm_fl/__init__.py": "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8",
}
assert all(sources[name] == value for name, value in expected.items())
assert sha(CONTROL / "prepare_kv_protocol_source.py") == "4c8ae1d50a113fa35f2642dafa4f60f9a2790187e327a369e063cdb587b3790b"
assert sha(CONTROL / "launch.sh") == "8d7bdd79a3c0e937694b8a9fe910416cba67f7c075eb46378e2f71abf2e6c6b7"
assert sha(RUN / "screen-driver.py") == "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9"
pack = read(CONTROL / "plugin-source/innovation-source.json")
assert len(pack["input_sha256"]) == 410 and len(pack["changes"]) == 6
assert {k: v for k, v in sources.items() if k != "innovation-source.json"} == pack["output_sha256_excluding_this_manifest"]
manifest = read(RUN / "manifest.json")
assert (RUN / "exit-code").read_text().strip() == "0"
assert read(RUN / "launch-command.json") == manifest["server_command"]
assert manifest["server_command"] == ["vllm", "serve", "/workspace/MiniCPM5-2B", "--port", "9031", "--compilation-config", '{"cudagraph_mode": "FULL_DECODE_ONLY"}', "--served-model-name", "minicpm", "--gpu-memory-utilization", "0.85", "--max-model-len", "131072"]
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
assert [x["event"] for x in events if x["event"] != "RESTORE_DEFERRED"] == ["FIRST_CHECKED", "RPC_ACK", "SAVE_ACK_FREE", "PRIVATE_PAGES_ORDERED", "RPC_ACK", "RPC_ACK", "RESTORE_ACK", "RESUME_PUBLISHED", "RPC_ACK", "RUNNER_RESUME_STATE_CHECKED", "RESUME_OUTPUT_PROCESSED"]
assert events[0]["eligible"] is True
pid = events[0]["pid"]
acks = [x for x in events if x["event"] == "RPC_ACK"]
assert [x["command"]["kind"] for x in acks] == ["SAVE", "ZERO", "RESTORE", "DROP"]
key = acks[0]["command"]["key"]
prefix_tokens = acks[0]["command"]["prefix_tokens"]
assert prefix_tokens > 0 and prefix_tokens % 16 == 0
page_count, payload_bytes = prefix_tokens // 16, prefix_tokens * 43008
for serial, row in enumerate(acks, 1):
    cmd, response = row["command"], row["worker_response"]
    assert cmd["key"] == key and cmd["operation_serial"] == serial
    assert response["completed"] is True and response["successful"] is True and response["error"] is None
    assert row["pid"] == response["worker_pid"] == pid
    assert all(cmd[k] == response[k] for k in ("key", "operation_serial", "kind", "pages", "nbytes", "prefix_tokens"))
    assert response["transferred_bytes"] == cmd["nbytes"]
    if cmd["kind"] != "DROP":
        assert len(cmd["pages"]) == len(set(cmd["pages"])) == page_count and min(cmd["pages"]) > 0
        assert cmd["prefix_tokens"] == prefix_tokens and cmd["nbytes"] == payload_bytes
        assert response["submitted_bytes"] == cmd["nbytes"]
save, zero, restore, drop = acks
assert save["worker_response"]["copy_calls"] == runs(save["command"]["pages"]) * 42
assert zero["command"]["pages"] == restore["command"]["pages"]
destination = zero["command"]["pages"]
assert destination == sorted(destination)
destination_runs = runs(destination)
ordered, = [x for x in events if x["event"] == "PRIVATE_PAGES_ORDERED"]
assert ordered["prefix_tokens"] == prefix_tokens and ordered["page_count"] == page_count
assert ordered["increasing_runs_after"] == destination_runs < ordered["increasing_runs_before"] <= page_count
assert ordered["same_page_ids"] is True and ordered["same_block_objects"] is True and ordered["owned_list_identity"] is True
assert ordered["host_logical_order_changed"] is False and ordered["future_free_order_may_change"] is True
assert zero["worker_response"]["zero_calls"] == destination_runs * 42
verify = restore["worker_response"]
assert verify["copy_calls"] == verify["verification_copy_calls"] == destination_runs * 42
assert verify["verification_performed"] is True and verify["verification_passed"] is True
assert verify["verification_readback_bytes"] == payload_bytes
assert verify["diagnostic_verify_requested"] is True and verify["diagnostic_extra_pinned_bytes"] == payload_bytes // 42
assert drop["command"]["nbytes"] == 0 and drop["command"]["pages"] == []
assert drop["worker_response"]["host_held"] is False and drop["worker_response"]["host_payload_bytes"] == 0
defers = [x for x in events if x["event"] == "RESTORE_DEFERRED"]
assert len(defers) <= 1
assert all(x["host_retained"] is True and x["allocator_required_blocks_observed"] is False for x in defers)
state, consumed = events[-2:]
assert len(state["checks"]) == 6 and all(state["checks"].values())
assert state["key"] == consumed["key"] == key
assert state["before_attention"] is True and state["gpu_completion_claimed"] is False
assert consumed["after_original_update"] is True and consumed["scheduled_tokens"] > 0
assert all(consumed[k] == value for k, value in {"saved": 1, "restored": 1, "published": 1, "rollbacks": 0}.items())
kv_match, = re.findall(r"GPU KV cache size: ([\d,]+) tokens", log)
kv_tokens = int(kv_match.replace(",", ""))
assert all(max(row["command"]["pages"], default=0) < kv_tokens // 16 for row in acks)
metrics = {}
for phase in ("before", "after"):
    text = (RUN / ("metrics-" + phase + "-context-16k-long.prom")).read_text()
    metrics[phase] = sum(map(float, re.findall(r'^vllm:num_preemptions_total\{[^\n]*\} ([\d.e+\-]+)$', text, re.M)))
hp = CONTROL / "snapshot_tuning_db.py"
assert sha(hp) == "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2"
spec = importlib.util.spec_from_file_location("private_order_protocol_db", hp)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
database, table_maps = {}, {}
for phase in ("before", "after"):
    directory = CONTROL / ("db-" + phase)
    saved = read(directory / "manifest.json")
    fingerprint = helper.fingerprint((directory / "snapshot.sqlite").resolve())
    value = {"snapshot_sha256": sha(directory / "snapshot.sqlite"), **{k: fingerprint[k] for k in ("schema_sha256", "logical_content_sha256", "table_count", "row_count")}}
    assert all(value[k] == saved[k] for k in value)
    database[phase] = value
    table_maps[phase] = {x["name"]: x for x in saved["tables"]}
post = read(RUN / "postflight-full.json")
assert post["source_count"] == 416 and post["source_failures"] == []
assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values())
assert "No running processes found" in post["ixsmi"]
assert all(value is None or "\nState:\tZ " in value for value in post["owned_process_status"].values())
assert sha(RUN / "postflight-sources/triton_unified_attention.py") == "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
report = {
    "status": "verified_single_actual_private_page_order_restore_readback_and_consumer",
    "run": RUN.name, "source_count_rehashed": 416, "source_manifest_sha256": sha(CONTROL / "source-sha256.json"),
    "manifest_sha256": sha(RUN / "manifest.json"), "raw_sha256": sha(raw_path), "server_log_sha256": sha(RUN / "server.log"),
    "events": [x["event"] for x in events], "transaction_key": key, "saved_prefix_tokens": prefix_tokens,
    "payload_bytes": payload_bytes, "logical_pages": page_count, "save_runs": runs(save["command"]["pages"]), "save_copy_calls": save["worker_response"]["copy_calls"],
    "private_order_observation": ordered,
    "destination_runs": destination_runs, "zero_calls": zero["worker_response"]["zero_calls"], "restore_copy_calls": verify["copy_calls"],
    "verification_copy_calls": verify["verification_copy_calls"], "verification_readback_bytes": verify["verification_readback_bytes"],
    "verification_passed": True, "verification_layers_from_pinned_worker_source": 42,
    "first_defer": defers[0] if defers else None, "final_restore_skips": consumed["restore_skips"], "runner_six_checks": state["checks"],
    "original_consumer_scheduled_tokens": consumed["scheduled_tokens"], "host_released": True,
    "save_memory_observations": {k: save["worker_response"][k] for k in ("memory_before", "memory_after_pin", "host_payload_bytes", "diagnostic_extra_pinned_bytes")},
    "database": database, "database_unchanged": database["before"] == database["after"],
    "database_new_tables": [{"name": name, "row_count": table_maps["after"][name]["row_count"]} for name in sorted(table_maps["after"].keys() - table_maps["before"].keys())],
    "database_existing_changed_tables": [{"name": name, "before_rows": table_maps["before"][name]["row_count"], "after_rows": table_maps["after"][name]["row_count"]} for name in sorted(table_maps["before"].keys() & table_maps["after"].keys()) if table_maps["before"][name]["content_sha256"] != table_maps["after"][name]["content_sha256"]],
    "cpu_quota": 6, "physical_memory_mib": 32768, "kv_tokens": kv_tokens, "preemptions": metrics,
    "completed": 32, "failed": 0, "tokens": [524288, 32768], "finished_utc": (RUN / "finished-at.txt").read_text().strip(),
    "diagnostic_duration_s": raw["duration"], "diagnostic_total_tps": raw["total_token_throughput"], "diagnostic_ttft_ms": raw["mean_ttft_ms"],
    "postflight_utc": post["utc"], "idle_verified": True,
    "shutdown_error_lines": [line for line in log.splitlines() if "ERROR" in line or "EngineDeadError" in line],
    "limits": ["仅一次实际抢占的排序/42层前缀恢复/整字节回读、CPU状态检查与原输出消费，不是整模型准确率或所有恢复情形证明。", "old/new run与集合守恒标记来自被精确pin的helper；完整old目的页序未另外输出，不能声称从raw独立重建全部旧物理映射。", "ENV1完整回读属于诊断；DB本轮实算，不预设变化或不变，不作性能因果/稳定收益结论。", "CPU状态六检查明确在Attention之前；原output消费不是单独Attention数值对照；未来物理归还/reuse轨迹可能变化。"],
}
Path(__file__).with_name("private-order-protocol-review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ("status", "source_count_rehashed", "verification_passed", "preemptions", "database_unchanged", "postflight_utc")}, ensure_ascii=True, indent=2))
