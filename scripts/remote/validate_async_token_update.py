#!/usr/bin/env python3
"""Prepare/run the short integer async-input gate; no weights or performance score.

Import and --help are CPU-only. The controller owns the device lock and starts
one worker, then records postflight after that worker's CUDA context exits.
Run only after independent review and after the current device job is gone.
"""

from __future__ import annotations

import argparse
import ast
from collections.abc import Mapping
import copy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
import traceback
from types import SimpleNamespace as NS


EXPECTED_RUNNER = "446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64"
EXPECTED_RUNTIME = "1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc"
EXPECTED_TRANSFORM = "e5a84a3cd90a81ec7134a3646b36921454be647ba1cb2a1936460c849a2daf8c"
EXPECTED_PATCHED = "ce1860c89760c851c2f6b3bb4c35dd334e01e7927844c5460ec35f407633fdbc"
CASES = (
    dict(name="identity_slice", lengths=[1] * 8, previous=list(range(8)), rows=8, selected=0),
    dict(name="no_previous", lengths=[1, 3], previous=[-1, -1], rows=4, selected=0, no_previous=True),
    dict(name="empty", lengths=[], previous=[], rows=1, selected=0),
    dict(name="no_common", lengths=[3, 2], previous=[-1, -1], rows=5, selected=0),
    dict(name="removal_and_condense", lengths=[1] * 5, previous=[7, 0, 1, 3, 5], rows=8, selected=1),
    dict(name="reorder", lengths=[1] * 4, previous=[2, 0, 3, 1], rows=4, selected=1),
    dict(name="new_prefill_holes", lengths=[1, 3, 1, 2], previous=[4, -1, 1, -1], rows=6, selected=1),
    dict(name="positive_strides", lengths=[1] * 3, previous=[2, 0, 1], rows=4, selected=1, stride=2),
    dict(name="int64_fallback", lengths=[1] * 3, previous=[2, 0, 1], rows=4, selected=0, dtype="int64"),
    dict(name="prompt_embeds_fallback", lengths=[1] * 3, previous=[2, 0, 1], rows=4, selected=0, embeds=True),
    dict(name="spec_draft_fallback", lengths=[2, 2], previous=[2, 0], rows=3, selected=0, spec=True),
    dict(name="cross_stream", lengths=[1, 3, 1, 2], previous=[4, -1, 1, -1], rows=6, selected=1, cross_stream=True),
)


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def extract_method(source, namespace):
    """Execute only the pinned real method, never runner imports/init/weights."""
    tree = ast.parse(source)
    classes = [x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == "ModelRunnerFL"]
    if len(classes) != 1:
        raise RuntimeError("missing unique ModelRunnerFL")
    methods = [x for x in classes[0].body if isinstance(x, ast.FunctionDef) and x.name == "_prepare_input_ids"]
    if len(methods) != 1 or methods[0].decorator_list:
        raise RuntimeError("unexpected _prepare_input_ids")
    node = copy.deepcopy(methods[0])
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), node], type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, "archived:_prepare_input_ids", "exec"), namespace)
    return namespace["_prepare_input_ids"]


def cache_snapshot(jit):
    """Read populated dictionaries only; never index a new device-cache key."""
    caches = getattr(jit, "__dict__", {}).get("device_caches")
    if not isinstance(caches, Mapping):
        return {"status": "unavailable", "reason": "unrecognized existing device_caches"}
    devices, records = [], []
    for device, entry in caches.items():
        if not isinstance(entry, (tuple, list)) or not entry or not isinstance(entry[0], Mapping):
            return {"status": "unavailable", "reason": "unrecognized populated cache tuple"}
        kernels = entry[0]
        devices.append({"device": str(device), "entries": len(kernels), "keys": sorted(str(k) for k in kernels)})
        for kernel in kernels.values():
            metadata = getattr(kernel, "__dict__", {}).get("metadata")
            if metadata is not None:
                row = {}
                for key in ("name", "num_warps", "num_stages", "warp_size", "shared", "constants"):
                    value = metadata.get(key) if isinstance(metadata, Mapping) else getattr(metadata, key, None)
                    if value is not None:
                        row[key] = value if isinstance(value, (str, int, bool, float)) else str(value)
                records.append(row)
    return {"status": "available" if devices else "unavailable", "devices": devices, "metadata": records,
            "entries": sum(x["entries"] for x in devices)}


