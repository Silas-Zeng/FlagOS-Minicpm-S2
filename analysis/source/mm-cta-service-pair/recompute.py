"""stdlib只读复算CTA/干净基线短筛，保留KV容量差及退出错误时序。"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / "scripts/remote/snapshot_tuning_db.py"
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text(encoding="utf-8"))
assert sha(HELPER) == "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2"
spec = importlib.util.spec_from_file_location("readonly_db", HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def inspect_run(name, worker, count):
    run = ROOT / "experiments/framework" / name
    control = Path(str(run) + "-control")
    manifest, sources = read(run / "manifest.json"), read(control / "source-sha256.json")
    assert (run / "exit-code").read_text().strip() == "0"
    assert len(sources) == count and all(sha(control / "plugin-source" / k) == v for k, v in sources.items())
    assert sources["vllm_fl/worker/model_runner.py"] == worker
    assert sha(run / "screen-driver.py") == "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9"
    assert manifest["sha256"]["/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py"] == "0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565"
    assert manifest["context_screen"] and not any(manifest[k] for k in (
        "context_long_screen", "decode_screen", "host_profile", "native_profile", "smoke_only"))
    assert read(run / "launch-command.json") == manifest["server_command"]
    load, = read(run / "load-commands.json")
    assert load[3:] == ["context-16k", "16384", "128", "64", "32", "721201"]
    raw_path, = run.glob("context-16k/results/*.json")
    raw = read(raw_path)
    assert tuple(raw[k] for k in ("completed", "failed", "total_input_tokens", "total_output_tokens")) == (32, 0, 524288, 4096)
    assert abs(raw["total_token_throughput"] - 528384 / raw["duration"]) < 1e-8
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    kv, = re.findall(r"GPU KV cache size: ([\d,]+) tokens", log)
    before_shutdown, _, shutdown = log.partition("[shutdown] API server: shutdown triggered")
    post = read(run / "postflight-full.json")
    assert post["source_count"] == count and not post["source_failures"]
    assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values())
    assert "No running processes found" in post["ixsmi"]
    assert all(x is None or "\nState:\tZ " in x for x in post["owned_process_status"].values())
    assert sha(run / "postflight-sources/triton_unified_attention.py") == "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
    gpu = list(csv.DictReader((run / "gpu.csv").open(encoding="utf-8")))
    assert gpu and all(x["memory.total"].strip() == "32768 MiB" and "BI-V150" in x["gpu_name"] for x in gpu)
    databases, metrics = {}, {}
    for phase in ("before", "after"):
        d = control / ("db-" + phase)
        dm, fp = read(d / "manifest.json"), helper.fingerprint((d / "snapshot.sqlite").resolve())
        assert sha(d / "snapshot.sqlite") == dm["snapshot_sha256"]
        keys = ("schema_sha256", "logical_content_sha256", "table_count", "row_count")
        assert all(fp[k] == dm[k] for k in keys)
        databases[phase] = {"snapshot_sha256": dm["snapshot_sha256"], **{k: fp[k] for k in keys}}
        cpu = read(run / ("cpu-" + phase + "-context-16k.json"))
        assert int(cpu["cpu.cfs_quota_us"]) / int(cpu["cpu.cfs_period_us"]) == 6
        text = (run / ("metrics-" + phase + "-context-16k.prom")).read_text()
        metrics[phase] = sum(map(float, re.findall(r'^vllm:num_preemptions_total\{[^\n]*\} ([\d.e+\-]+)$', text, re.M)))
    assert databases["before"] == databases["after"]
    installed = {k: v for k, v in manifest["sha256"].items() if not k.startswith(manifest["source_dir"] + "/")}
    evidence = {"run_id": name, "started_utc": manifest["started_utc"],
        "finished_utc": (run / "finished-at.txt").read_text().strip(), "raw_sha256": sha(raw_path),
        "source_count_verified": count, "worker_sha256": worker, "completed": 32, "failed": 0,
        "input_tokens": 524288, "output_tokens": 4096, "duration_s": raw["duration"],
        "total_tokens_per_s": raw["total_token_throughput"], "mean_ttft_ms": raw["mean_ttft_ms"],
        "kv_tokens": int(kv.replace(",", "")), "database": databases, "preemptions": metrics,
        "cpu_quota_cores": 6, "physical_memory_mib": 32768, "postflight_idle_verified": True,
        "postflight_utc": post["utc"], "errors_before_shutdown": [x for x in before_shutdown.splitlines() if "ERROR" in x],
        "errors_during_shutdown": [x for x in shutdown.splitlines() if "ERROR" in x],
        "shutdown_forcekill_lines": [x for x in shutdown.splitlines() if "force killing remaining" in x]}
    assert not evidence["errors_before_shutdown"]
    return evidence, manifest, sources, installed


candidate = inspect_run("20261021T182916Z-mm-cta-group-context16k",
    "787665d3cf6dabc1afc2bdf7069fab4802fd5f6bfb0baedd119229b5b8ce1775", 413)
baseline = inspect_run("20261021T183543Z-baseline-context16k",
    "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1", 410)
repeat = inspect_run("20261021T184244Z-baseline-context16k",
    "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1", 410)
c, b = candidate[0], baseline[0]
assert candidate[1]["server_command"] == baseline[1]["server_command"]
assert candidate[1]["packages"] == baseline[1]["packages"] and candidate[3] == baseline[3]
assert candidate[1]["seed"] == baseline[1]["seed"] == 721201 and c["database"] == b["database"]
assert repeat[1]["server_command"] == baseline[1]["server_command"] and repeat[1]["packages"] == baseline[1]["packages"]
assert repeat[3] == baseline[3] and repeat[2] == baseline[2] and repeat[0]["database"] == b["database"]
assert repeat[0]["kv_tokens"] == b["kv_tokens"]
artifact, = (ROOT / "experiments/framework" / (c["run_id"] + "-control") / "cta-artifacts").iterdir()
installed, status = read(artifact / "install.json"), read(artifact / "status.json")
assert all(sha(artifact / name) == value for name, value in installed["source_sha256"].items())
assert status["first_real_selected"]["selected_delta"] == 42
differences = {name: {"baseline": baseline[2].get(name), "candidate": candidate[2].get(name)}
    for name in sorted(baseline[2].keys() | candidate[2].keys()) if baseline[2].get(name) != candidate[2].get(name)}
print(json.dumps({"kind": "BI-V150 CTA gate-up-only单次同参数/同DB短筛；KV不同，非严格匹配或官方计分",
    "baseline": b, "baseline_repeat": repeat[0], "candidate": c, "source_differences": differences,
    "two_baseline_same_kv_duration_range_s": [min(b["duration_s"], repeat[0]["duration_s"]), max(b["duration_s"], repeat[0]["duration_s"])],
    "two_baseline_observed_duration_span_percent": (max(b["duration_s"], repeat[0]["duration_s"]) / min(b["duration_s"], repeat[0]["duration_s"]) - 1) * 100,
    "matched_dimensions": {"server_command": True, "load_shape_seed": True, "packages_installed_source": True,
        "database_before_after": True, "cpu_quota_physical_memory": True, "kv_capacity": c["kv_tokens"] == b["kv_tokens"]},
    "descriptive_total_tps_ratio": c["total_tokens_per_s"] / b["total_tokens_per_s"],
    "descriptive_total_tps_change_percent": (b["duration_s"] / c["duration_s"] - 1) * 100,
    "descriptive_duration_saved_percent": (1 - c["duration_s"] / b["duration_s"]) * 100,
    "descriptive_mean_ttft_change_percent": (c["mean_ttft_ms"] / b["mean_ttft_ms"] - 1) * 100,
    "first_real_selected": status["first_real_selected"], "first_real_marker_is_full_count": False,
    "limitations": ["baseline KV521936、candidate521840，差96tokens，不能严格容量归因。",
        "运行顺序候选→mapped编译失败门→干净基线→第二干净基线，未随机交替；同DB不排除Triton/主机缓存和CPU负载。",
        "第二基线同KV521936，仅记录同容量观察范围；不无限刷新、不加假buffer凑候选521840。",
        "status只首次real flush，证明至少该真实execute中42次，不是全负载调用数或覆盖率。",
        "候选原raw32/0完成后SIGTERM/abort shutdown出现EngineDeadError及force-kill警告，原日志不删。",
        "保留单次正信号待确认，无新模型accuracy/正式吞吐或默认集成，不对coverage诊断计算gain。"]}, ensure_ascii=False, indent=2))
