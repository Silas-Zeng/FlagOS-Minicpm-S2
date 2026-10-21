"""只读复核mapped首次服务及同参数/DB基线；保留KV差异和负结果。"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
NAMES = ("20261021T184244Z-baseline-context16k", "20261021T185627Z-mapped-decode-context16k")
DRIVER = "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9"
HELPER = "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


hp = ROOT / "scripts/remote/snapshot_tuning_db.py"
assert sha(hp) == HELPER
spec = importlib.util.spec_from_file_location("mapped_review_sqlite", hp)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
db_cache, runs, source_maps, manifests, loads = {}, [], [], [], []
for name in NAMES:
    run = ROOT / "experiments/framework" / name
    control = run.with_name(name + "-control")
    manifest = read(run / "manifest.json")
    sources = read(control / "source-sha256.json")
    assert all(sha(control / "plugin-source" / relative) == expected for relative, expected in sources.items())
    assert all(manifest["sha256"][manifest["source_dir"] + "/" + relative] == expected
               for relative, expected in sources.items() if manifest["source_dir"] + "/" + relative in manifest["sha256"])
    assert sha(run / "screen-driver.py") == DRIVER
    assert read(run / "launch-command.json") == manifest["server_command"]
    assert manifest["context_screen"] and not any(manifest[x] for x in ("decode_screen", "context_long_screen", "host_profile", "native_profile", "smoke_only"))
    raw_path, = list((run / "context-16k/results").glob("*.json"))
    raw = read(raw_path)
    assert (run / "exit-code").read_text().strip() == "0"
    assert [raw[k] for k in ("completed", "failed", "total_input_tokens", "total_output_tokens")] == [32, 0, 524288, 4096]
    post = read(run / "postflight-full.json")
    assert post["source_count"] == len(sources) and post["source_failures"] == []
    assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values())
    assert "No running processes found" in post["ixsmi"]
    assert all(value is None or "\nState:\tZ " in value for value in post["owned_process_status"].values())
    assert sha(run / "postflight-sources/triton_unified_attention.py") == "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
    for phase in ("before", "after"):
        cpu = read(run / ("cpu-" + phase + "-context-16k.json"))
        assert int(cpu["cpu.cfs_quota_us"]) / int(cpu["cpu.cfs_period_us"]) == 6
    with (run / "gpu.csv").open(encoding="utf-8") as stream:
        gpu = list(csv.DictReader(stream))
    assert gpu and all(row["memory.total"].strip() == "32768 MiB" for row in gpu)
    database = {}
    for phase in ("before", "after"):
        directory = control / ("db-" + phase)
        db_manifest = read(directory / "manifest.json")
        physical = sha(directory / "snapshot.sqlite")
        assert physical == db_manifest["snapshot_sha256"]
        if physical not in db_cache:
            db_cache[physical] = helper.fingerprint((directory / "snapshot.sqlite").resolve())
        keys = ("schema_sha256", "logical_content_sha256", "table_count", "row_count")
        assert all(db_cache[physical][key] == db_manifest[key] for key in keys)
        database[phase] = {"snapshot_sha256": physical, **{key: db_cache[physical][key] for key in keys}}
    assert database["before"] == database["after"]
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    lines = log.splitlines()
    kv, = re.findall(r"GPU KV cache size: ([\d,]+) tokens", log)
    metrics = {}
    for phase in ("before", "after"):
        text = (run / ("metrics-" + phase + "-context-16k.prom")).read_text(encoding="utf-8")
        metrics[phase] = sum(map(float, re.findall(r'^vllm:num_preemptions_total\{[^\n]*\} ([\d.e+\-]+)$', text, re.M)))
    load, = read(run / "load-commands.json")
    load[2] = "<run/context-16k>"
    row = {"run": name, "raw_sha256": sha(raw_path), "manifest_sha256": sha(run / "manifest.json"),
           "archive_sources_rehashed": len(sources), "remote_live_source_report_passed": True,
           "duration_s": raw["duration"], "total_tps": raw["total_token_throughput"],
           "ttft_ms": raw["mean_ttft_ms"], "tpot_ms": raw["mean_tpot_ms"],
           "shape": [32, 0, 524288, 4096], "kv_tokens": int(kv.replace(",", "")),
           "database": database, "preemptions": metrics, "idle_verified": True,
           "shutdown_error_lines": [line for line in lines if "ERROR" in line or "EngineDeadError" in line],
           "periodic_prompt_throughputs": re.findall(r"Avg prompt throughput: ([\d.]+) tokens/s", log),
           "compiler_evidence": "No per-derived-JIT compile/cache timing or hit-count captured. Startup torch.compile/AOT cache messages do not prove later mapped-JIT hits."}
    selected = [i for i, line in enumerate(lines) if "BIV150_MAPPED_DECODE_FIRST_SELECTED" in line]
    if selected:
        index = selected[0]
        assert "real_execute=1" in lines[index]
        before = next(line for line in reversed(lines[:index]) if "Avg prompt throughput:" in line)
        after = next(line for line in lines[index + 1:] if "Avg prompt throughput:" in line)
        row["first_real_selected"] = {"line": lines[index], "preceding_timestamped_log": before,
                                      "following_timestamped_log": after,
                                      "full_coverage_or_counts": "unobserved; first marker is not aggregate"}
    runs.append(row); source_maps.append(sources); manifests.append(manifest); loads.append(load)
assert manifests[0]["server_command"] == manifests[1]["server_command"]
assert manifests[0]["packages"] == manifests[1]["packages"] and manifests[0]["seed"] == manifests[1]["seed"] == 721201
assert loads[0] == loads[1] and runs[0]["database"] == runs[1]["database"]
installed = [{key: value for key, value in m["sha256"].items() if not key.startswith(m["source_dir"] + "/")} for m in manifests]
assert installed[0] == installed[1]
base, candidate = runs
out = {"kind": "BI-V150 mapped首次真实服务独立复核；同参数/同DB，KV不完全匹配",
       "runs": runs, "server_and_load_commands_equal": True, "installed_source_hashes_equal": True,
       "source_differences": {key: {"baseline": source_maps[0].get(key), "candidate": source_maps[1].get(key)}
                              for key in sorted(source_maps[0].keys() | source_maps[1].keys()) if source_maps[0].get(key) != source_maps[1].get(key)},
       "comparison": {"duration_added_s": candidate["duration_s"] - base["duration_s"],
                      "duration_change_percent": (candidate["duration_s"] / base["duration_s"] - 1) * 100,
                      "total_tps_change_percent": (candidate["total_tps"] / base["total_tps"] - 1) * 100,
                      "ttft_change_percent": (candidate["ttft_ms"] / base["ttft_ms"] - 1) * 100,
                      "kv_difference_candidate_minus_baseline": candidate["kv_tokens"] - base["kv_tokens"]},
       "conclusion": "本轮服务负结果保留；不直接归因为cold compile或coverage开销，不合入final。",
       "limits": ["首个D15真实选中夹在02:58:42–02:58:52，无精确时间或最终覆盖计数。",
                  "双方都有一个3276左右prompt低窗，不能把候选低窗独自当冷编译证明。",
                  "DB相同不代表Triton cache/CPU热状态相同；无per-JIT编译/命中日志。",
                  "单层正信号不代表服务获益。scheduled几何、prefill/decode/层外占比及CPU计划开销未知。",
                  "按root决定仅必要一次原runtime/参数不变repeat；不新增observer/cache扫描脚本，不覆盖首轮。",
                  "候选shutdown信号后有AsyncLLM/EngineDeadError，原样保留；32请求完成/driverexit0/postidle通过，不写全程无错误。"]}
destination = Path(__file__).with_name("first-service-review.json")
destination.write_text(json.dumps(out, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "verified_negative_first_service", "sources": [x["archive_sources_rehashed"] for x in runs],
                  "duration_s": [x["duration_s"] for x in runs], "kv_tokens": [x["kv_tokens"] for x in runs],
                  "comparison": out["comparison"], "result": str(destination)}, indent=2))
