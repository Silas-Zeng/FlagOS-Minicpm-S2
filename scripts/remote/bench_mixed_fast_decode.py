#!/usr/bin/env python3
"""Optimistic mixed-attention split screen with measured w2s1 decode.

One layer only. Metadata normalization is prepared once outside timing.
Finite decode and bitwise prefill gates do not establish model accuracy.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import shlex
import statistics
import subprocess
import sys
import traceback


SHAPES = ((63, 1985, 4096), (63, 127, 4096), (29, 2019, 16384), (29, 127, 16384))


def json_safe(value):
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_safe(item) for item in value]
    return str(value) if isinstance(value, float) and not math.isfinite(value) else value


def write_json(path, value):
    path.write_text(json.dumps(json_safe(value), ensure_ascii=True, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_metadata(data, decode_requests, prefill_tokens):
    """Views plus one cu-query normalization; call once before measurement."""
    d = decode_requests
    decode, prefill = data.copy(), data.copy()
    decode.update(q=data["q"][:d], cu_seqlens_q=data["cu_seqlens_q"][:d + 1],
                  seqused_k=data["seqused_k"][:d], block_table=data["block_table"][:d],
                  max_seqlen_q=1)
    prefill.update(q=data["q"][d:], cu_seqlens_q=data["cu_seqlens_q"][d:] - d,
                   seqused_k=data["seqused_k"][d:], block_table=data["block_table"][d:],
                   max_seqlen_q=prefill_tokens)
    return decode, prefill


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--transform-path", type=Path, required=True)
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args()
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
        "python": sys.version, "platform": platform.platform(), "seed": args.seed,
        "kind": "single-layer optimistic mixed split; not accuracy, E2E or official score",
        "control": "whole retained attention, original 2D prefill policy for the mixed batch",
        "candidate": "decode prefix via isolated w2s1 source; prefill suffix via retained original function",
        "timing": "eager CUDA events, 2 warmups and 5 samples per path; metadata normalization excluded",
        "lock_path": str(root / "framework-device.lock"),
        "shapes": [{"decode_requests": d, "prefill_tokens": p, "kv_len": k} for d, p, k in SHAPES],
        "environment": {key: os.environ[key] for key in (
            "CUDA_VISIBLE_DEVICES", "IX_VISIBLE_DEVICES", "VLLM_PLUGINS", "PYTHONPATH",
            "OMP_NUM_THREADS", "MKL_NUM_THREADS", "TRITON_CACHE_DIR", "USE_FLAGTUNE",
        ) if key in os.environ},
    }
    result = {
        "status": "started", "accuracy": "not evaluated", "cases": [],
        "limitations": [
            "Metadata views and one cu-query normalization are prepared once outside timing: optimistic upper bound.",
            "Only attention is split; no model, GEMM, scheduler, KV-write or sampling cost is measured.",
            "Decoder output may differ; finite decode plus exact prefill is not an accuracy gate.",
            "CUDA event intervals can include eager host submission gaps; raw samples are retained.",
        ],
    }
    lock, monitor, torch = None, None, None
    status = 1

    def checkpoint():
        write_json(run / "manifest.json", manifest)
        write_json(run / "results.json", result)

    checkpoint()
    write_json(run / "command.json", manifest["command"])
    try:
        lock = (root / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest["preflight"] = validator.preflight(args.ixsmi)
        manifest["lock_acquired_utc"] = validator.utc()
        source = run / "source"
        source.mkdir()
        for label, path in (
            ("benchmark.py", Path(__file__)), ("transform.py", args.transform_path),
            ("bench_attention_dispatch.py", Path(shared.__file__)),
            ("validate_block_table_candidate.py", Path(validator.__file__)),
            ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh"),
        ):
            (source / label).write_bytes(path.read_bytes())
        transform = shared.load("mixed_fast_launch_transform", source / "transform.py")
        import torch
        import vllm.v1.attention.ops.triton_unified_attention as installed
        import vllm.v1.attention.ops.triton_attention_helpers as helpers
        attention_bytes = Path(installed.__file__).read_bytes()
        helper_bytes = Path(helpers.__file__).read_bytes()
        (source / "retained.py").write_bytes(attention_bytes)
        (source / "helpers.py").write_bytes(helper_bytes)
        (source / "decode_w2s1.py").write_bytes(transform.transform_source(attention_bytes, helper_bytes, 2, 1))
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["installed_sources"] = {"attention": str(installed.__file__), "helpers": str(helpers.__file__)}
        manifest["packages"] = {}
        for name in ("torch", "vllm", "vllm-plugin-fl", "triton", "flag-gems", "flagtree"):
            try:
                manifest["packages"][name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][name] = "distribution name unavailable"
        if torch.cuda.device_count() != 1 or torch.get_default_dtype() != torch.float32:
            raise RuntimeError("expected one accelerator and standard float32 scratch default")
        torch.cuda.set_device(0)
        torch.manual_seed(args.seed)
        manifest["device"] = str(torch.cuda.get_device_properties(0))
        retained = shared.load("mixed_fast_retained", source / "retained.py")
        fast_decode = shared.load("mixed_fast_decode_w2s1", source / "decode_w2s1.py")
        monitor = subprocess.Popen(["bash", str(source / "monitor_gpu.sh"), str(os.getpid()), str(run / "gpu.csv")],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        manifest["monitor_pid"] = monitor.pid
        checkpoint()
        for index, (d, p, kv_len) in enumerate(SHAPES):
            row = {"decode_requests": d, "prefill_tokens": p, "kv_len": kv_len,
                   "accuracy": "not evaluated", "metadata_normalization": "outside timing"}
            try:
                data = shared.inputs(torch, [1] * d + [p], kv_len)
                control, changed = torch.empty_like(data["q"]), torch.empty_like(data["q"])
                decode, prefill = split_metadata(data, d, p)

                def whole():
                    shared.invoke(retained, data, control)

                def split():
                    shared.invoke(fast_decode, decode, changed[:d])
                    shared.invoke(retained, prefill, changed[d:])

                whole()
                split()
                torch.cuda.synchronize()
                row["decode_output"] = shared.compare(torch, control[:d], changed[:d], d)
                row["prefill_output"] = shared.compare(torch, control[d:], changed[d:], p)
                gate = row["decode_output"]["finite"] and row["prefill_output"]["finite"] and row["prefill_output"]["bitwise_equal"]
                row["gate_passed"] = gate
                if gate:
                    # Alternate path order across shapes, keeping the exact five
                    # raw eager-event samples from the existing timing helper.
                    order = ("whole", "split") if index % 2 == 0 else ("split", "whole")
                    row["timing_order"] = order
                    for label in order:
                        values = shared.times(torch, whole if label == "whole" else split, False, repeats=5)
                        row[label + "_ms"] = values
                        row[label + "_median_ms"] = statistics.median(values)
                    row["post_timing_decode_output"] = shared.compare(torch, control[:d], changed[:d], d)
                    row["post_timing_prefill_output"] = shared.compare(torch, control[d:], changed[d:], p)
                    post_gate = row["post_timing_decode_output"]["finite"] and row["post_timing_prefill_output"]["finite"] and row["post_timing_prefill_output"]["bitwise_equal"]
                    row["status"] = "finite_decode_exact_prefill" if post_gate else "reject_post_timing"
                else:
                    row.update(status="reject_finite_or_prefill_gate", timing="not run")
            except Exception:
                row.update(status="reject_runtime_error", error=traceback.format_exc())
            result["cases"].append(row)
            checkpoint()
            print(json.dumps(json_safe(row), ensure_ascii=True, allow_nan=False), flush=True)
        passed = len(result["cases"]) == 4 and all(row["status"] == "finite_decode_exact_prefill" for row in result["cases"])
        result.update(status="completed_finite_decode_exact_prefill" if passed else "completed_with_rejections",
                      all_finite_prefill_gates_passed=passed, accuracy="not evaluated")
        status = 0 if passed else 2
    except BaseException:
        result.update(status="failed", error=traceback.format_exc())
        print(result["error"], flush=True)
    finally:
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
            except BaseException:
                result.update(shutdown_error=traceback.format_exc(), status="failed")
                status = 1
        if monitor is not None:
            try:
                monitor.terminate()
                monitor.wait(timeout=10)
            except BaseException:
                result.update(monitor_shutdown_error=traceback.format_exc(), status="failed")
                status = 1
        manifest.update(finished_utc=validator.utc(), exit_code=status)
        result["finished_utc"] = manifest["finished_utc"]
        checkpoint()
        (run / "exit-code").write_text(str(status) + "\n", encoding="utf-8")
        (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n", encoding="utf-8")
        if lock is not None:
            lock.close()
    print(json.dumps({"status": result["status"], "accuracy": "not evaluated", "run_dir": str(run), "exit_code": status}), flush=True)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
