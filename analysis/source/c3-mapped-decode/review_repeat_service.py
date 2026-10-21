"""只读复核mapped未改代码的一次复核；不覆盖首次负结果。"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
NAMES = (
    "20261021T183543Z-baseline-context16k",
    "20261021T184244Z-baseline-context16k",
    "20261021T185627Z-mapped-decode-context16k",
    "20261021T191131Z-mapped-decode-context16k",
)
DRIVER = "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9"
HELPER = "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2"
OLD_REVIEW = "258793116a996974f9f92c2bf83dc721d9713e887726e9c64e541c480940806b"
EXPECTED_MAPPED = {
    "vllm_fl/patches/biv150_mapped_decode.py": "d085ad6dcc0fd5dc26188d3e0f5801b8e394dc07a79c05a376192ec9e1e95b4b",
    "vllm_fl/patches/biv150_mapped_decode_source.py": "919e80abf5b95c55ea63aa8619fa3202cd78b0c4cc0e303df7b4197bf1898316",
    "vllm_fl/patches/biv150_mapped_attention.py": "72713a90584bc6567706fb881188afa04335230afc13e021c10f862f88d054a1",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


hp = ROOT / "scripts/remote/snapshot_tuning_db.py"
assert sha(hp) == HELPER
spec = importlib.util.spec_from_file_location("mapped_repeat_review_sqlite", hp)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
old = Path(__file__).with_name("first-service-review.json")
assert sha(old) == OLD_REVIEW
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
    assert manifest["context_screen"] and not any(manifest[x] for x in (
        "decode_screen", "context_long_screen", "host_profile", "native_profile", "smoke_only"))
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
    assert metrics == {"before": 0, "after": 0}
    load, = read(run / "load-commands.json")
    load[2] = "<run/context-16k>"
    row = {
        "run": name, "raw_sha256": sha(raw_path), "manifest_sha256": sha(run / "manifest.json"),
        "archive_sources_rehashed": len(sources), "remote_live_source_report_passed": True,
        "duration_s": raw["duration"], "total_tps": raw["total_token_throughput"],
        "ttft_ms": raw["mean_ttft_ms"], "tpot_ms": raw["mean_tpot_ms"],
        "shape": [32, 0, 524288, 4096], "kv_tokens": int(kv.replace(",", "")),
        "cpu_quota": 6, "device_memory_mib": 32768, "database": database, "preemptions": metrics,
        "idle_verified": True, "postflight_utc": post["utc"],
        "shutdown_error_lines": [line for line in lines if "ERROR" in line or "EngineDeadError" in line],
        "periodic_prompt_throughputs": re.findall(r"Avg prompt throughput: ([\d.]+) tokens/s", log),
        "compiler_cache_state": "未观测每个派生JIT的命中/编译时间，不能称全热；启动AOT缓存消息不构成证明。",
    }
    selected = [i for i, line in enumerate(lines) if "BIV150_MAPPED_DECODE_FIRST_SELECTED" in line]
    if selected:
        index = selected[0]
        assert len(selected) == 1 and "real_execute=1" in lines[index]
        row["first_real_selected"] = {
            "line": lines[index],
            "preceding_timestamped_log": next(line for line in reversed(lines[:index]) if "Avg prompt throughput:" in line),
            "following_timestamped_log": next(line for line in lines[index + 1:] if "Avg prompt throughput:" in line),
            "full_coverage_or_counts": "未观测；first marker不是全程计数。",
        }
    runs.append(row)
    source_maps.append(sources)
    manifests.append(manifest)
    loads.append(load)

assert all(m["server_command"] == manifests[0]["server_command"] and
           m["packages"] == manifests[0]["packages"] and m["seed"] == 721201 for m in manifests)
assert all(load == loads[0] for load in loads)
assert all(run["database"] == runs[0]["database"] for run in runs)
installed = [{key: value for key, value in m["sha256"].items()
              if not key.startswith(m["source_dir"] + "/")} for m in manifests]
assert all(item == installed[0] for item in installed)
assert source_maps[0] == source_maps[1] and len(source_maps[0]) == 410
assert len(source_maps[2]) == len(source_maps[3]) == 414
source_differences = {key: {"first": source_maps[2].get(key), "repeat": source_maps[3].get(key)}
                      for key in source_maps[2].keys() | source_maps[3].keys()
                      if source_maps[2].get(key) != source_maps[3].get(key)}
assert set(source_differences) == {"innovation-source.json"}
packaging = [read(ROOT / "experiments/framework" / (name + "-control") /
                  "plugin-source/innovation-source.json") for name in NAMES[2:]]
assert {key for key in packaging[0].keys() | packaging[1].keys()
        if packaging[0].get(key) != packaging[1].get(key)} == {"created_utc", "command", "output"}
for item in packaging:
    command = list(item["command"])
    command[command.index("--output") + 1] = "<new-source>"
    item["command"] = command
    del item["created_utc"], item["output"]
assert packaging[0] == packaging[1]
assert all(source_maps[2][key] == value for key, value in EXPECTED_MAPPED.items())
assert all("first_real_selected" in run for run in runs[2:])
assert [run["kv_tokens"] for run in runs] == [521936, 521936, 521840, 521840]


def compare(base, candidate):
    return {
        "baseline": base["run"], "candidate": candidate["run"],
        "duration_added_s": candidate["duration_s"] - base["duration_s"],
        "duration_change_percent": (candidate["duration_s"] / base["duration_s"] - 1) * 100,
        "total_tps_change_percent": (candidate["total_tps"] / base["total_tps"] - 1) * 100,
        "ttft_change_percent": (candidate["ttft_ms"] / base["ttft_ms"] - 1) * 100,
        "kv_difference_candidate_minus_baseline": candidate["kv_tokens"] - base["kv_tokens"],
    }


out = {
    "kind": "天数BI-V150 mapped未改代码的一次服务复核；首轮负、复核正并列保留",
    "runs": runs, "server_and_load_commands_equal": True, "installed_source_hashes_equal": True,
    "candidate_413_nonmanifest_file_hashes_equal": True,
    "packaging_manifest_only_differs_by_utc_and_output_path": source_differences,
    "first_review_sha256_unchanged": OLD_REVIEW,
    "descriptive_baseline_comparisons": [compare(base, cand) for base in runs[:2] for cand in runs[2:]],
    "same_candidate_repeat_comparison": compare(runs[2], runs[3]),
    "conclusion": "复核出现正信号，与首轮负信号同时成立；不能据两轮认定稳定收益、全热、KVmatched或冷编译因果。保留候选，不直接合入final。",
    "limits": [
        "两个baseline同KV521936，candidate两轮同KV521840；baseline对candidate均非完全matched。",
        "首轮与复核source/参数/DB/KV相同，但先后时序和编译缓存/主机状态未严格控制；不是ABBA或稳定性证明。",
        "两个FIRST_SELECTED均为真实EngineCore/D15，不是全程mapped命中率或forward总量。",
        "32请求成功不是整模型accuracy门；新3D归约顺序仍需独立准确率，不继承103/105。",
        "首轮shutdown后的EngineDeadError等保留；postidle与driverexit0不等于全程无告警。",
        "按root决定不盲刷服务、不添加observer、不更改runtime；后续由主负责人统一选择。",
    ],
}
assert sha(old) == OLD_REVIEW
destination = Path(__file__).with_name("repeat-service-review.json")
destination.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "verified_mixed_service_signals", "sources": [x["archive_sources_rehashed"] for x in runs],
                  "durations_s": [x["duration_s"] for x in runs], "comparisons": out["descriptive_baseline_comparisons"],
                  "same_candidate_repeat": out["same_candidate_repeat_comparison"], "result": str(destination)}, ensure_ascii=True, indent=2))
