"""本地stdlib复算已封存的启动smoke，不运行框架/设备/新测试。"""
import ast
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
PINS = {
    "launch.sh": "5bdb67afe573d9ffc803e40bafcaee2e7e7fd85e8b831bb94137516e85c060fd",
    "prepare_kv_memory_observer_source.py": "0ab0ce3ab3d8cde4a8e725d9fdfd3e62726fcf95613fbc1e55b850b3e48a9029",
    "biv150_kv_memory_observer.py": "6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c",
    "prepare_innovation_source.py": "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca",
    "run_framework_screen.py": "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9",
    "snapshot_tuning_db.py": "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2",
}
INIT = {"stable": "00e8def05ec16d3dcc01bcfe47c976dd4954402984b0a9ba1162d4b72547c3f4",
        "capacity": "39fb96f474c4bacc79ba4cdc1ae27ce877f9dd654825c792dc8446ac620b08e0"}


def inspect(name):
    match = re.fullmatch(r"\d{8}T\d{6}Z-kv-memory-(stable|capacity)-smoke", name)
    assert match
    variant = match[1]
    run = ROOT / "experiments/framework" / name
    control = Path(str(run) + "-control")
    assert (run / "exit-code").read_text().strip() == "0"
    for key, value in PINS.items():
        assert sha(control / key) == value, key
    assert sha(run / "screen-driver.py") == PINS["run_framework_screen.py"]
    sources, manifest = read(control / "source-sha256.json"), read(run / "manifest.json")
    count = 412 if variant == "stable" else 418
    assert len(sources) == count and all(sha(control / "plugin-source" / n) == h for n, h in sources.items())
    prepared = read(control / "plugin-source/memory-observer-source.json")
    prior_control = ROOT / "experiments/framework/20261021T212106Z-kv-capacity-context16k-long-control"
    assert sha(prior_control / "source-sha256.json") == "73e5d880f5a92f528618ffda71677c2b56c4b49ae582258dc0946ff20809a436"
    assert sha(prior_control / "plugin-source/innovation-source.json") == "5bef5daf33f8d4ed31f4d146106ff2eb23f5a05f317c256f544a07332a6f872d"
    original = (read(prior_control / "plugin-source/innovation-source.json")["input_sha256"]
                if variant == "stable" else read(prior_control / "source-sha256.json"))
    assert prepared["variant"] == variant and prepared["input_sha256"] == original
    assert prepared["preparer_sha256"] == PINS["prepare_kv_memory_observer_source.py"]
    expected = {**original, "vllm_fl/__init__.py": INIT[variant],
                "vllm_fl/patches/biv150_kv_memory_observer.py": PINS["biv150_kv_memory_observer.py"]}
    assert prepared["output_sha256_excluding_this_manifest"] == expected
    assert sources == {**expected, "memory-observer-source.json": sha(control / "plugin-source/memory-observer-source.json")}
    assert sources["vllm_fl/worker/worker.py"] == "a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24"
    assert sources["vllm_fl/worker/model_runner.py"] == "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
    if variant == "capacity":
        assert sources["innovation-source.json"] == original["innovation-source.json"]
    tree = ast.parse((control / "biv150_kv_memory_observer.py").read_bytes())
    footer, = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
               and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "INIT_FOOTER"]
    init = (control / "plugin-source/vllm_fl/__init__.py").read_bytes()
    assert init.endswith(footer) and hashlib.sha256(init[:-len(footer)]).hexdigest() == original["vllm_fl/__init__.py"]
    server, = [ast.literal_eval(n.value) for n in ast.parse((run / "screen-driver.py").read_bytes()).body
               if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "SERVER"]
    assert read(run / "launch-command.json") == manifest["server_command"] == server
    assert manifest["smoke_only"] is True and manifest["smoke_repeats"] == 1 and manifest["seed"] == 721201
    assert not any(manifest[k] for k in ("native_profile", "host_profile", "decode_screen", "context_screen", "context_long_screen"))
    assert manifest["require_log_marker"] == '"event": "DETERMINE_RETURN"'
    assert (control / "command.txt").read_text().startswith("BIV150_KV_VERIFY_RESTORE=0 ")
    payload, smoke = read(run / "smoke-request.json"), read(run / "smoke.json")
    assert payload == {"model": "minicpm", "prompt": "Explain what an inference engine does.",
                       "temperature": 0, "seed": 71, "max_tokens": 32, "logprobs": 2, "return_token_ids": True}
    choice, = smoke["choices"]
    assert smoke["model"] == "minicpm" and choice["finish_reason"] == "length"
    assert len(choice["token_ids"]) == smoke["usage"]["completion_tokens"] == 32
    assert len(choice["logprobs"]["token_logprobs"]) == 32
    assert smoke["usage"]["prompt_tokens"] + 32 == smoke["usage"]["total_tokens"]
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    events = [json.loads(line.split("BIV150_KV_MEMORY_OBSERVER ", 1)[1]) for line in log.splitlines() if "BIV150_KV_MEMORY_OBSERVER " in line]
    assert events and set(e["event"] for e in events) == {"ARMED", "DETERMINE_RETURN", "PARENT_RETURN"}
    determine, = [e for e in events if e["event"] == "DETERMINE_RETURN"]
    parent, = [e for e in events if e["event"] == "PARENT_RETURN"]
    assert all(e["observational_only"] is True and e["new_gpu_samples"] is False for e in events)
    assert determine["pid"] == parent["pid"] and determine["profile_context_calls"] == 1
    assert determine["error_type"] is None and parent["error_type"] is None
    assert type(determine["returned"]) is int and determine["returned"] > 0
    assert parent["returned_type"] == "list" and parent["returned"] == [determine["returned"]]
    assert set(parent["restored"]) == {"worker_method", "profiling_context", "parent_method"}
    assert all(v is True for v in parent["restored"].values()) and events.index(determine) < events.index(parent)
    assert all(type(v) in (int, float) and v >= 0 for part in ("worker_fields", "profile") for v in determine[part].values())
    for key in ("init_snapshot", "before_create", "before_profile", "after_profile"):
        assert len(determine[key]) == 8 and all(type(v) in (int, float, bool) for v in determine[key].values())
    assert any(e["event"] == "ARMED" and e["pid"] == determine["pid"] for e in events)
    post = read(run / "postflight-full.json")
    assert post["source_count"] == count and not post["source_failures"]
    assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values()) and "No running processes found" in post["ixsmi"]
    assert all(value is None or "\nState:\tZ " in value for value in post["owned_process_status"].values())
    assert sha(run / "postflight-sources/triton_unified_attention.py") == "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
    gpu = list(csv.DictReader((run / "gpu.csv").open(encoding="utf-8")))
    assert gpu and all(x["memory.total"].strip() == "32768 MiB" and "BI-V150" in x["gpu_name"] for x in gpu)
    for cpu in (manifest["cpu_before"], read(run / "cpu-final.json")):
        assert int(cpu["cpu.cfs_quota_us"]) / int(cpu["cpu.cfs_period_us"]) == 6
    helper = ROOT / "scripts/remote/snapshot_tuning_db.py"
    assert sha(helper) == PINS["snapshot_tuning_db.py"]
    spec = importlib.util.spec_from_file_location("readonly_memory_db", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    database = {}
    for phase in ("before", "after"):
        directory = control / ("db-" + phase)
        recorded = read(directory / "manifest.json")
        actual = module.fingerprint((directory / "snapshot.sqlite").resolve())
        assert sha(directory / "snapshot.sqlite") == recorded["snapshot_sha256"]
        keys = ("schema_sha256", "logical_content_sha256", "table_count", "row_count")
        assert all(actual[k] == recorded[k] for k in keys)
        database[phase] = {"snapshot_sha256": recorded["snapshot_sha256"], **{k: actual[k] for k in keys}}
    before, _, shutdown = log.partition("[shutdown] API server: shutdown triggered")
    errors = {"before_shutdown": [x for x in before.splitlines() if "ERROR" in x],
              "during_shutdown": [x for x in shutdown.splitlines() if "ERROR" in x]}
    assert not errors["before_shutdown"]
    kv, = re.findall(r"GPU KV cache size: ([\d,]+) tokens", log)
    return {"status": "passed_startup_scalar_diagnostic", "run_id": name, "variant": variant,
        "started_utc": manifest["started_utc"], "finished_utc": (run / "finished-at.txt").read_text().strip(),
        "source_count_verified": count, "source_manifest_sha256": sha(control / "source-sha256.json"),
        "observer_events": events, "actual_pid": determine["pid"], "kv_tokens": int(kv.replace(",", "")),
        "smoke_sha256": sha(run / "smoke.json"), "smoke_usage": smoke["usage"],
        "database": database, "database_before_after_equal": database["before"] == database["after"],
        "postflight_utc": post["utc"], "postflight_idle_verified": True,
        "CPU_cores": 6, "physical_memory_mib": 32768, "errors": errors,
        "forcekill_warnings": [x for x in shutdown.splitlines() if "force killing remaining" in x],
        "validator_sha256": sha(Path(__file__)), "performance_calculated": False,
        "limits": ["只验收启动已有标量/原返回与hook恢复；不测性能/模型accuracy或历史6块原因。",
                   "ARMED可跨API/Core多PID，实际determine/profile/parent只用同PID；无新GPU采样。",
                   "字段与logger解释由hardware另审；完整raw事件保留，重构值不是新采样。"]}


if __name__ == "__main__":
    assert not sys.flags.optimize
    run_id, output = sys.argv[1:]
    result = inspect(run_id)
    with Path(output).open("x", encoding="utf-8", newline="\n") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(json.dumps({k: result[k] for k in ("status", "source_count_verified", "actual_pid", "kv_tokens", "database_before_after_equal", "postflight_utc")}))
