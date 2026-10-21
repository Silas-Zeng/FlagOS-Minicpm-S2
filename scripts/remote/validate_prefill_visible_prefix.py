#!/usr/bin/env python3
"""Two actual-backend BF16 prefill correctness cases; one warm timing ABBA.

No weights, serving, profiler, graph capture, sweep or official score. The
controller imports no accelerator runtime; only its owned child uses CUDA.
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
EXPECTED_POLICY = "87c6a31075939c551402d7007b491546a215584a58ec82caddc08fc7249998d6"
TIMING_METHOD = "one P2019 ABBA; pre-recorded Event pairs; record/submit/final sync inside wall; 32 calls/window"


def timed_batch(torch, callback, pair, loops):
    torch.cuda.synchronize()
    start, end = pair
    begin = time.perf_counter_ns()
    start.record()
    for _ in range(loops):
        callback()
    end.record()
    torch.cuda.synchronize()
    wall = (time.perf_counter_ns() - begin) / 1e6
    event = start.elapsed_time(end)
    if not math.isfinite(event) or event <= 0:
        raise RuntimeError("invalid timing Event elapsed time")
    return {"calls": loops, "wall_total_ms": wall, "wall_per_call_ms": wall / loops,
            "event_total_ms": event, "event_per_call_ms": event / loops}


def prepare_pages(torch, common, key, value, kv_len):
    """Noncontiguous physical pages and real reused cached-prefix blocks.

    Input setup may copy page numbers to CPU; the runtime candidate never
    reads metadata values on the host. New-token slots follow the same map.
    """
    rows, blocks = common.block_table_tensor.shape
    table = torch.randperm(rows * blocks, device="cuda", dtype=torch.int64).to(torch.int32).reshape(rows, blocks)
    if rows > 1:
        # Only old KV is shared: all new tokens start beyond position 256.
        table[-1, :16] = table[0, :16]
    common.block_table_tensor = table
    pages = table.cpu().tolist()
    lengths = (common.query_start_loc_cpu[1:] - common.query_start_loc_cpu[:-1]).tolist()
    slots = []
    for row, length in enumerate(lengths):
        for position in range(kv_len - length, kv_len):
            slots.append(pages[row][position // 16] * 16 + position % 16)
    total = common.num_actual_tokens
    common.slot_mapping = torch.tensor(slots + [-1] * 3, dtype=torch.int64, device="cuda")
    key[total:] = float("nan")
    value[total:] = float("nan")


def worker(run, model):
    result = {"status": "started", "accuracy": "not evaluated", "official_performance": "not evaluated",
              "timing_loops": 32, "timing_method": TIMING_METHOD,
              "worker_command": [sys.executable, *sys.argv],
              "worker_command_shell": shlex.join([sys.executable, *sys.argv]),
              "limitations": ["Actual backend/builder/KV writer, synthetic inputs, no weights or model runner.",
                              "Only P2019/KV16K is timed; Q2048/KV16K is correctness only.",
                              "No accuracy, graph-replay, serving or official-performance conclusion."]}
    torch, attention, original = None, None, None
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
        text = config.model_config.hf_text_config
        if (Path(str(config.model_config.model).rstrip("/\\")).name != "MiniCPM5-2B"
                or config.model_config.dtype != torch.bfloat16
                or (text.hidden_size, text.num_hidden_layers, text.num_attention_heads,
                    text.num_key_value_heads) != (2048, 42, 16, 2)):
            raise RuntimeError("gate requires the actual MiniCPM5-2B BF16 configuration")
        backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
        attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
        helpers = importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
        writer = importlib.import_module("vllm.v1.attention.ops.triton_reshape_and_cache_flash")
        if (digest(Path(writer.__file__)) != EXPECTED_WRITER
                or backend.triton_reshape_and_cache_flash is not writer.triton_reshape_and_cache_flash):
            raise RuntimeError("unaudited actual KV writer source/binding")
        c2 = load("visible_gate_c2", run / "source/runtime.py")
        c3 = load("visible_gate_c3", run / "source/mixed.py")
        policy = load("visible_gate_policy", run / "source/policy.py")
        result["c2_install"], result["c3_install"] = c2.install(), c3.install()
        original = attention.kernel_unified_attention
        proxy = policy.create(attention, helpers, backend, run / "source/candidate_attention.py")
        for name, module in (("backend.py", backend), ("attention.py", attention),
                             ("helpers.py", helpers), ("writer.py", writer)):
            (run / "source" / name).write_bytes(Path(module.__file__).read_bytes())
        (run / "source/model-config.json").write_bytes((model / "config.json").read_bytes())
        if torch.cuda.device_count() != 1:
            raise RuntimeError("expected exactly one accelerator")
        torch.cuda.set_device(0)
        torch.manual_seed(721502)
        result["device"] = str(torch.cuda.get_device_properties(0))
        spec = FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=128, dtype=torch.bfloat16)
        builder = backend.TritonAttentionMetadataBuilder(spec, ["synthetic.attn"], config, torch.device("cuda:0"))
        impl = backend.TritonAttentionImpl(num_heads=16, head_size=128, scale=128 ** -0.5, num_kv_heads=2,
                                         alibi_slopes=None, sliding_window=None, kv_cache_dtype="auto",
                                         attn_type=backend.AttentionType.DECODER)
        layer = NS(_q_scale=torch.ones((), device="cuda"), _k_scale=torch.ones((), device="cuda"),
                   _v_scale=torch.ones((), device="cuda"))
        result["cases"] = []
        timed_case = None
        for label, lengths in (("C3-P2019-KV16K", [1] * 29 + [2019]),
                               ("Q2048-KV16K", [2048])):
            common, q, k, v, cache = previous.make_data(torch, lengths, 16384)
            prepare_pages(torch, common, k, v, 16384)
            total = common.num_actual_tokens
            q[total:] = float("nan")
            metadata = builder.build(0, common)
            plan = getattr(metadata, c3._PLAN, None)
            if (label.startswith("C3") and (plan is None or plan.prefill.num_actual_tokens != 2019
                                            or plan.prefill.query_start_loc.shape[0] != 2)):
                raise RuntimeError("actual C3 metadata did not produce the audited P2019 suffix")
            # The actual writer must skip -1 padding BEFORE loading NaN K/V.
            impl.do_kv_cache_update(layer, k, v, cache, common.slot_mapping)
            before_cache = cache.clone()
            cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
            baseline, changed = torch.full_like(q, -17), torch.full_like(q, -17)
            attention.kernel_unified_attention = original
            impl.forward(layer, q, k, v, cache, metadata, baseline)
            before_selected, before_fallback = proxy.selected_launches, proxy.fallback_launches
            attention.kernel_unified_attention = proxy
            impl.forward(layer, q, k, v, cache, metadata, changed)
            torch.cuda.synchronize()
            checks = {"all_output_bits_equal": torch.equal(baseline.view(torch.int16), changed.view(torch.int16)),
                      "valid_output_finite": bool(torch.isfinite(changed[:total]).all()),
                      "padding_untouched": bool((changed[total:] == -17).all()),
                      "entire_kv_bits_unchanged": torch.equal(before_cache.view(torch.int16), cache.view(torch.int16)),
                      "rng_unchanged": torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state()),
                      "one_prefill_selected": proxy.selected_launches - before_selected == 1,
                      "c2_decode_fallback": proxy.fallback_launches - before_fallback == (1 if plan is not None else 0)}
            result["cases"].append({"case": label, "lengths": lengths, "kv_len": 16384,
                                    "random_physical_pages": True,
                                    "reused_old_prefix_blocks": 16 if len(lengths) > 1 else 0,
                                    "negative_padding_slots": 3, "correctness": checks})
            if not all(checks.values()):
                raise AssertionError("visible-prefix correctness/scope failed: " + repr(checks))
            if plan is not None:
                timed_case = (q, k, v, cache, metadata)

        q, k, v, cache, metadata = timed_case
        baseline_out, candidate_out = torch.empty_like(q), torch.empty_like(q)
        def invoke(output):
            impl.forward(layer, q, k, v, cache, metadata, output)
        for target, output in ((original, baseline_out), (proxy, candidate_out)):
            attention.kernel_unified_attention = target
            invoke(output); invoke(output)
            torch.cuda.synchronize()
        # Initialize all timing Events on this stream before ANY wall window.
        # This also excludes first-record lazy initialization, unlike old914.
        pairs = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in range(4)]
        for start, end in pairs:
            start.record(); end.record()
        torch.cuda.synchronize()
        result["timings"] = []
        for name, pair in zip(("baseline", "candidate", "candidate", "baseline"), pairs):
            attention.kernel_unified_attention = original if name == "baseline" else proxy
            output = baseline_out if name == "baseline" else candidate_out
            row = timed_batch(torch, lambda: invoke(output), pair, 32)
            row["policy"] = name
            result["timings"].append(row)
        result["summary"] = {}
        for kind in ("wall", "event"):
            a = statistics.median(x[kind + "_per_call_ms"] for x in result["timings"] if x["policy"] == "baseline")
            b = statistics.median(x[kind + "_per_call_ms"] for x in result["timings"] if x["policy"] == "candidate")
            result["summary"][kind] = {"baseline_ms": a, "candidate_ms": b, "fraction_saved": 1 - b / a}
        result["selected_launches"], result["fallback_launches"] = proxy.selected_launches, proxy.fallback_launches
        result["status"] = "correctness_passed_single_layer_signal_only"
    except BaseException:
        result["status"], result["error"] = "failed", traceback.format_exc()
        traceback.print_exc()
    finally:
        if attention is not None and original is not None:
            attention.kernel_unified_attention = original
            result["original_proxy_restored"] = attention.kernel_unified_attention is original
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
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
    parser.add_argument("--policy-path", type=Path)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir, args.model)
    if any(path is None for path in (args.runtime_path, args.mixed_path, args.policy_path)):
        parser.error("controller requires C2, C3 and visible-prefix candidate paths")
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
                "kind": "two actual-layer prefix mask correctness cases, one P2019 ABBA, no weights/service/score",
                "timing_loops": 32, "timing_method": TIMING_METHOD,
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
                           ("mixed.py", args.mixed_path), ("policy.py", args.policy_path),
                           ("validate_hidden_row_gather.py", Path(utilities.__file__)),
                           ("validate_mixed_decode.py", Path(previous.__file__)),
                           ("bench_attention_dispatch.py", Path(shared.__file__)),
                           ("validate_block_table_candidate.py", Path(owner.__file__)),
                           ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh")):
            (source / name).write_bytes(path.read_bytes())
        for name, expected in (("runtime.py", EXPECTED_C2), ("mixed.py", EXPECTED_C3), ("policy.py", EXPECTED_POLICY)):
            if expected is None or digest(source / name) != expected:
                raise RuntimeError("unaudited visible-prefix gate asset: " + name)
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["packages"] = {}
        for package in ("torch", "vllm", "FlagGems", "SQLAlchemy"):
            try:
                manifest["packages"][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][package] = "unavailable"
        manifest["worker_command"] = [sys.executable, str(source / "gate.py"), "--worker", "--run-dir", str(run),
                                      "--model", str(args.model)]
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
