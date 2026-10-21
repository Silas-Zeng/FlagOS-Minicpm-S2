#!/usr/bin/env python3
"""Isolated decode launch screen: exact output gates before graph microtiming.

Requires sibling bench_attention_dispatch.py and validate_block_table_candidate.py.
Only a device owner may run this on the accelerator, after independent review.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from datetime import datetime, timezone
import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shlex
import statistics
import subprocess
import sys
import traceback


VARIANTS = (("w4s3", 4, 3), ("w4s1", 4, 1), ("w2s3", 2, 3), ("w2s1", 2, 1))
CASES = (
    ("dense-4k", [1] * 64, 4096, False),
    ("dense-16k", [1] * 30, 16384, False),
    ("padded-tail", [1] * 13 + [0] * 3, 4096, True),
    ("zero-middle", [1, 0, 1, 1, 0, 1, 1, 1], 127, True),
    ("prefill-fallback", [16, 13], 256, False),
)
ENV_KEYS = (
    "CUDA_VISIBLE_DEVICES", "IX_VISIBLE_DEVICES", "VLLM_PLUGINS", "PYTHONPATH",
    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "TRITON_CACHE_DIR", "USE_FLAGTUNE",
    "VLLM_FL_USE_FLAGGEMS_ATTN", "VLLM_FL_ILUVATAR_KEEP_SAMPLER_COMPILE",
)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def backend_defaults():
    """Best-effort installed backend options; do not infer from variant labels."""
    try:
        import triton
        from triton.compiler.compiler import make_backend
        target = triton.runtime.driver.active.get_current_target()
        options = make_backend(target).parse_options({})
        return {"status": "available", "target": str(target),
                "options": {name: getattr(options, name, None) for name in
                            ("num_warps", "num_stages", "warp_size", "maxnreg")},
                "basis": "installed backend parse_options({}); compiled kernel metadata separately recorded"}
    except Exception:
        return {"status": "unavailable", "error": traceback.format_exc()}


def compiled_metadata(module):
    """Read already populated caches only; never compile or launch to inspect."""
    found, visited = [], set()

    def walk(value, depth=0):
        if depth > 7 or len(found) >= 64 or id(value) in visited:
            return
        visited.add(id(value))
        if isinstance(value, Mapping):
            for child in value.values():
                walk(child, depth + 1)
        elif isinstance(value, (tuple, list)):
            for child in value:
                walk(child, depth + 1)
        else:
            attrs = getattr(value, "__dict__", {})
            metadata = attrs.get("metadata")
            if metadata is None:
                return
            record = {}
            for name in ("name", "num_warps", "num_stages", "warp_size", "shared", "maxnreg"):
                item = metadata.get(name) if isinstance(metadata, Mapping) else getattr(metadata, name, None)
                if item is not None:
                    record[name] = item if isinstance(item, (str, int, float, bool)) else str(item)
            for name in ("n_regs", "n_spills"):
                if name in attrs:
                    record[name] = attrs[name]
            if record:
                found.append(record)

    kernel = module.kernel_unified_attention
    attrs = getattr(kernel, "__dict__", {})
    for key in ("device_caches", "cache"):
        if key in attrs:
            walk(attrs[key])
    return {"status": "available" if found else "unavailable",
            "records": found, "limit": 64,
            "basis": "best-effort already populated JIT caches; no one-to-one case mapping asserted"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--transform-path", required=True, type=Path)
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    # Keep module import and --help CPU-only, including on Windows. These
    # sibling utilities import fcntl, but neither imports torch at module scope.
    import fcntl
    import bench_attention_dispatch as shared
    import validate_block_table_candidate as validator

    root, run = validator.ROOT.resolve(), args.run_dir.resolve()
    if not run.is_relative_to(root) or run == root:
        raise ValueError("run directory must be new and inside experiment workspace")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {
        "run_id_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
        "started_utc": validator.utc(), "pid": os.getpid(), "run_dir": str(run),
        "command": [sys.executable, *sys.argv], "command_shell": shlex.join([sys.executable, *sys.argv]),
        "kind": "single-layer launch diagnostic; not model accuracy, E2E performance or official score",
        "python": sys.version, "platform": platform.platform(),
        "environment": {name: os.environ[name] for name in ENV_KEYS if name in os.environ},
        "seed": args.seed, "repeats": args.repeats,
        "control_identity": "C0 is isolated retained original bytes with implicit backend defaults",
        "explicit_control_identity": "w4s3 is an explicit variant, not assumed equivalent to C0",
        "lock_path": str(root / "framework-device.lock"),
        "cases": [{"case": label, "query_lengths": lengths, "kv_len": kv_len,
                   "padded_input_storage": padded} for label, lengths, kv_len, padded in CASES],
    }
    result = {"status": "started", "baseline_cases": [], "variants": {}, "timings": [],
              "limitations": ["Only valid packed query tokens have defined comparison outputs.",
                              "All five case gates precede timing for each variant.",
                              "Changing warp/stage can change generated arithmetic; bitwise equality is measured, not assumed.",
                              "Graph timings are single-layer diagnostics and do not establish a model speedup."]}
    lock, monitor, torch = None, None, None
    status, datasets, modules = 1, {}, {}

    def checkpoint():
        write_json(run / "manifest.json", manifest)
        write_json(run / "results.json", result)

    checkpoint()
    write_json(run / "command.json", manifest["command"])
    try:
        if not __debug__:
            raise RuntimeError("validation requires Python assertions; do not use -O")
        lock = (root / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest["lock_acquired_utc"] = validator.utc()
        manifest["preflight"] = validator.preflight(args.ixsmi)
        source = run / "source"
        source.mkdir()
        archive = (
            ("benchmark.py", Path(__file__)), ("bench_attention_dispatch.py", Path(shared.__file__)),
            ("validate_block_table_candidate.py", Path(validator.__file__)),
            ("transform.py", args.transform_path), ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh"),
        )
        for label, path in archive:
            (source / label).write_bytes(path.read_bytes())
        transform = shared.load("biv150_launch_transform", source / "transform.py")
        # Device-capable imports occur only after exclusive ownership/preflight.
        import torch
        import vllm.v1.attention.ops.triton_unified_attention as installed
        import vllm.v1.attention.ops.triton_attention_helpers as helpers
        attention_bytes = Path(installed.__file__).read_bytes()
        helper_bytes = Path(helpers.__file__).read_bytes()
        (source / "retained_original.py").write_bytes(attention_bytes)
        (source / "helpers.py").write_bytes(helper_bytes)
        for label, warps, stages in VARIANTS:
            path = source / (label + ".py")
            path.write_bytes(transform.transform_source(attention_bytes, helper_bytes, warps, stages))
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["installed_sources"] = {"attention": str(installed.__file__), "helpers": str(helpers.__file__)}
        manifest["packages"] = {}
        for name in ("torch", "vllm", "vllm-plugin-fl", "triton", "flag-gems", "flagtree"):
            try:
                manifest["packages"][name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][name] = "distribution name unavailable"
        if torch.cuda.device_count() != 1:
            raise RuntimeError("expected exactly one visible accelerator")
        if torch.get_default_dtype() != torch.float32:
            raise RuntimeError("shared input helper scratch requires the standard float32 default")
        torch.cuda.set_device(0)
        torch.manual_seed(args.seed)
        manifest["device"] = str(torch.cuda.get_device_properties(0))
        manifest["backend_defaults"] = backend_defaults()
        modules["C0"] = shared.load("biv150_launch_retained", source / "retained_original.py")
        for label, _, _ in VARIANTS:
            modules[label] = shared.load("biv150_launch_" + label, source / (label + ".py"))
        monitor = subprocess.Popen(["bash", str(source / "monitor_gpu.sh"), str(os.getpid()), str(run / "gpu.csv")],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        manifest["monitor_pid"] = monitor.pid
        checkpoint()
        # Reference-repeat control detects instability without silently blaming
        # a launch variant. Save all five cases before any timing is attempted.
        for case, lengths, kv_len, padded in CASES:
            data = shared.inputs(torch, lengths, kv_len, padded)
            reference, repeated = torch.empty_like(data["q"]), torch.empty_like(data["q"])
            shared.invoke(modules["C0"], data, reference)
            shared.invoke(modules["C0"], data, repeated)
            torch.cuda.synchronize()
            check = shared.compare(torch, reference, repeated, sum(lengths))
            row = {"case": case, "reference": "C0 retained original repeat", **check}
            row["status"] = "pass" if check["finite"] and check["bitwise_equal"] else "inconclusive_reference"
            result["baseline_cases"].append(row)
            datasets[case] = (data, reference, sum(lengths))
            checkpoint()
        baseline_ok = all(row["status"] == "pass" for row in result["baseline_cases"])
        manifest["retained_compiled_metadata"] = compiled_metadata(modules["C0"])
        for label, warps, stages in VARIANTS:
            entry = {"num_warps": warps, "num_stages": stages, "gate_cases": [], "all_five_gates_passed": False}
            result["variants"][label] = entry
            for case, _, _, _ in CASES:
                row = {"variant": label, "case": case, "reference": "C0 retained original"}
                if not baseline_ok:
                    row.update(status="inconclusive_reference", timing="not run")
                else:
                    try:
                        data, reference, count = datasets[case]
                        changed = torch.empty_like(data["q"])
                        shared.invoke(modules[label], data, changed)
                        torch.cuda.synchronize()
                        check = shared.compare(torch, reference, changed, count)
                        row.update(check)
                        row["status"] = "pass" if check["finite"] and check["bitwise_equal"] else "reject_numerical"
                    except Exception:
                        row.update(status="reject_runtime_error", error=traceback.format_exc())
                entry["gate_cases"].append(row)
                checkpoint()
                print(json.dumps(row), flush=True)
            entry["all_five_gates_passed"] = all(row["status"] == "pass" for row in entry["gate_cases"])
            entry["compiled_metadata"] = compiled_metadata(modules[label])
            entry["status"] = "gates_passed" if entry["all_five_gates_passed"] else "reject_or_inconclusive"
            checkpoint()
        # No timing for a variant that failed any of the five cases. C0 remains
        # the primary timing reference; explicit w4s3 is separately reported.
        if baseline_ok:
            eligible = [label for label, _, _ in VARIANTS if result["variants"][label]["all_five_gates_passed"]]
            for index, case in enumerate(("dense-4k", "dense-16k")):
                order = ["C0", *eligible] if index == 0 else [*reversed(eligible), "C0"]
                data, reference, count = datasets[case]
                for label in order:
                    row = {"variant": label, "case": case, "mode": "CUDA graph replay", "case_order": order}
                    try:
                        changed = torch.empty_like(data["q"])
                        values = shared.times(torch, lambda: shared.invoke(modules[label], data, changed), True,
                                              repeats=args.repeats)
                        post = shared.compare(torch, reference, changed, count)
                        row.update(times_ms=values, median_ms=statistics.median(values), post_graph_check=post)
                        row["status"] = "pass" if post["finite"] and post["bitwise_equal"] else "reject_post_graph"
                    except Exception:
                        row.update(status="reject_timing_runtime_error", error=traceback.format_exc())
                    result["timings"].append(row)
                    checkpoint()
                    print(json.dumps(row), flush=True)
        all_gates = baseline_ok and all(entry["all_five_gates_passed"] for entry in result["variants"].values())
        all_timing = len(result["timings"]) == 10 and all(row["status"] == "pass" for row in result["timings"])
        result.update(all_variants_passed=all_gates and all_timing,
                      status="pass" if all_gates and all_timing else "completed_with_rejections_or_inconclusive")
        status = 0 if result["all_variants_passed"] else 2
    except BaseException:
        result.update(status="failed", error=traceback.format_exc(), all_variants_passed=False)
        print(result["error"], flush=True)
    finally:
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
            except BaseException:
                result.update(shutdown_error=traceback.format_exc(), status="failed", all_variants_passed=False)
                status = 1
        if monitor is not None:
            try:
                monitor.terminate()
                monitor.wait(timeout=10)
            except BaseException:
                result.update(monitor_shutdown_error=traceback.format_exc(), status="failed", all_variants_passed=False)
                status = 1
        datasets.clear()
        gc.collect()
        manifest.update(finished_utc=validator.utc(), exit_code=status)
        result["finished_utc"] = manifest["finished_utc"]
        checkpoint()
        (run / "exit-code").write_text(str(status) + "\n", encoding="utf-8")
        (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n", encoding="utf-8")
        if lock is not None:
            lock.close()
    print(json.dumps({"status": result["status"], "all_variants_passed": result.get("all_variants_passed", False),
                      "run_dir": str(run), "exit_code": status}), flush=True)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
