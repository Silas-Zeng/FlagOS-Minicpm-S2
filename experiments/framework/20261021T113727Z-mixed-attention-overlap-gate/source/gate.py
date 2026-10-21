#!/usr/bin/env python3
"""One actual mixed Attention shape, serial versus two streams; no weights/service.

No external events or profiler. Bitwise/KV/join correctness comes first; regular
GPU events and whole-call wall samples are diagnostic, never official scores.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shlex
import signal
import statistics
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace as NS

from validate_hidden_row_gather import digest, load, utc, write


EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"
EXPECTED_C3 = "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42"
EXPECTED_WRITER = "f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb"
EXPECTED_OVERLAP = "93c3124ccab9311cb98f319d9f786f7aae571f9c1d976d1a9f1d623adca378db"


def timed_batch(torch, callback, loops):
    torch.cuda.synchronize()
    begin = time.perf_counter_ns()
    event_error, start, end = None, None, None
    try:
        start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        start.record()
    except RuntimeError as exc:
        event_error = "timing event start: " + repr(exc)
    for _ in range(loops):
        callback()
    if event_error is None:
        try:
            end.record()
        except RuntimeError as exc:
            event_error = "timing event end: " + repr(exc)
    torch.cuda.synchronize()
    wall_ms = (time.perf_counter_ns() - begin) / 1e6
    event_ms = None
    if event_error is None:
        try:
            event_ms = start.elapsed_time(end)
            if not math.isfinite(event_ms) or event_ms <= 0:
                event_error, event_ms = "timing event non-positive/non-finite", None
        except RuntimeError as exc:
            event_error = "timing event elapsed: " + repr(exc)
    return {"calls": loops, "wall_total_ms": wall_ms, "wall_per_call_ms": wall_ms / loops,
            "event_total_ms": event_ms, "event_per_call_ms": event_ms / loops if event_ms is not None else None,
            "event_error": event_error}


def worker(run, model):
    result = {"status": "started", "accuracy": "not evaluated", "official_performance": "not evaluated",
              "shape": {"decode": 29, "prefill": 2019, "kv_len": 16384},
              "limitations": ["One actual-backend synthetic layer, no weights or model runner.",
                              "A second stream does not itself prove hardware concurrency.",
                              "Strong-reference pending frames need a full-model memory design before serving integration."]}
    torch, overlap = None, None
    try:
        import importlib
        import torch
        import validate_mixed_decode as previous
        from vllm.config import CompilationConfig, CUDAGraphMode
        from vllm.engine.arg_utils import EngineArgs
        from vllm.v1.kv_cache_interface import FullAttentionSpec

        config = EngineArgs(model=str(model), served_model_name=["minicpm"], gpu_memory_utilization=0.85,
                            max_model_len=131072, compilation_config=CompilationConfig(
                                cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
        # Platform configuration can refresh these bindings; resolve afterwards.
        backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
        attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
        helpers = importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
        writer = importlib.import_module("vllm.v1.attention.ops.triton_reshape_and_cache_flash")
        if (digest(Path(writer.__file__)) != EXPECTED_WRITER
                or backend.triton_reshape_and_cache_flash is not writer.triton_reshape_and_cache_flash):
            raise RuntimeError("unaudited actual KV writer source/binding")
        c2 = load("overlap_gate_c2", run / "source/runtime.py")
        c3 = load("overlap_gate_c3", run / "source/mixed.py")
        policy = load("overlap_gate_policy", run / "source/overlap.py")
        result["c2_install"], result["c3_install"] = c2.install(), c3.install()
        for name, module in (("backend.py", backend), ("attention.py", attention),
                             ("helpers.py", helpers), ("writer.py", writer)):
            (run / "source" / name).write_bytes(Path(module.__file__).read_bytes())
        (run / "source/model-config.json").write_bytes((model / "config.json").read_bytes())
        if torch.cuda.device_count() != 1:
            raise RuntimeError("expected exactly one visible accelerator")
        torch.cuda.set_device(0)
        torch.manual_seed(721501)
        result["device"] = str(torch.cuda.get_device_properties(0))
        spec = FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=128, dtype=torch.bfloat16)
        builder = backend.TritonAttentionMetadataBuilder(spec, ["synthetic.attn"], config, torch.device("cuda:0"))
        impl = backend.TritonAttentionImpl(num_heads=16, head_size=128, scale=128 ** -0.5, num_kv_heads=2,
                                         alibi_slopes=None, sliding_window=None, kv_cache_dtype="auto",
                                         attn_type=backend.AttentionType.DECODER)
        layer = NS(_q_scale=torch.ones((), device="cuda"), _k_scale=torch.ones((), device="cuda"),
                   _v_scale=torch.ones((), device="cuda"))
        common, q, k, v, cache = previous.make_data(torch, [1] * 29 + [2019], 16384)
        metadata = builder.build(0, common)
        if getattr(metadata, c3._PLAN, None) is None:
            raise RuntimeError("actual metadata did not select the audited natural-prefix split")
        overlap = policy.MixedAttentionOverlap(backend, c3, torch, torch.device("cuda:0"))
        # Actual cache writes occur on main before the prototype records its ready event.
        impl.do_kv_cache_update(layer, k[:2048], v[:2048], cache, common.slot_mapping)
        original_cache = cache.clone()
        first, second = q.clone(), -q
        golden, consumed = [], []
        cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
        for query in (first, second):
            serial_out = torch.full_like(query, -17)
            candidate_out = torch.full_like(query, -17)
            overlap.serial(impl, layer, query, k, v, cache, metadata, serial_out)
            overlap.forward(impl, layer, query, k, v, cache, metadata, candidate_out)
            # The original stream consumes output immediately after join. No host
            # sync between these two different-Q calls; scratch is reused.
            golden.append(serial_out.clone())
            consumed.append(candidate_out.clone())
        torch.cuda.synchronize()
        correctness = {"all_output_bits_equal": all(torch.equal(a.view(torch.int16), b.view(torch.int16))
                                                   for a, b in zip(golden, consumed)),
                       "valid_output_finite": all(bool(torch.isfinite(x[:2048]).all()) for x in consumed),
                       "padding_untouched": all(bool((x[2048:] == -17).all()) for x in consumed),
                       "entire_kv_bits_unchanged": torch.equal(original_cache.view(torch.int16), cache.view(torch.int16)),
                       "rng_unchanged": torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state()),
                       "selected_both_calls": overlap.selected_calls == 2}
        result["correctness"] = correctness
        if not all(correctness.values()):
            raise AssertionError("stream split correctness/join failure: " + repr(correctness))
        overlap.collect_completed()
        # One no-plan fallback uses the original dummy/no-attention behavior.
        dummy = torch.full_like(q, -19)
        before = overlap.selected_calls
        overlap.forward(impl, layer, q, k, v, cache, None, dummy)
        torch.cuda.synchronize()
        result["no_plan_fallback"] = overlap.selected_calls == before and overlap.fallback_calls == 1
        if not result["no_plan_fallback"]:
            raise AssertionError("no-plan forward bypassed serial fallback")

        serial_out, overlap_out = torch.empty_like(q), torch.empty_like(q)
        serial_fn = lambda: overlap.serial(impl, layer, q, k, v, cache, metadata, serial_out)
        overlap_fn = lambda: overlap.forward(impl, layer, q, k, v, cache, metadata, overlap_out)
        for callback in (serial_fn, overlap_fn):
            callback(); callback()
            torch.cuda.synchronize()
            overlap.collect_completed()
        result["timings"] = []
        for name in ("serial", "overlap", "overlap", "serial"):
            row = timed_batch(torch, serial_fn if name == "serial" else overlap_fn, 4)
            row["policy"] = name
            result["timings"].append(row)
            overlap.collect_completed()
        serial_wall = statistics.median(x["wall_per_call_ms"] for x in result["timings"] if x["policy"] == "serial")
        overlap_wall = statistics.median(x["wall_per_call_ms"] for x in result["timings"] if x["policy"] == "overlap")
        result["summary"] = {"serial_wall_median_ms": serial_wall, "overlap_wall_median_ms": overlap_wall,
                             "wall_fraction_saved": 1 - overlap_wall / serial_wall,
                             "event_timing_available": all(x["event_error"] is None for x in result["timings"]),
                             "scope": "one warm layer, complete submit/wait/record path; no hardware-concurrency or E2E claim"}
        result["status"] = "correctness_passed_single_layer_signal_only"
    except BaseException:
        result["status"], result["error"] = "failed", traceback.format_exc()
        traceback.print_exc()
    finally:
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
                if overlap is not None:
                    overlap.collect_completed()
                    result["pending_after_sync"] = len(overlap.pending)
                    result["peak_pending_frames"] = overlap.peak_pending
                    if overlap.pending:
                        raise RuntimeError("side completion events remain pending after device synchronization")
            except BaseException:
                result["status"], result["shutdown_error"] = "failed", traceback.format_exc()
        result["source_sha256"] = {p.name: digest(p) for p in (run / "source").iterdir() if p.is_file()}
        write(run / "results.json", result)
    return 0 if result["status"] == "correctness_passed_single_layer_signal_only" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--runtime-path", type=Path)
    parser.add_argument("--mixed-path", type=Path)
    parser.add_argument("--overlap-path", type=Path)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir, args.model)
    if any(path is None for path in (args.runtime_path, args.mixed_path, args.overlap_path)):
        parser.error("controller requires C2, C3 and overlap candidate paths")
    import fcntl
    import validate_block_table_candidate as owner
    import validate_hidden_row_gather as utilities
    import validate_mixed_decode as previous
    import bench_attention_dispatch as shared

    root, run = owner.ROOT.resolve(), args.run_dir.resolve()
    if not run.is_relative_to(root) or run == root:
        raise ValueError("run must be a new child of experiment root")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {"started_utc": utc(), "pid": os.getpid(), "command": [sys.executable, *sys.argv],
                "command_shell": shlex.join([sys.executable, *sys.argv]),
                "kind": "one-layer actual mixed stream correctness/timing, no weights/service/score",
                "environment": {name: os.environ[name] for name in (
                    "VLLM_PLUGINS", "PYTHONPATH", "CUDA_VISIBLE_DEVICES", "IX_VISIBLE_DEVICES",
                    "COREX_VISIBLE_DEVICES", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "TRITON_CACHE_DIR") if name in os.environ}}
    lock, child, monitor, monitor_log, status = None, None, None, None, 1
    def interrupted(signum, frame):
        raise SystemExit(f"controller interrupted by signal {signum}")
    signal.signal(signal.SIGTERM, interrupted)
    try:
        lock = (root / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest["preflight"] = owner.preflight(args.ixsmi)
        gpu = subprocess.check_output([args.ixsmi], text=True, timeout=10)
        (run / "preflight-ixsmi.txt").write_text(gpu, encoding="utf-8")
        if "No running processes found" not in gpu:
            raise RuntimeError("accelerator process already active")
        source = run / "source"
        source.mkdir()
        for name, path in (("gate.py", Path(__file__)), ("runtime.py", args.runtime_path),
                           ("mixed.py", args.mixed_path), ("overlap.py", args.overlap_path),
                           ("validate_hidden_row_gather.py", Path(utilities.__file__)),
                           ("validate_mixed_decode.py", Path(previous.__file__)),
                           ("bench_attention_dispatch.py", Path(shared.__file__)),
                           ("validate_block_table_candidate.py", Path(owner.__file__)),
                           ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh")):
            (source / name).write_bytes(path.read_bytes())
        for name, expected in (("runtime.py", EXPECTED_C2), ("mixed.py", EXPECTED_C3), ("overlap.py", EXPECTED_OVERLAP)):
            if expected is None or digest(source / name) != expected:
                raise RuntimeError("unaudited overlap gate asset: " + name)
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["packages"] = {}
        for package in ("torch", "vllm", "FlagGems", "SQLAlchemy"):
            try:
                manifest["packages"][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][package] = "unavailable"
        manifest["worker_command"] = [sys.executable, str(source / "gate.py"), "--worker", "--run-dir", str(run), "--model", str(args.model)]
        write(run / "manifest.json", manifest)
        with (run / "worker.log").open("x") as log:
            child = subprocess.Popen(manifest["worker_command"], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            manifest["worker_pid"] = child.pid
            monitor_log = (run / "monitor.log").open("x")
            monitor = subprocess.Popen(["bash", str(source / "monitor_gpu.sh"), str(child.pid), str(run / "gpu.csv")],
                                       stdout=monitor_log, stderr=subprocess.STDOUT, start_new_session=True)
            write(run / "manifest.json", manifest)
            status = child.wait(timeout=300)
    except BaseException:
        manifest["controller_error"] = traceback.format_exc()
        traceback.print_exc()
    finally:
        for process in (child, monitor):
            if process is not None and process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=10)
                except ProcessLookupError:
                    process.wait(timeout=10)
                except BaseException:
                    manifest["cleanup_error"], status = traceback.format_exc(), 1
        if monitor_log is not None:
            monitor_log.close()
        if child is not None and child.poll() is not None:
            try:
                manifest["postflight"] = owner.preflight(args.ixsmi)
                gpu = subprocess.check_output([args.ixsmi], text=True, timeout=10)
                (run / "postflight-ixsmi.txt").write_text(gpu, encoding="utf-8")
                if "No running processes found" not in gpu:
                    raise RuntimeError("accelerator process remains after owned worker exit")
            except BaseException:
                manifest["postflight_error"], status = traceback.format_exc(), 1
        manifest.update(finished_utc=utc(), exit_code=status)
        write(run / "manifest.json", manifest)
        (run / "exit-code").write_text(str(status) + "\n", encoding="utf-8")
        (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n", encoding="utf-8")
        if lock is not None:
            lock.close()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
