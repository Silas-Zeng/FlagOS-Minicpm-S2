"""仅读195012真实smoke：逐源SHA、实际descriptor、DB和清理，不导入框架。"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/framework/20261021T195012Z-kv-runtime-descriptor-smoke"
CONTROL = RUN.with_name(RUN.name + "-control")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = read(RUN / "manifest.json")
sources = read(CONTROL / "source-sha256.json")
assert len(sources) == 412
assert all(sha(CONTROL / "plugin-source" / name) == value for name, value in sources.items())
assert sources["vllm_fl/patches/biv150_kv_runtime_descriptor.py"] == "0c892ad02fbfe663d3f7c8f668cdd000c0c1fc7860ff915db8bce5949cae0667"
assert sources["vllm_fl/__init__.py"] == "90fe0b381fd53ec5273c623d91b806a0fc21f5b84165beba0b015a1e07d53e74"
assert sources["vllm_fl/worker/model_runner.py"] == "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
assert sha(CONTROL / "prepare_kv_runtime_descriptor_source.py") == "936c9260724f97b02dc1e69da2f4f0da7cdfaf7fdcb0e8ab866c26d9c028c59e"
assert sha(RUN / "screen-driver.py") == "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9"
pack = read(CONTROL / "plugin-source/innovation-source.json")
assert len(pack["input_sha256"]) == 410
assert set(pack["changes"]) == {"vllm_fl/__init__.py", "vllm_fl/patches/biv150_kv_runtime_descriptor.py"}
assert {k: v for k, v in sources.items() if k != "innovation-source.json"} == pack["output_sha256_excluding_this_manifest"]
assert read(RUN / "launch-command.json") == manifest["server_command"]
assert manifest["smoke_only"] and manifest["smoke_repeats"] == 1 and manifest["seed"] == 721201
assert not any(manifest[key] for key in ("native_profile", "host_profile", "decode_screen", "context_screen", "context_long_screen"))
assert (RUN / "exit-code").read_text().strip() == "0"
cpu = manifest["cpu_before"]
assert int(cpu["cpu.cfs_quota_us"]) / int(cpu["cpu.cfs_period_us"]) == 6
with (RUN / "gpu.csv").open(encoding="utf-8") as stream:
    gpu = list(csv.DictReader(stream))
assert gpu and all(row["memory.total"].strip() == "32768 MiB" for row in gpu)
smoke = read(RUN / "smoke.json")
assert "error" not in smoke and len(smoke["choices"]) == 1
assert smoke["usage"]["prompt_tokens"] == 8 and smoke["usage"]["completion_tokens"] == 32
worker_path, = (RUN / "kv-descriptors").glob("worker-kv-*.json")
core_path, = (RUN / "kv-descriptors").glob("core-objects-*.json")
worker, core = read(worker_path), read(core_path)
assert worker["status"] == "observed_complete" and core["status"] == "observed"
assert worker["pid"] == core["pid"] == 213942
assert worker["worker"] == core["direct_worker"] and worker["runner"] == core["direct_runner"]
expected_classes = {"engine": ("vllm.v1.engine.core", "EngineCoreProc"),
                    "executor": ("vllm.v1.executor.uniproc_executor", "UniProcExecutor"),
                    "driver_worker_wrapper": ("vllm.v1.worker.worker_base", "WorkerWrapperBase"),
                    "direct_worker": ("vllm_fl.worker.worker", "WorkerFL"),
                    "direct_runner": ("vllm_fl.worker.model_runner", "ModelRunnerFL"),
                    "scheduler": ("vllm.v1.core.sched.async_scheduler", "AsyncScheduler")}
for name, (module, qualname) in expected_classes.items():
    assert (core[name]["module"], core[name]["qualname"]) == (module, qualname)
assert core["phase"] == "first_engine_step_after_constructor" and core["batch_queue_size"] == 2 and core["async_scheduling"] is True
assert worker["layer_count"] == worker["runner_kv_cache_count"] == worker["storage_alias_group_count"] == 42
assert worker["configured_num_blocks"] == 32621 and worker["kernel_block_sizes"] == [16]
assert worker["cross_layers_kv_cache"] == {"status": "observed_none"} and worker["shared_kv_cache_layers"] == {}
flat = worker["runner_kv_cache_list"]
views = [row["kv_views"][0] for row in worker["layers"]]
assert len({row["layer_name"] for row in worker["layers"]}) == 42
assert all(len(row["kv_views"]) == 1 for row in worker["layers"])
assert len({row["storage_alias_group"] for row in flat}) == 42
assert {row["storage_alias_group"] for row in flat} == {row["storage_alias_group"] for row in views}
for row in flat + views:
    assert row["status"] == "observed" and row["shape"] == [32621, 2, 16, 2, 128]
    assert row["stride"] == [8192, 4096, 256, 128, 1] and row["storage_offset_elements"] == 0
    assert row["dtype"] == "torch.bfloat16" and row["device"] == "cuda:0"
    assert row["logical_nbytes"] == row["storage_nbytes"] == 534462464 and row["element_size_bytes"] == 2
for row in (worker, core):
    assert all(row[name] is False for name in ("tensor_values_read", "gpu_synchronization_requested", "gpu_buffers_allocated", "scheduling_changed"))
    assert row["current_stream"].startswith("unobserved")
log = (RUN / "server.log").read_text(encoding="utf-8", errors="replace")
assert "GPU KV cache size: 521,936 tokens" in log
assert "BIV150_KV_RUNTIME_DESCRIPTOR_INSTALLED" in log
assert not any("BIV150_KV_RUNTIME_DESCRIPTOR_" + item in log for item in ("ERROR", "WRITE_ERROR", "REJECTED"))
hp = ROOT / "scripts/remote/snapshot_tuning_db.py"
assert sha(hp) == "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2"
spec = importlib.util.spec_from_file_location("descriptor_actual_db", hp)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
database = []
for phase in ("before", "after"):
    directory = CONTROL / ("db-" + phase)
    saved = read(directory / "manifest.json")
    fingerprint = helper.fingerprint((directory / "snapshot.sqlite").resolve())
    value = {"snapshot_sha256": sha(directory / "snapshot.sqlite"),
             **{k: fingerprint[k] for k in ("schema_sha256", "logical_content_sha256", "table_count", "row_count")}}
    assert all(value[k] == saved[k] for k in value)
    database.append(value)
assert database[0] == database[1]
post = read(RUN / "postflight-full.json")
assert post["source_count"] == 412 and post["source_failures"] == []
assert post["query"].strip() == "68, 0" and all(post["ports_closed"].values())
assert "No running processes found" in post["ixsmi"]
assert all(value is None or "\nState:\tZ " in value for value in post["owned_process_status"].values())
assert sha(RUN / "postflight-sources/triton_unified_attention.py") == "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
report = {"status": "actual_normal42_and_local_executor_verified", "run": RUN.name,
          "sha256": {"manifest": sha(RUN / "manifest.json"), "worker_event": sha(worker_path), "core_event": sha(core_path)},
          "source_count_rehashed": 412, "original_runner_unchanged": True, "observed_pid": worker["pid"],
          "worker_and_runner_object_identity_matches_core": True, "classes": expected_classes,
          "kv_shape": flat[0]["shape"], "kv_stride": flat[0]["stride"], "storage_offset_elements": 0,
          "layout": "normal42独立storage；不是packed42", "storage_alias_group_count": 42,
          "bytes_per_layer": 534462464, "total_kv_bytes": 42 * 534462464,
          "block_count": 32621, "kv_tokens": 521936, "batch_queue_size": 2,
          "cross_layers_kv_cache": worker["cross_layers_kv_cache"], "database": database[0],
          "cpu_quota": 6, "physical_memory_mib": 32768, "smoke_tokens": [8, 32],
          "worker_cgroup_snapshot": worker["cgroup_snapshot"], "core_cgroup_snapshot": core["cgroup_snapshot"],
          "postflight_utc": post["utc"], "postflight_idle_verified": True,
          "log_error_lines": [line for line in log.splitlines() if "ERROR" in line or "EngineDeadError" in line],
          "limits": ["该一次加载布局和同pid直接对象已观测，不证明任何copy完成或恢复协议。",
                     "CPU/cgroup仅时点与限额，未测峰值或保证pinned可分配。",
                     "smoke一请求非吞吐或accuracy；current stream未观察；不继承构造packed成本。"]}
destination = Path(__file__).with_name("actual-smoke-review.json")
destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ("status", "source_count_rehashed", "observed_pid", "layout", "kv_tokens", "database", "postflight_utc")}, ensure_ascii=True, indent=2))
