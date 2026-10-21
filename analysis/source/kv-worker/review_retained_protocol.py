"""只读202526真实恢复原件；原始日志/DB/source不改，不导入框架。"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/framework/20261021T202526Z-kv-retain-context16k-long"
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
    "vllm_fl/patches/biv150_kv_protocol.py": "a1b691f52f3724b95bbcb11f5702611a17103161001bb929096c71ab4fa74751",
    "vllm_fl/patches/biv150_kv_transaction.py": "616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13",
    "vllm_fl/patches/biv150_kv_page_copy.py": "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c",
    "vllm_fl/worker/model_runner.py": "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1",
    "vllm_fl/__init__.py": "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8",
}
assert all(sources[name] == value for name, value in expected.items())
assert sha(CONTROL / "prepare_kv_protocol_source.py") == "ac18b84dfc2e9435c6984f05ddc084d24458d2b158003df29ec9fedc641b6429"
assert sha(CONTROL / "launch.sh") == "c4526fa0178989b47647acba2407025cfd04d54034c97c569451d8b77bc5a973"
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
assert [x["event"] for x in events] == ["FIRST_CHECKED", "RPC_ACK", "SAVE_ACK_FREE", "RESTORE_DEFERRED", "RPC_ACK", "RPC_ACK", "RESTORE_ACK", "RESUME_PUBLISHED", "RPC_ACK", "RUNNER_RESUME_STATE_CHECKED", "RESUME_OUTPUT_PROCESSED"]
assert events[0]["eligible"] is True
acks = [x for x in events if x["event"] == "RPC_ACK"]
assert [x["command"]["kind"] for x in acks] == ["SAVE", "ZERO", "RESTORE", "DROP"]
key = acks[0]["command"]["key"]
for serial, row in enumerate(acks, 1):
    cmd, response = row["command"], row["worker_response"]
    assert cmd["key"] == key and cmd["operation_serial"] == serial
    assert response["completed"] is True and response["successful"] is True and response["error"] is None
    assert row["pid"] == response["worker_pid"] == 217577
    assert all(cmd[k] == response[k] for k in ("key", "operation_serial", "kind", "pages", "nbytes", "prefix_tokens"))
    assert response["transferred_bytes"] == cmd["nbytes"]
    if cmd["kind"] != "DROP":
        assert len(cmd["pages"]) == len(set(cmd["pages"])) == 1044 and min(cmd["pages"]) > 0
        assert cmd["prefix_tokens"] == 16704 and cmd["nbytes"] == 16704 * 43008 == 718405632
        assert response["submitted_bytes"] == cmd["nbytes"]
save, zero, restore, drop = acks
assert runs(save["command"]["pages"]) == 24 and save["worker_response"]["copy_calls"] == 1008
assert zero["command"]["pages"] == restore["command"]["pages"]
assert runs(zero["command"]["pages"]) == 1044
assert zero["worker_response"]["zero_calls"] == 1044 * 42 == 43848
verify = restore["worker_response"]
assert verify["copy_calls"] == verify["verification_copy_calls"] == 43848
assert verify["verification_performed"] is True and verify["verification_passed"] is True
assert verify["verification_readback_bytes"] == 718405632
assert verify["diagnostic_verify_requested"] is True and verify["diagnostic_extra_pinned_bytes"] == 17104896
assert drop["command"]["nbytes"] == 0 and drop["command"]["pages"] == []
assert drop["worker_response"]["host_held"] is False and drop["worker_response"]["host_payload_bytes"] == 0
defer = events[3]
assert defer["reason"] == "allocation_none" and defer["host_retained"] is True
assert [defer[k] for k in ("free_blocks", "saved_prefix_pages", "request_tokens", "token_budget", "pending_frames", "output_placeholders")] == [1030, 1044, 16712, 2018, 0, 0]
assert defer["full_sequence_must_fit"] is True and defer["allocator_required_blocks_observed"] is False
state, consumed = events[-2:]
assert len(state["checks"]) == 6 and all(state["checks"].values())
assert state["key"] == consumed["key"] == key
assert state["before_attention"] is True and state["gpu_completion_claimed"] is False
assert consumed["after_original_update"] is True and consumed["scheduled_tokens"] == 8
assert all(consumed[k] == value for k, value in {"saved": 1, "restored": 1, "published": 1, "rollbacks": 0, "restore_skips": 454}.items())
assert "GPU KV cache size: 521,936 tokens" in log
metrics = {}
for phase in ("before", "after"):
    text = (RUN / ("metrics-" + phase + "-context-16k-long.prom")).read_text()
    metrics[phase] = sum(map(float, re.findall(r'^vllm:num_preemptions_total\{[^\n]*\} ([\d.e+\-]+)$', text, re.M)))
hp = CONTROL / "snapshot_tuning_db.py"
assert sha(hp) == "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2"
spec = importlib.util.spec_from_file_location("retained_protocol_db", hp)
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
assert [database[p]["table_count"] for p in ("before", "after")] == [516, 518]
assert [database[p]["row_count"] for p in ("before", "after")] == [19270, 19337]
assert database["before"] != database["after"]
post = read(RUN / "postflight-full.json")
assert post["source_count"] == 416 and post["source_failures"] == []
assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values())
assert "No running processes found" in post["ixsmi"]
assert all(value is None or "\nState:\tZ " in value for value in post["owned_process_status"].values())
assert sha(RUN / "postflight-sources/triton_unified_attention.py") == "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
report = {
    "status": "verified_single_actual_restore_byte_readback_and_original_consumer",
    "run": RUN.name, "source_count_rehashed": 416, "source_manifest_sha256": sha(CONTROL / "source-sha256.json"),
    "manifest_sha256": sha(RUN / "manifest.json"), "raw_sha256": sha(raw_path), "server_log_sha256": sha(RUN / "server.log"),
    "events": [x["event"] for x in events], "transaction_key": key, "saved_prefix_tokens": 16704,
    "payload_bytes": 718405632, "logical_pages": 1044, "save_runs": 24, "save_copy_calls": 1008,
    "destination_runs": 1044, "zero_calls": 43848, "restore_copy_calls": 43848,
    "verification_copy_calls": 43848, "verification_readback_bytes": 718405632,
    "verification_passed": True, "verification_layers_from_pinned_worker_source": 42,
    "first_defer": defer, "final_restore_skips": 454, "runner_six_checks": state["checks"],
    "original_consumer_scheduled_tokens": 8, "host_released": True,
    "save_memory_observations": {k: save["worker_response"][k] for k in ("memory_before", "memory_after_pin", "host_payload_bytes", "diagnostic_extra_pinned_bytes")},
    "database": database, "database_unchanged": False,
    "database_new_tables": [{"name": name, "row_count": table_maps["after"][name]["row_count"]} for name in sorted(table_maps["after"].keys() - table_maps["before"].keys())],
    "database_existing_changed_tables": [{"name": name, "before_rows": table_maps["before"][name]["row_count"], "after_rows": table_maps["after"][name]["row_count"]} for name in sorted(table_maps["before"].keys() & table_maps["after"].keys()) if table_maps["before"][name]["content_sha256"] != table_maps["after"][name]["content_sha256"]],
    "cpu_quota": 6, "physical_memory_mib": 32768, "kv_tokens": 521936, "preemptions": metrics,
    "completed": 32, "failed": 0, "tokens": [524288, 32768], "finished_utc": (RUN / "finished-at.txt").read_text().strip(),
    "diagnostic_duration_s": raw["duration"], "diagnostic_total_tps": raw["total_token_throughput"], "diagnostic_ttft_ms": raw["mean_ttft_ms"],
    "postflight_utc": post["utc"], "idle_verified": True,
    "shutdown_error_lines": [line for line in log.splitlines() if "ERROR" in line or "EngineDeadError" in line],
    "limits": ["仅一次实际抢占的42层前缀恢复/整字节回读、CPU状态检查与原输出消费，不是整模型准确率或所有恢复情形证明。", "首个allocation_none日志有free1030<1044prefix页且full-fit真；未记录allocator所需值，不把454次跳过逐次归因。", "DB新增表/形状调优和ENV1完整回读均在本诊断中；240.93秒不作性能因果或稳定收益结论。", "CPU状态六检查明确在Attention之前；后续原output消费不是单独Attention数值对照。"],
}
Path(__file__).with_name("retained-protocol-review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ("status", "source_count_rehashed", "verification_passed", "preemptions", "database_unchanged", "postflight_utc")}, ensure_ascii=True, indent=2))