def make_runner(torch, np, case):
    dtype = getattr(torch, case.get("dtype", "int32"))
    stride, capacity = case.get("stride", 1), sum(case["lengths"]) + 9
    class Buffer:
        def __init__(self, data, tensor_dtype):
            self.cpu = data.to(tensor_dtype).pin_memory()
            shape = (capacity * stride, *data.shape[1:])
            self.storage = torch.full(shape, -99 if tensor_dtype != torch.bool else False,
                                      dtype=tensor_dtype, device="cuda")
            self.gpu = self.storage[::stride]
            self.copies = []
        def copy_to_gpu(self, count):
            self.copies.append(count)
            self.gpu[:count].copy_(self.cpu[:count], non_blocking=True)
    data = torch.arange(capacity, dtype=torch.int64) * 7 + 1000
    source_storage = torch.empty((case["rows"] * stride,), dtype=dtype, device="cuda")
    # Signed extremes verify integer copy, not a float round trip.
    pattern = torch.tensor([-2147483648, -1, 0, 1, 130559, 2147483647], dtype=dtype)
    values = pattern.repeat((case["rows"] + 5) // 6)[:case["rows"]]
    source_storage.fill_(-81)
    source_storage[::stride].copy_(values.to("cuda"))
    src = source_storage[::stride].reshape(case["rows"], 1)
    config = NS(model_config=NS(model="/workspace/MiniCPM5-2B", dtype=torch.bfloat16,
            hf_text_config=NS(hidden_size=2048, num_hidden_layers=42, num_attention_heads=16, num_key_value_heads=2),
            is_encoder_decoder=False),
        parallel_config=NS(tensor_parallel_size=1, pipeline_parallel_size=1,
            decode_context_parallel_size=1, data_parallel_size=1, use_ubatching=False),
        speculative_config=object() if case.get("spec") else None, lora_config=None)
    runner = NS(vllm_config=config, use_async_scheduling=True, use_async_spec_decode=bool(case.get("spec")),
        num_spec_tokens=2 if case.get("spec") else 0, prev_num_spec_tokens=2 if case.get("spec") else 0,
        enable_prompt_embeds=bool(case.get("embeds")), use_aux_hidden_state_outputs=False,
        _draft_token_ids=None, uses_mrope=False, uses_xdrope_dim=0, device=torch.device("cuda"), pin_memory=True,
        prev_positions=NS(np=np.array(case["previous"], dtype=np.int64)),
        input_ids=Buffer(data, dtype), inputs_embeds=Buffer(torch.stack([data] * 4, dim=1), torch.float32),
        is_token_ids=Buffer(torch.zeros(capacity, dtype=torch.bool), torch.bool),
        input_batch=NS(req_ids=[f"r{i}" for i in range(len(case["lengths"]))],
                       prev_sampled_token_ids=None if case.get("no_previous") else src))
    if case.get("spec"):
        runner._draft_token_ids = torch.arange(case["rows"] * 2, dtype=torch.int64, device="cuda").reshape(case["rows"], 2) + 70000
    scheduled = NS(scheduled_spec_decode_tokens={name: [0] for name in runner.input_batch.req_ids} if case.get("spec") else {})
    return runner, scheduled, np.cumsum(case["lengths"], dtype=np.int64)


def compare_case(torch, np, runtime, original, changed, case):
    left, scheduled, cu = make_runner(torch, np, case)
    right, _, _ = make_runner(torch, np, case)
    before = runtime.selected_launches
    producer, consumer = torch.cuda.current_stream(), torch.cuda.current_stream()
    if case.get("cross_stream"):
        producer, consumer = torch.cuda.Stream(), torch.cuda.Stream()
        producer.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(producer):
            # Existing caller readiness is explicit; record_stream is not a wait.
            left.input_batch.prev_sampled_token_ids.add_(0)
            right.input_batch.prev_sampled_token_ids.add_(0)
        consumer.wait_stream(producer)
    with torch.cuda.stream(consumer):
        original(left, scheduled, len(case["lengths"]), int(cu[-1]) if len(cu) else 0, cu)
        changed(right, scheduled, len(case["lengths"]), int(cu[-1]) if len(cu) else 0, cu)
    consumer.synchronize()
    total = sum(case["lengths"])
    checks = {}
    for name in ("input_ids", "inputs_embeds", "is_token_ids"):
        a, b = getattr(left, name), getattr(right, name)
        checks[name] = torch.equal(a.storage, b.storage) and a.copies == b.copies
    checks["padding_unchanged"] = torch.equal(right.input_ids.gpu[total:],
        torch.full_like(right.input_ids.gpu[total:], -99))
    if right.input_ids.gpu.stride(0) > 1:
        checks["stride_holes_unchanged"] = torch.equal(right.input_ids.storage[1::2],
            torch.full_like(right.input_ids.storage[1::2], -99))
    checks["selection"] = runtime.selected_launches - before == case["selected"]
    row = {**case, "checks": checks, "selected_launches": runtime.selected_launches - before,
           "status": "pass" if all(checks.values()) else "reject"}
    # No use of view snapshots as evidence for races; readiness is explicit.
    return row


def dynamic_cache_gate(torch, runtime, runner):
    src_storage = torch.arange(64, device="cuda", dtype=torch.int32).reshape(64, 1) + 130000
    dst = torch.full((80,), -99, dtype=torch.int32, device="cuda")
    prev_storage = torch.empty((64,), dtype=torch.int64, device="cuda")
    target_storage = torch.empty_like(prev_storage)
    snapshots, rows = [], []
    for count in (62, 61, 60):
        n = count - 1
        previous, destinations = [*range(1, n), 0], list(range(n))
        prev_storage[:n].copy_(torch.tensor(previous, dtype=torch.int64, pin_memory=True), non_blocking=True)
        target_storage[:n].copy_(torch.tensor(destinations, dtype=torch.int64, pin_memory=True), non_blocking=True)
        dst.fill_(-99)
        expected = torch.full_like(dst, -99)
        # Independent CPU integer formula avoids adding another generic GPU
        # index path to the specialization observation itself.
        expected[:n].copy_(torch.tensor([130000 + i for i in previous], dtype=torch.int32, device="cuda"))
        selected = runtime.fused_sampled_token_update(runner, src_storage[:count], dst,
            prev_storage[:n], target_storage[:n], previous, destinations, n)
        torch.cuda.synchronize()
        snapshot = cache_snapshot(runtime._gather_scatter_i32)
        snapshots.append(snapshot)
        rows.append({"previous_rows": count, "n": n, "selected": selected,
                     "entire_storage_equal": torch.equal(dst, expected), "cache": snapshot})
    available = all(x["status"] == "available" for x in snapshots)
    stable = available and len({json.dumps(x["devices"], sort_keys=True) for x in snapshots}) == 1
    return {"rows": rows, "no_new_entries_after_first_dynamic_shape": stable,
            "status": "pass" if stable and all(x["selected"] and x["entire_storage_equal"] for x in rows)
                      else "cache_unavailable" if not available else "reject",
            "scope": "same storage addresses/dtypes/strides; runtime N/source rows/total vary; no global one-kernel assertion"}


def invalid_mapping_guards(torch, runtime, runner):
    src = torch.arange(4, dtype=torch.int32, device="cuda").reshape(4, 1)
    dst = torch.full((12,), -99, dtype=torch.int32, device="cuda")
    rows = []
    for previous, destinations in (([-1], [0]), ([4], [0]), ([0], [-1]), ([0], [8]), ([0, 1], [2, 2])):
        before = runtime.selected_launches
        selected = runtime.fused_sampled_token_update(runner, src, dst,
            torch.tensor(previous, dtype=torch.int64, device="cuda"),
            torch.tensor(destinations, dtype=torch.int64, device="cuda"), previous, destinations, 8)
        torch.cuda.synchronize()
        passed = not selected and runtime.selected_launches == before and bool((dst == -99).all().item())
        rows.append({"previous": previous, "destinations": destinations, "rejected_before_launch": passed})
    return {"rows": rows, "status": "pass" if all(x["rejected_before_launch"] for x in rows) else "reject",
            "limitation": "invalid original gather/scatter not launched; checks fallback decision and no writes, not error-message equivalence"}


def worker(run):
    result = {"status": "started", "cases": [], "limitations": [
        "Exact archived _prepare_input_ids methods with stub buffers/config; no model weights or scheduler/service loop.",
        "Integer entire-storage comparisons are correctness evidence, not model accuracy or performance.",
        "Cross-stream caller wait is explicit; not an exhaustive race/allocator schedule test.",
        "Cache observation covers one fixed-address 62/61/60 sequence; unavailable cache inspection is inconclusive."]}
    status = 1
    try:
        import numpy as np
        import torch
        runtime = load("vllm_fl.patches.biv150_async_token_update", run / "source/runtime.py")
        if torch.cuda.device_count() != 1:
            raise RuntimeError("expected one accelerator")
        torch.cuda.set_device(0)
        original = extract_method((run / "source/runner-original.py").read_bytes(), {"torch": torch, "np": np})
        changed = extract_method((run / "source/runner-patched.py").read_bytes(),
            {"torch": torch, "np": np, "_biv150_fused_sampled_token_update": runtime.fused_sampled_token_update})
        result["device"] = str(torch.cuda.get_device_properties(0))
        for case in CASES:
            row = compare_case(torch, np, runtime, original, changed, case)
            result["cases"].append(row)
            write_json(run / "results.json", result)
            if row["status"] != "pass":
                raise RuntimeError("actual-method comparison rejected: " + case["name"])
        runner, _, _ = make_runner(torch, np, CASES[4])
        result["invalid_mapping"] = invalid_mapping_guards(torch, runtime, runner)
        result["dynamic_cache"] = dynamic_cache_gate(torch, runtime, runner)
        passed = result["invalid_mapping"]["status"] == result["dynamic_cache"]["status"] == "pass"
        result["status"] = "passed_integer_wrapper_gate" if passed else "functional_gate_inconclusive_or_rejected"
        status = 0 if passed else 2
    except BaseException:
        result.update(status="failed", error=traceback.format_exc())
        print(result["error"], flush=True)
    result.update(finished_utc=utc(), worker_exit_code=status)
    write_json(run / "results.json", result)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--runner-path", type=Path)
    parser.add_argument("--runtime-path", type=Path)
    parser.add_argument("--transform-path", type=Path)
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir.resolve())
    if any(value is None for value in (args.runner_path, args.runtime_path, args.transform_path)):
        parser.error("controller requires --runner-path, --runtime-path and --transform-path")
    import fcntl
    import validate_block_table_candidate as validator
    root, run = validator.ROOT.resolve(), args.run_dir.resolve()
    if not run.is_relative_to(root) or run == root:
        raise ValueError("run directory outside experiment workspace")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {"started_utc": utc(), "pid": os.getpid(), "run_id_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
        "kind": "actual-method integer gate; no weights/service/score", "command": [sys.executable, *sys.argv],
        "command_shell": shlex.join([sys.executable, *sys.argv]), "python": sys.version, "platform": platform.platform()}
    status, lock, child, monitor, monitor_log = 1, None, None, None, None
    write_json(run / "manifest.json", manifest)
    write_json(run / "command.json", manifest["command"])
    try:
        lock = (root / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest["preflight"] = validator.preflight(args.ixsmi)
        manifest["lock_acquired_utc"] = utc()
        source = run / "source"
        source.mkdir()
        for label, path, expected in (
            ("runner-original.py", args.runner_path, EXPECTED_RUNNER),
            ("runtime.py", args.runtime_path, EXPECTED_RUNTIME),
            ("transform.py", args.transform_path, EXPECTED_TRANSFORM)):
            data = path.read_bytes()
            actual = hashlib.sha256(data).hexdigest()
            if actual != expected:
                raise RuntimeError(f"unaudited {label}: {actual}")
            (source / label).write_bytes(data)
        (source / "validation.py").write_bytes(Path(__file__).read_bytes())
        (source / "validator.py").write_bytes(Path(validator.__file__).read_bytes())
        (source / "monitor_gpu.sh").write_bytes((root / "scripts/monitor_gpu.sh").read_bytes())
        transform = load("async_update_gate_transform", source / "transform.py")
        (source / "runner-patched.py").write_bytes(transform.transform_source((source / "runner-original.py").read_bytes()))
        if digest(source / "runner-patched.py") != EXPECTED_PATCHED:
            raise RuntimeError("transformed runner differs from independently reviewed result")
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["environment"] = {k: os.environ[k] for k in ("PYTHONPATH", "VLLM_PLUGINS", "COREX_VISIBLE_DEVICES", "TRITON_CACHE_DIR", "OMP_NUM_THREADS", "MKL_NUM_THREADS") if k in os.environ}
        manifest["packages"] = {}
        for name in ("torch", "vllm", "vllm-plugin-fl", "flag-gems", "flagtree"):
            try:
                manifest["packages"][name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][name] = "unavailable"
        manifest["worker_command"] = [sys.executable, str(source / "validation.py"), "--worker", "--run-dir", str(run)]
        write_json(run / "manifest.json", manifest)
        with (run / "gate.log").open("x", encoding="utf-8") as log:
            child = subprocess.Popen(manifest["worker_command"], stdout=log, stderr=subprocess.STDOUT)
            manifest["worker_pid"] = child.pid
            monitor_log = (run / "monitor.log").open("x", encoding="utf-8")
            monitor = subprocess.Popen(["bash", str(source / "monitor_gpu.sh"), str(child.pid), str(run / "gpu.csv")], stdout=monitor_log, stderr=subprocess.STDOUT)
            write_json(run / "manifest.json", manifest)
            status = child.wait()
    except BaseException:
        manifest["controller_error"] = traceback.format_exc()
        status = 1
    finally:
        # A controller interruption must not leave its device worker behind.
        if child is not None and child.poll() is None:
            try:
                child.terminate()
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=10)
            except BaseException:
                manifest["worker_shutdown_error"] = traceback.format_exc()
                status = 1
        if monitor is not None and monitor.poll() is None:
            try:
                monitor.terminate()
                monitor.wait(timeout=10)
            except BaseException:
                manifest["monitor_shutdown_error"] = traceback.format_exc()
                status = 1
        if monitor_log is not None:
            monitor_log.close()
        if child is not None and child.poll() is not None:
            try:
                # The worker has exited: its CUDA context is gone before this sample.
                post = validator.preflight(args.ixsmi)
                gpu = subprocess.check_output([args.ixsmi, "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader"], text=True, timeout=10).strip()
                write_json(run / "postflight.json", {**post, "gpu": gpu, "port_9031_open": False})
            except BaseException:
                manifest["postflight_error"] = traceback.format_exc()
                status = 1
        manifest.update(finished_utc=utc(), exit_code=status)
        write_json(run / "manifest.json", manifest)
        (run / "exit-code").write_text(str(status) + "\n", encoding="utf-8")
        (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n", encoding="utf-8")
        if lock is not None:
            lock.close()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
