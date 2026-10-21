"""纯只读VERIFY0成对短测原件；不套用diagnostic verification=True门。"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
REMOTE = "/workspace/experiments/minicpm-s2/"
RUNS = {"stable": "20261021T205219Z-kv-pair-stable-context16k-long",
        "page-order": "20261021T205819Z-kv-pair-page-order-context16k-long"}
WRAPPER = "11917a047c3c3f5fadebca3898b5720224e075e3ca93bb610c258a4ef70776ad"
DRIVER = "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9"
DB_KEYS = ("snapshot_sha256", "schema_sha256", "logical_content_sha256")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def runs(pages):
    return sum(i == 0 or p != pages[i - 1] + 1 for i, p in enumerate(pages))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=RUNS)
    variant = parser.parse_args().variant
    run = ROOT / "experiments/framework" / RUNS[variant]
    control = run.with_name(run.name + "-control")
    reference = ROOT / "experiments/framework/20261021T204159Z-kv-page-order-context16k-long-control"
    assert sha(reference / "source-sha256.json") == "98a72844e77eee9e07d6c70050003bd121bb61404c507189dd663a320651f240"
    assert sha(reference / "plugin-source/innovation-source.json") == "3b1343aba960abe70b59bc2979a4b7a16a5defac5d8506161852614f862cc5a7"
    package = read(reference / "plugin-source/innovation-source.json")
    expected = package["input_sha256"] if variant == "stable" else read(reference / "source-sha256.json")
    sources = read(control / "source-sha256.json")
    assert sources == expected and len(sources) == (410 if variant == "stable" else 416)
    assert all(sha(control / "plugin-source" / name) == value for name, value in sources.items())
    actual_files = {p.relative_to(control / "plugin-source").as_posix() for p in (control / "plugin-source").rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")}
    assert actual_files == sources.keys()
    assert sha(control / "launch_kv_pair_screen.py") == WRAPPER
    assert sha(control / "run_framework_screen.py") == sha(run / "screen-driver.py") == DRIVER
    assert (run / "exit-code").read_text().strip() == "0"
    manifest, purpose, command = read(run / "manifest.json"), read(control / "purpose.json"), read(control / "command.json")
    assert purpose["variant"] == variant and purpose["wrapper_sha256"] == WRAPPER
    assert purpose["source_count"] == len(sources) and purpose["restore_byte_readback_enabled"] is False
    assert command["env"] == {"BIV150_KV_VERIFY_RESTORE": "0"} and command["argv"] == purpose["command"]
    assert command["argv"][2:] == [REMOTE + "framework/" + run.name, "--source-dir", manifest["source_dir"], "--context-long-screen", "--seed", "721201", "--require-log-marker", "BIV150_SQL_REFLECTION_INSTALLED" if variant == "stable" else "BIV150_KV_PROTOCOL_INSTALLED"]
    assert manifest["context_long_screen"] and manifest["seed"] == 721201
    assert not any(manifest[k] for k in ("native_profile", "host_profile", "decode_screen", "context_screen", "smoke_only"))
    assert manifest["server_command"] == read(run / "launch-command.json") == ["vllm", "serve", "/workspace/MiniCPM5-2B", "--port", "9031", "--compilation-config", '{"cudagraph_mode": "FULL_DECODE_ONLY"}', "--served-model-name", "minicpm", "--gpu-memory-utilization", "0.85", "--max-model-len", "131072"]
    load, = read(run / "load-commands.json")
    assert load[3:] == ["context-16k-long", "16384", "1024", "64", "32", "721201"]
    raw_path, = (run / "context-16k-long/results").glob("*.json")
    raw = read(raw_path)
    assert [raw[k] for k in ("completed", "failed", "total_input_tokens", "total_output_tokens")] == [32, 0, 524288, 32768]
    for phase in ("before", "after"):
        cpu = read(run / ("cpu-" + phase + "-context-16k-long.json"))
        assert int(cpu["cpu.cfs_quota_us"]) / int(cpu["cpu.cfs_period_us"]) == 6
    with (run / "gpu.csv").open(encoding="utf-8") as stream:
        gpu = list(csv.DictReader(stream))
    assert gpu and all(row["memory.total"].strip() == "32768 MiB" for row in gpu)
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    kv_match, = re.findall(r"GPU KV cache size: ([\d,]+) tokens", log)
    kv_tokens = int(kv_match.replace(",", ""))
    metrics = {phase: sum(map(float, re.findall(r'^vllm:num_preemptions_total\{[^\n]*\} ([\d.e+\-]+)$', (run / ("metrics-" + phase + "-context-16k-long.prom")).read_text(), re.M))) for phase in ("before", "after")}
    hp = control / "snapshot_tuning_db.py"
    assert sha(hp) == "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2"
    spec = importlib.util.spec_from_file_location("kv_pair_review_db", hp)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)

    def database(directory):
        saved = read(directory / "manifest.json")
        actual = {"snapshot_sha256": sha(directory / "snapshot.sqlite"), **helper.fingerprint((directory / "snapshot.sqlite").resolve())}
        assert saved["status"] == "complete" and all(saved[k] == actual[k] for k in (*DB_KEYS, "table_count", "row_count"))
        return {k: actual[k] for k in (*DB_KEYS, "table_count", "row_count")}

    db = {phase: database(control / ("db-" + phase)) for phase in ("before", "after")}
    assert purpose["db_before"] == db["before"]
    events = [json.loads(line.split("BIV150_KV_PROTOCOL ", 1)[1]) for line in log.splitlines() if "BIV150_KV_PROTOCOL {" in line]
    protocol = None
    matched = None
    if variant == "stable":
        assert not events and "BIV150_KV_PROTOCOL_INSTALLED" not in log
        assert purpose["matching_baseline_after"] is None
    else:
        acks = [x for x in events if x["event"] == "RPC_ACK"]
        assert [x["command"]["kind"] for x in acks] == ["SAVE", "ZERO", "RESTORE", "DROP"]
        key = acks[0]["command"]["key"]
        for serial, row in enumerate(acks, 1):
            cmd, ack = row["command"], row["worker_response"]
            assert cmd["key"] == key and cmd["operation_serial"] == serial
            assert all(cmd[k] == ack[k] for k in ("key", "operation_serial", "kind", "pages", "nbytes", "prefix_tokens"))
            assert ack["successful"] is True and ack["completed"] is True and ack["transferred_bytes"] == cmd["nbytes"]
            if cmd["kind"] != "DROP":
                assert ack["diagnostic_verify_requested"] is False and ack["diagnostic_extra_pinned_bytes"] == 0
                assert ack.get("verification_performed", False) is False and ack.get("verification_readback_bytes", 0) == 0
        save, zero, restore, drop = acks
        destination = zero["command"]["pages"]
        assert destination == restore["command"]["pages"] == sorted(destination) and len(set(destination)) == len(destination)
        new_runs = runs(destination)
        ordered, = [x for x in events if x["event"] == "PRIVATE_PAGES_ORDERED"]
        assert ordered["increasing_runs_after"] == new_runs < ordered["increasing_runs_before"]
        assert zero["worker_response"]["zero_calls"] == restore["worker_response"]["copy_calls"] == new_runs * 42
        assert drop["worker_response"]["host_held"] is False
        state, = [x for x in events if x["event"] == "RUNNER_RESUME_STATE_CHECKED"]
        consumed, = [x for x in events if x["event"] == "RESUME_OUTPUT_PROCESSED"]
        assert len(state["checks"]) == 6 and all(state["checks"].values())
        assert state["key"] == consumed["key"] == key and consumed["after_original_update"] is True
        protocol = {"key": key, "prefix_tokens": save["command"]["prefix_tokens"], "payload_bytes": save["command"]["nbytes"], "save_calls": save["worker_response"]["copy_calls"], "ordered": ordered, "zero_calls": zero["worker_response"]["zero_calls"], "restore_calls": restore["worker_response"]["copy_calls"], "restore_skips": consumed["restore_skips"], "consumer_scheduled_tokens": consumed["scheduled_tokens"], "runner_checks": state["checks"], "verification_performed": False}
        baseline = ROOT / "experiments/framework" / (RUNS["stable"] + "-control")
        baseline_db = {phase: database(baseline / ("db-" + phase)) for phase in ("before", "after")}
        assert all(baseline_db["before"][k] == baseline_db["after"][k] == db["before"][k] for k in DB_KEYS)
        match = purpose["matching_baseline_after"]
        assert match["baseline_before_after_three_hashes_equal"] and match["three_hashes_equal"]
        assert match["before"] == baseline_db["before"] and match["after"] == baseline_db["after"]
        baseline_run = baseline.with_name(baseline.name[:-8])
        baseline_manifest = read(baseline_run / "manifest.json")
        assert baseline_manifest["server_command"] == manifest["server_command"] and baseline_manifest["seed"] == manifest["seed"]
        assert re.findall(r"GPU KV cache size: ([\d,]+) tokens", (baseline_run / "server.log").read_text(encoding="utf-8")) == [kv_match]
        matched = {"baseline_run": RUNS["stable"], "baseline_db_before_after_and_candidate_before_equal": True, "kv_tokens_equal": True, "server_seed_equal": True}
    post = read(run / "postflight-full.json")
    assert post["source_count"] == len(sources) and post["source_failures"] == []
    assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values()) and "No running processes found" in post["ixsmi"]
    assert all(value is None or "\nState:\tZ " in value for value in post["owned_process_status"].values())
    assert sha(run / "postflight-sources/triton_unified_attention.py") == "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
    result = {"status": "verified_verify0_" + variant + "_screen", "run": run.name, "variant": variant,
              "source_count_rehashed": len(sources), "source_sha256": sha(control / "source-sha256.json"), "raw_sha256": sha(raw_path), "server_log_sha256": sha(run / "server.log"), "wrapper_sha256": WRAPPER,
              "verification_performed": False, "completed": 32, "failed": 0, "tokens": [524288, 32768], "cpu_quota": 6, "physical_memory_mib": 32768, "kv_tokens": kv_tokens, "preemptions": metrics,
              "database": db, "database_unchanged": db["before"] == db["after"], "protocol": protocol, "paired_conditions": matched,
              "duration_s": raw["duration"], "total_tps": raw["total_token_throughput"], "mean_ttft_ms": raw["mean_ttft_ms"], "finished_utc": (run / "finished-at.txt").read_text().strip(), "postflight_utc": post["utc"], "idle_verified": True,
              "shutdown_error_lines": [line for line in log.splitlines() if "ERROR" in line or "EngineDeadError" in line],
              "limits": ["VERIFY0性能短测不做本轮字节回读，既有204159 VERIFY1证据单列，不能硬要求True或伪造核验。", "单次pair只能记录描述差异，不证明稳定收益、编译cache全热或新accuracy；非官方成绩。"]}
    Path(__file__).with_name("pair-" + variant + "-review.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "source_count_rehashed", "duration_s", "database_unchanged", "kv_tokens", "postflight_utc")}, ensure_ascii=True))


if __name__ == "__main__":
    main()
