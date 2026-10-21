"""本地 stdlib 复算四份短筛；只读原件，stdout JSON，不是官方计分器。"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SHAPES = (64, 0, 262144, 8192)
HELPER_SHA = "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2"
DRIVER_SHA = "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9"
ATTENTION_SHA = "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


helper_path = ROOT / "scripts/remote/snapshot_tuning_db.py"
assert sha(helper_path) == HELPER_SHA
spec = importlib.util.spec_from_file_location("sqlite_readonly_helper", helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
DB_CACHE = {}


def inspect_run(stamp):
    run = next(p for p in (ROOT / "experiments/framework").glob("20261021T" + stamp + "Z-*")
               if not p.name.endswith("-control"))
    control = Path(str(run) + "-control")
    manifest = read(run / "manifest.json")
    assert read(run / "launch-command.json") == manifest["server_command"]
    assert manifest["decode_screen"] and not any(manifest[key] for key in (
        "native_profile", "host_profile", "context_screen", "context_long_screen", "smoke_only"))
    raw_path, = list(run.glob("decode-4k/results/*.json"))
    raw = read(raw_path)
    assert (run / "exit-code").read_text().strip() == "0"
    assert tuple(raw[k] for k in ("completed", "failed", "total_input_tokens", "total_output_tokens")) == SHAPES
    assert abs(raw["total_token_throughput"] - sum(SHAPES[2:]) / raw["duration"]) < 1e-8
    assert sha(run / "screen-driver.py") == DRIVER_SHA
    assert manifest["sha256"]["/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py"] == "0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565"
    sources = read(control / "source-sha256.json")
    assert all(sha(control / "plugin-source" / name) == value for name, value in sources.items())
    assert all(manifest["sha256"][manifest["source_dir"] + "/" + name] == value
               for name, value in sources.items() if manifest["source_dir"] + "/" + name in manifest["sha256"])
    post = read(run / "postflight-full.json")
    assert not post["source_failures"] and post["source_count"] == len(sources)
    assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values())
    assert "No running processes found" in post["ixsmi"]
    assert all(v is None or "\nState:\tZ " in v for v in post["owned_process_status"].values())
    assert sha(run / "postflight-sources/triton_unified_attention.py") == ATTENTION_SHA
    gpu = list(csv.DictReader((run / "gpu.csv").open(encoding="utf-8")))
    assert gpu and all(row["memory.total"].strip() == "32768 MiB" and "BI-V150" in row["gpu_name"] for row in gpu)
    for phase in ("before", "after"):
        cpu = read(run / ("cpu-" + phase + "-decode-4k.json"))
        assert int(cpu["cpu.cfs_quota_us"]) / int(cpu["cpu.cfs_period_us"]) == 6
    databases = {}
    for phase in ("before", "after"):
        directory = control / ("db-" + phase)
        db_manifest = read(directory / "manifest.json")
        physical = sha(directory / "snapshot.sqlite")
        assert physical == db_manifest["snapshot_sha256"]
        if physical not in DB_CACHE:
            DB_CACHE[physical] = helper.fingerprint((directory / "snapshot.sqlite").resolve())
        fingerprint = DB_CACHE[physical]
        keys = ("schema_sha256", "logical_content_sha256", "table_count", "row_count")
        assert all(fingerprint[k] == db_manifest[k] for k in keys)
        databases[phase] = {"snapshot_sha256": physical, **{k: fingerprint[k] for k in keys}}
    assert databases["before"] == databases["after"]
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    kv, = re.findall(r"GPU KV cache size: ([\d,]+) tokens", log)
    markers = read(run / "selected-marker-review.json")["markers"]
    assert all(line in log for lines in markers.values() for line in lines)
    expected = "BIV150_ASYNC_TOKEN_UPDATE_FIRST_SELECTED" if stamp == "174741" else "BIV150_CPU_METADATA_FIRST_SELECTED" if stamp == "175049" else None
    assert expected is None or markers[expected]
    metrics = {}
    for phase in ("before", "after"):
        values = re.findall(r'^vllm:num_preemptions_total\{[^\n]*\} ([\d.e+\-]+)$',
                            (run / ("metrics-" + phase + "-decode-4k.prom")).read_text(), re.M)
        metrics[phase] = sum(map(float, values))
    load_command, = read(run / "load-commands.json")
    load_command[2] = "<run/decode-4k>"
    result = {"run_id": run.name, "started_utc": manifest["started_utc"],
              "finished_utc": (run / "finished-at.txt").read_text().strip(),
              "raw_path": str(raw_path.relative_to(ROOT)).replace("\\", "/"), "raw_sha256": sha(raw_path),
              "manifest_sha256": sha(run / "manifest.json"), "source_count_verified": len(sources),
              "source_worker_sha256": sources["vllm_fl/worker/model_runner.py"],
              "duration_s": raw["duration"], "total_tokens_per_s": raw["total_token_throughput"],
              "mean_ttft_ms": raw["mean_ttft_ms"], "shape_completed_failed_input_output": SHAPES,
              "kv_tokens": int(kv.replace(",", "")), "database": databases,
              "preemptions": metrics, "cpu_quota_cores": 6, "physical_memory_mib": 32768,
              "selected_markers": markers, "postflight_utc": post["utc"],
              "postflight_idle_verified": True,
              "log_error_or_shutdown_kill_lines": [s for s in log.splitlines() if "ERROR" in s or "kill remaining" in s]}
    return result, manifest, load_command, sources


items = [inspect_run(stamp) for stamp in ("174402", "174741", "175049", "175441")]
assert all(m["server_command"] == items[0][1]["server_command"] and m["packages"] == items[0][1]["packages"]
           and m["seed"] == 721201 and cmd == items[0][2] for _, m, cmd, _ in items)
assert all(item[0]["database"] == items[0][0]["database"] for item in items)
installed = {name: value for name, value in items[0][1]["sha256"].items()
             if not name.startswith(items[0][1]["source_dir"] + "/")}
assert all({name: value for name, value in m["sha256"].items()
            if not name.startswith(m["source_dir"] + "/")} == installed for _, m, _, _ in items)
pairs = []
for label, base_index, candidate_index in (("async_token", 0, 1), ("cpu_metadata", 3, 2)):
    base, candidate = items[base_index][0], items[candidate_index][0]
    assert base["kv_tokens"] == candidate["kv_tokens"]
    before, after = items[base_index][3], items[candidate_index][3]
    differences = {name: {"baseline": before.get(name), "candidate": after.get(name)}
                   for name in sorted(before.keys() | after.keys()) if before.get(name) != after.get(name)}
    pairs.append({"candidate": label, "baseline_run": base["run_id"], "candidate_run": candidate["run_id"],
                  "kv_tokens_matched": base["kv_tokens"], "source_differences": differences,
                  "total_tps_ratio": candidate["total_tokens_per_s"] / base["total_tokens_per_s"],
                  "total_tps_change_percent": (base["duration_s"] / candidate["duration_s"] - 1) * 100,
                  "duration_saved_percent": (1 - candidate["duration_s"] / base["duration_s"]) * 100,
                  "mean_ttft_change_percent": (candidate["mean_ttft_ms"] / base["mean_ttft_ms"] - 1) * 100,
                  "status": "单次同KV/同DB短筛正信号，保留待确认；非稳定因果或最终集成"})
print(json.dumps({"kind": "BI-V150 SQL+C3上的独立小收益短筛；非官方计分", "runs": [v[0] for v in items],
                  "pairs": pairs, "shared_server_command": items[0][1]["server_command"],
                  "shared_load_command_normalized": items[0][2], "shared_packages": items[0][1]["packages"],
                  "shared_installed_source_sha256": installed,
                  "screen_driver_sha256": DRIVER_SHA, "sqlite_helper_sha256": HELPER_SHA,
                  "limitations": ["每个候选仅一轮短服务，无新准确率/正式吞吐；FIRST_SELECTED不证明全步计数。",
                                  "async对A1同KV521840，metadata对随后A2同KV521936；不能跨容量比较漂移。",
                                  "运行顺序A1→async→metadata→A2，未随机交替；相同DB不保证Triton/CPU缓存或主机负载完全相同。",
                                  "保留小正差，未达到稳定性归因证据，不设最低收益淘汰线。"]}, ensure_ascii=False, indent=2))
