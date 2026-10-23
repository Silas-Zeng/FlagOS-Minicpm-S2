"""只读三轮prefix原件；齐全后生成skip候选与干净6f单pair，observe不计收益。"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RUNS = {
    "observe": "20261022T173203Z-prefix-cost-single16k-observe",
    "candidate": "20261022T174402Z-no-cascade-prefix-candidate-single16k",
    "baseline": "20261022T174712Z-no-cascade-prefix-baseline-single16k",
}
BENCHMARK = "/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py"
BENCHMARK_SHA = "0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565"
DB_KEYS = ("snapshot_sha256", "schema_sha256", "logical_content_sha256", "table_count", "row_count")
HELPER = "vllm_fl/patches/biv150_no_cascade_prefix.py"
INIT = "vllm_fl/__init__.py"


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
    files = list((run / "prefix-single16k/results").glob("*.json"))
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
    kv_values = {int(x.replace(",", "")) for x in re.findall(r"GPU KV cache size: ([\d,]+) tokens", log)}
    if len(kv_values) != 1:
        raise ValueError(f"{run_id}: KV容量缺失或不唯一")
    validation_name = "prefix-observation-validation.json" if label == "observe" else "prefix-skip-validation.json"
    validation = read_json(run / validation_name)
    post = read_json(run / "postflight-full.json")
    source = read_json(control / "source-sha256.json")
    command = (run / "load-commands.json").read_text(encoding="utf-8").replace(
        "/workspace/experiments/minicpm-s2/framework/" + run_id, "<RUN>")
    metadata = {
        "run_id": run_id, "exit_code": exit_code, "benchmark": benchmark,
        "kv_tokens": next(iter(kv_values)), "db": db, "source_count": len(source),
        "validation": validation, "benchmark_source_sha256": manifest["sha256"].get(BENCHMARK),
        "driver_sha256": sha(run / "screen-driver.py"),
        "postflight_idle_and_source_ok": bool(post["query"].strip() == "68, 0"
            and all(post["ports_closed"].values()) and not post["source_failures"]
            and "No running processes found" in post["ixsmi"]),
    }
    return {"run": run, "control": control, "manifest": manifest, "source": source,
            "normalized_load": json.loads(command), "data": metadata}


def compare():
    arms = {label: load_arm(label, run_id) for label, run_id in RUNS.items()}
    a, b, o = arms["candidate"], arms["baseline"], arms["observe"]
    data = {label: arm["data"] for label, arm in arms.items()}
    am, bm = a["manifest"], b["manifest"]
    sources = a["source"], b["source"]
    changes = sorted(k for k in sources[0].keys() | sources[1].keys() if sources[0].get(k) != sources[1].get(k))
    reference = read_json(ROOT / "archive/ai/20261022-framework-kv/no-cascade-prefix-skip/base-source-sha256.json")
    package = read_json(ROOT / "archive/ai/20261022-framework-kv/no-cascade-prefix-skip/cpu-preparation.json")
    endpoints = [arm["data"]["db"][side] for arm in (a, b) for side in ("db-before", "db-after")]
    checks = {
        "all_runs_complete_exit0": all(x["exit_code"] == 0 for x in data.values()),
        "all_validation_passed": all(x["validation"]["valid"] is True for x in data.values()),
        "all_requests_1_success_0_failure": all(x["benchmark"]["completed"] == 1 and x["benchmark"]["failed"] == 0 for x in data.values()),
        "all_tokens_16384_input_128_output": all(x["benchmark"]["total_input_tokens"] == 16384 and x["benchmark"]["total_output_tokens"] == 128 for x in data.values()),
        "all_same_server_args": all(x["manifest"]["server_command"] == bm["server_command"] for x in arms.values()),
        "all_same_seed721201": all(x["manifest"]["seed"] == 721201 for x in arms.values()),
        "all_same_load": all(x["normalized_load"] == b["normalized_load"] for x in arms.values()),
        "all_unprofiled_decode_screen": all(x["manifest"]["decode_screen"] is True and not x["manifest"]["native_profile"] and not x["manifest"]["host_profile"] for x in arms.values()),
        "pair_same_packages": am["packages"] == bm["packages"],
        "pair_same_cpu_quota_period": all(am["cpu_before"][k] == bm["cpu_before"][k] for k in ("cpu.cfs_quota_us", "cpu.cfs_period_us")),
        "pair_same_KV": a["data"]["kv_tokens"] == b["data"]["kv_tokens"],
        "pair_same_DB_four_endpoints": all(x == endpoints[0] for x in endpoints),
        "pair_only_init_and_helper_changed": changes == sorted((INIT, HELPER)),
        "baseline_exact_clean6f_map": b["source"] == reference,
        "candidate_helper_pin": a["source"].get(HELPER) == package["assets_sha256"]["biv150_no_cascade_prefix.py"] == sha(a["control"] / "plugin-source" / HELPER),
        "candidate_init_pin": a["source"].get(INIT) == package["candidate_init_sha256"] == sha(a["control"] / "plugin-source" / INIT),
        "all_original_benchmark_manifest_hash": all(x["benchmark_source_sha256"] == BENCHMARK_SHA for x in data.values()),
        "pair_same_frozen_driver": a["data"]["driver_sha256"] == b["data"]["driver_sha256"] == package["assets_sha256"]["run_prefix_skip_short.py"],
        "all_postflight_idle_sources_ok": all(x["postflight_idle_and_source_ok"] for x in data.values()),
    }
    observation = o["data"]["validation"]
    snapshots = observation["snapshots"]
    latest = max(snapshots, key=lambda x: x["counts"]["single_request_calls"] + x["counts"]["multiple_request_calls"])
    result = {"kind": "BI-V150单次skip候选→干净6f服务对照", "runs": data,
              "checks": checks, "pair_comparable": all(checks.values()),
              "status": "single_pair_only" if all(checks.values()) else "confounded_no_performance_conclusion",
              "declared_source_changes": changes,
              "observe_latest_partial": latest,
              "observe_not_performance_baseline": True,
              "gain_computed": False,
              "limits": ["FIRST_SELECTED可来自smoke，只证明真实调用激活，不证明全程逐步覆盖。",
                         "只有一次候选→基线短pair，不是稳定统计、官方完整性能或模型准确率。",
                         "observe的CPU成本不换算吞吐；原benchmark身份来自各run启动manifest。",
                         "配对环境核软件版本、CPU配额、KV与DB；不证明全程并行主机负载完全相同。",
                         "封包与逐seal验收由root负责，本入口不重复运行设备或改原件。"]}
    ar, br = a["data"]["benchmark"], b["data"]["benchmark"]
    result["descriptive_percent_not_causal"] = {
        "total_token_throughput_change": 100 * (ar["total_token_throughput"] / br["total_token_throughput"] - 1),
        "duration_saved": 100 * (1 - ar["duration"] / br["duration"]),
        "mean_ttft_change": 100 * (ar["mean_ttft_ms"] / br["mean_ttft_ms"] - 1),
        "mean_tpot_change": 100 * (ar["mean_tpot_ms"] / br["mean_tpot_ms"] - 1),
    }
    if not checks["pair_same_KV"]:
        result["limits"].append("候选KV521840、基线521936不一致；所有比率仅描述，不能认定性能收益。差异主要体现在TTFT，异步重叠可能遮盖CPU节省但本pair不能证明因果。")
    if result["pair_comparable"]:
        result["gain_computed"] = True
        result["single_pair_percent"] = dict(result["descriptive_percent_not_causal"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "analysis/prefix-skip-service-pair.json")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("不覆盖既有比较结果")
    try:
        result = compare()
    except FileNotFoundError as error:
        print(json.dumps({"status": "pending_raw", "reason": str(error), "output_written": False}, ensure_ascii=False))
        return 2
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": result["checks"], "single_pair_percent": result.get("single_pair_percent")}, ensure_ascii=False))
    return 0 if result["pair_comparable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
