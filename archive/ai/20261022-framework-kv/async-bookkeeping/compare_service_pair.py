"""只读完整两轮服务原件；不重验seal，不修改测量证据或提前计算收益。"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RUNS = {
    "candidate": "20261022T180643Z-async-bookkeeping-service-candidate-decode4k",
    "baseline": "20261022T181134Z-async-bookkeeping-service-baseline-decode4k",
}
ARCHIVE = ROOT / "archive/ai/20261022-framework-kv/async-bookkeeping"
BENCHMARK = "/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py"
BENCHMARK_SHA = "0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565"
DRIVER_SHA = "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9"
RUNNER = "vllm_fl/worker/model_runner.py"
HELPER = "vllm_fl/patches/biv150_async_bookkeeping.py"
MARKER = "BIV150_ASYNC_BOOKKEEPING_FIRST_ACTUAL_SAMPLE_SELECTED "
DB_KEYS = ("snapshot_sha256", "schema_sha256", "logical_content_sha256", "table_count", "row_count")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_arm(label, run_id):
    run = ROOT / "experiments/framework" / run_id
    control = run.with_name(run.name + "-control")
    manifest = read_json(run / "manifest.json")
    (run / "finished-at.txt").read_text()
    exit_code = int((run / "exit-code").read_text())
    files = list((run / "decode-4k/results").glob("*.json"))
    if len(files) != 1:
        raise FileNotFoundError(f"{run_id}: 需要唯一完整benchmark JSON，当前{len(files)}份")
    benchmark = read_json(files[0])
    db = {}
    for side in ("db-before", "db-after"):
        full = read_json(control / side / "manifest.json")
        if full.get("status") != "complete":
            raise FileNotFoundError(f"{run_id}: {side}未完整")
        db[side] = {key: full[key] for key in DB_KEYS}
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    kv = {int(x.replace(",", "")) for x in re.findall(r"GPU KV cache size: ([\d,]+) tokens", log)}
    if len(kv) != 1:
        raise ValueError(f"{run_id}: KV容量缺失或不唯一")
    post = read_json(run / "postflight-full.json")
    markers = []
    for line in log.splitlines():
        if MARKER in line:
            prefix, payload = line.split(MARKER, 1)
            record = json.loads(payload)
            pid = re.search(r"EngineCore[^\s()]* pid=(\d+)", prefix)
            record["same_engine_log_pid"] = bool(pid and int(pid.group(1)) == record.get("pid"))
            markers.append(record)
    marker_ok = not markers
    if label == "candidate":
        marker_ok = bool(len(markers) == 1 and all(
            x["same_engine_log_pid"] and x.get("actual_sample_tokens_returned") is True
            and x.get("num_requests", 0) >= 16
            and x.get("num_requests") == x.get("scheduled_tokens")
            and x.get("selected_delta", 0) > 0
            and x.get("selected_total", 0) >= x.get("selected_delta", 0)
            for x in markers))
    command = (run / "load-commands.json").read_text(encoding="utf-8").replace(
        "/workspace/experiments/minicpm-s2/framework/" + run_id, "<RUN>")
    data = {"run_id": run_id, "exit_code": exit_code, "benchmark": benchmark,
        "kv_tokens": next(iter(kv)), "db": db, "markers": markers, "marker_ok": marker_ok,
        "benchmark_source_sha256": manifest["sha256"].get(BENCHMARK),
        "driver_sha256": sha(run / "screen-driver.py"),
        "postflight_idle_and_source_ok": bool(post["query"].strip() == "68, 0"
            and all(post["ports_closed"].values()) and not post["source_failures"]
            and "No running processes found" in post["ixsmi"])}
    return {"data": data, "manifest": manifest, "control": control,
        "source": read_json(control / "source-sha256.json"), "normalized_load": json.loads(command)}


def compare():
    arms = {label: load_arm(label, run_id) for label, run_id in RUNS.items()}
    a, b = arms["candidate"], arms["baseline"]
    am, bm = a["manifest"], b["manifest"]
    data = {label: arm["data"] for label, arm in arms.items()}
    reference = read_json(ARCHIVE / "base-source-sha256.json")
    pins = read_json(ARCHIVE / "implementation.json")["sha256"]
    changes = sorted(k for k in a["source"].keys() | b["source"].keys() if a["source"].get(k) != b["source"].get(k))
    endpoints = [x["db"][side] for x in data.values() for side in ("db-before", "db-after")]
    checks = {
        "both_complete_exit0": all(x["exit_code"] == 0 for x in data.values()),
        "both_64_success_0_failure": all(x["benchmark"]["completed"] == 64 and x["benchmark"]["failed"] == 0 for x in data.values()),
        "both_expected_input_output_tokens": all(x["benchmark"]["total_input_tokens"] == 262144 and x["benchmark"]["total_output_tokens"] == 8192 for x in data.values()),
        "same_server_args": am["server_command"] == bm["server_command"],
        "same_seed721201": am["seed"] == bm["seed"] == 721201,
        "same_load": a["normalized_load"] == b["normalized_load"],
        "both_unprofiled_decode_screen": all(x["manifest"]["decode_screen"] is True and not x["manifest"]["native_profile"] and not x["manifest"]["host_profile"] for x in arms.values()),
        "same_packages": am["packages"] == bm["packages"],
        "same_cpu_quota_period": all(am["cpu_before"][k] == bm["cpu_before"][k] for k in ("cpu.cfs_quota_us", "cpu.cfs_period_us")),
        "same_KV": a["data"]["kv_tokens"] == b["data"]["kv_tokens"],
        "same_DB_four_endpoints": all(x == endpoints[0] for x in endpoints),
        "only_runner_and_helper_changed": changes == sorted((RUNNER, HELPER)),
        "baseline_exact_clean6f_map": b["source"] == reference,
        "candidate_helper_pin": a["source"].get(HELPER) == pins["biv150_async_bookkeeping.py"] == sha(a["control"] / "plugin-source" / HELPER),
        "candidate_runner_pin": a["source"].get(RUNNER) == pins["candidate_model_runner.py"] == sha(a["control"] / "plugin-source" / RUNNER),
        "both_original_benchmark_manifest_hash": all(x["benchmark_source_sha256"] == BENCHMARK_SHA for x in data.values()),
        "both_original_driver_hash": all(x["driver_sha256"] == DRIVER_SHA for x in data.values()),
        "candidate_actual_marker_baseline_none": all(x["marker_ok"] for x in data.values()),
        "both_postflight_idle_sources_ok": all(x["postflight_idle_and_source_ok"] for x in data.values()),
    }
    ar, br = data["candidate"]["benchmark"], data["baseline"]["benchmark"]
    comparable = all(checks.values())
    return {"kind": "BI-V150 async bookkeeping候选→干净6f单次短服务对照", "runs": data,
        "checks": checks, "pair_comparable": comparable,
        "status": "single_pair_only" if comparable else "confounded_no_performance_conclusion",
        "declared_source_changes": changes,
        "descriptive_percent": {
            "total_token_throughput_change": 100 * (ar["total_token_throughput"] / br["total_token_throughput"] - 1),
            "duration_saved": 100 * (1 - ar["duration"] / br["duration"]),
            "mean_ttft_change": 100 * (ar["mean_ttft_ms"] / br["mean_ttft_ms"] - 1),
            "mean_tpot_change": 100 * (ar["mean_tpot_ms"] / br["mean_tpot_ms"] - 1)},
        "limits": ["单次候选→基线短pair，不能冒称稳定统计收益、官方完整性能或模型准确率。",
            "samePID实际sample返回且selection增加证明该次命中；不是全程覆盖或GPU完成ACK。",
            "新增生产guard成本未包括在此前Windows CPU片段收益比例内，queue2可能遮盖CPU节省。",
            "参数/软件/CPU配额/DB/KV核对不证明全程并行主机负载相同；有任何失配时比率仅描述。",
            "benchmark身份来自各run启动manifest；整包逐seal核验复用root结论。"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "analysis/async-bookkeeping-service-pair.json")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("不覆盖既有比较结果")
    try:
        result = compare()
    except FileNotFoundError as error:
        print(json.dumps({"status": "pending_raw", "reason": str(error), "output_written": False}, ensure_ascii=False))
        return 2
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": result["checks"], "descriptive_percent": result["descriptive_percent"]}, ensure_ascii=False))
    return 0 if result["pair_comparable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
