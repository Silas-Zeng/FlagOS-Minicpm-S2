#!/usr/bin/env python3
"""复用 D1/P2047 正确性门；隔离 V-late 默认实例与仅设 PREFER_SHARED 的同 binary 实例。

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
EXPECTED_POLICY = "89134ef1d49d532d91d460094ae7a0563d1546c7d1b8b529490b77ecfa16ab08"
EXPECTED_CACHE_HELPER = "8604e373976951d95b939b4b3f56e00a6170ab0f10d28c73f0b124dc1e8f938f"
EXPECTED_CACHE_BRIDGE = "51d50f4516282c441594c7597ff414f7982b15543a3555e1e46ad62c5a9872ae"
TIMING_METHOD = "baseline anchor, A default, B cache-only, B, A, baseline anchor; 32 calls/window; prerecord events; existing wall/CPU/event boundaries"


def cpu_snapshot():
    names = {"stat": "/sys/fs/cgroup/cpu/cpu.stat",
             "quota": "/sys/fs/cgroup/cpu/cpu.cfs_quota_us",
             "period": "/sys/fs/cgroup/cpu/cpu.cfs_period_us"}
    raw = {name: Path(path).read_text(encoding="utf-8").strip() for name, path in names.items()}
    counters = {line.split()[0]: int(line.split()[1]) for line in raw["stat"].splitlines()}
    if (not {"nr_periods", "nr_throttled", "throttled_time"} <= counters.keys()
            or int(raw["quota"]) != 600000 or int(raw["period"]) != 100000):
        raise RuntimeError("expected the actual unchanged v1 six-CPU quota")
    return {"paths": names, "raw": raw, "counters": counters}


def timed_batch(torch, callback, pair, loops):
    torch.cuda.synchronize()
    before_cpu = cpu_snapshot()
    start, end = pair
    begin = time.perf_counter_ns()
    start.record()
    thread_begin, process_begin = time.thread_time_ns(), time.process_time_ns()
    for _ in range(loops):
        callback()
    submit_thread_ns = time.thread_time_ns() - thread_begin
    submit_process_ns = time.process_time_ns() - process_begin
    end.record()
    torch.cuda.synchronize()
    wall = (time.perf_counter_ns() - begin) / 1e6
    after_cpu = cpu_snapshot()
    event = start.elapsed_time(end)
    if not math.isfinite(event) or event <= 0:
        raise RuntimeError("invalid timing Event elapsed time")
    return {"calls": loops, "wall_total_ms": wall, "wall_per_call_ms": wall / loops,
            "event_total_ms": event, "event_per_call_ms": event / loops,
            "submit_thread_cpu_ns": submit_thread_ns, "submit_process_cpu_ns": submit_process_ns,
            "cpu_stat_before": before_cpu, "cpu_stat_after": after_cpu,
            "cpu_stat_delta": {name: after_cpu["counters"][name] - before_cpu["counters"][name]
                               for name in before_cpu["counters"]}}


def delta(after, before, name):
    return after[name] - before[name]


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
              "limitations": ["Actual backend/builder/writer, synthetic inputs, no model runner or weights.",
                              "Only 2D V load lifetime; BM128/T64/w8/s1, original 3D C2/reducer/math/scale retained.",
                              "D1/P2047 KV16K is an upper-bound fixture, not an observed native seq_len.",
                              "Submit CPU clocks include callback work; the sole kernel change is delayed V address/load/cast.",
                              "Bitwise is a conservative gate: a mismatch stops timing, not a model-accuracy verdict. allclose 0.01 is recorded only, not a relaxed pass condition.",
                              "No graph replay, service, official-performance or model-accuracy conclusion."]}
    torch, attention, original, manager = None, None, None, None
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
        c2 = load("c3_views_gate_c2", run / "source/runtime.py")
        c3 = load("c3_views_gate_c3", run / "source/mixed.py")
        policy = load("c3_views_gate_policy", run / "source/policy.py")
        result["c2_install"], result["c3_install"] = c2.install(), c3.install()
        original = (attention.kernel_unified_attention, attention.reduce_segments,
                    backend.TritonAttentionImpl.forward)
        prepare_begin = time.perf_counter_ns()
        manager = policy.create(attention, helpers, backend)
        result["manager_prepare_wall_ns"] = time.perf_counter_ns() - prepare_begin
        cache_probe = load("isolated_cache_probe", run / "source/cache_experiment.py")
        pair = cache_probe.CachePair(manager, run / "source/cache_bridge.c")
        result["cache_experiment"] = pair.report
        result["limitations"].append("Only per-function PREFER_SHARED is set; dynamic shared optin is untouched. No function cache getter exists; success rc is not proof of an effective carveout or occupancy change.")
        for name, module in (("backend.py", backend), ("attention.py", attention),
                             ("helpers.py", helpers), ("writer.py", writer)):
            (run / "source" / name).write_bytes(Path(module.__file__).read_bytes())
        (run / "source/model-config.json").write_bytes((model / "config.json").read_bytes())
        if torch.cuda.device_count() != 1:
            raise RuntimeError("expected exactly one accelerator")
        torch.cuda.set_device(0)
        torch.manual_seed(721502)
        result["device"] = str(torch.cuda.get_device_properties(0))
        result["torch_num_threads"] = torch.get_num_threads()
        spec = FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=128, dtype=torch.bfloat16)
        builder = backend.TritonAttentionMetadataBuilder(spec, ["synthetic.attn"], config, torch.device("cuda:0"))
        impl = backend.TritonAttentionImpl(num_heads=16, head_size=128, scale=128 ** -0.5, num_kv_heads=2,
                                         alibi_slopes=None, sliding_window=None, kv_cache_dtype="auto",
                                         attn_type=backend.AttentionType.DECODER)
        layer = NS(_q_scale=torch.full((), 0.75, device="cuda"),
                   _k_scale=torch.full((), 1.25, device="cuda"),
                   _v_scale=torch.full((), 0.5, device="cuda"))
        scale_objects = (layer._q_scale, layer._k_scale, layer._v_scale)
        scale_values = tuple(scale.clone() for scale in scale_objects)
        result["cases"] = []
        timed_case = None
        for label, lengths in (("C3-P2047-KV16K", [1, 2047]),):
            common, q, k, v, cache = previous.make_data(torch, lengths, 16384)
            prepare_pages(torch, common, k, v, 16384)
            total = common.num_actual_tokens
            q[total:] = float("nan")
            metadata = builder.build(0, common)
            plan = getattr(metadata, c3._PLAN, None)
            if (label.startswith("C3") and (plan is None or plan.prefill.num_actual_tokens != 2047
                                            or plan.prefill.query_start_loc.shape[0] != 2)):
                raise RuntimeError("actual C3 metadata did not produce the audited P2047 suffix")
            impl.do_kv_cache_update(layer, k, v, cache, common.slot_mapping)
            before_cache = cache.clone()
            cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
            baseline, changed = torch.full_like(q, -17), torch.full_like(q, -17)
            manager.install_baseline_observer()
            impl.forward(layer, q, k, v, cache, metadata, baseline)
            manager.restore()
            pair.prepare(torch, lambda: impl.forward(layer, q, k, v, cache, metadata, changed))
            manager.install()
            before_bootstrap = manager.snapshot()
            impl.forward(layer, q, k, v, cache, metadata, changed)
            after_bootstrap = manager.snapshot()
            torch.cuda.synchronize()
            checks = {"all_output_bits_equal": torch.equal(baseline.view(torch.int16), changed.view(torch.int16)),
                      "valid_output_finite": bool(torch.isfinite(changed[:total]).all()),
                      "padding_untouched": bool((changed[total:] == -17).all()),
                      "entire_kv_bits_unchanged": torch.equal(before_cache.view(torch.int16), cache.view(torch.int16)),
                      "rng_unchanged": torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state()),
                      "default_scale_arguments_same": delta(after_bootstrap, before_bootstrap, "selected_calls") == 1
                                                     and delta(after_bootstrap, before_bootstrap, "fallback_calls") == 0,
                      "original_3d_preserved": delta(after_bootstrap, before_bootstrap, "original_3d_calls") == 1,
                      "layer_scale_values_preserved": all(torch.equal(a, b) for a, b in zip(scale_objects, scale_values))}

            # Same shape, different input values and output storage. Explicit
            # nondefault stream consumes a default-stream producer Event.
            q2 = q.clone()
            q2[:total].mul_(0.5)
            reference2, changed2 = torch.full_like(q2, -17), torch.full_like(q2, -17)
            producer, done = torch.cuda.Event(), torch.cuda.Event()
            side = torch.cuda.Stream()
            producer.record()
            before_hot = manager.snapshot()
            with torch.cuda.stream(side):
                side.wait_event(producer)
                manager.restore()
                impl.forward(layer, q2, k, v, cache, metadata, reference2)
                manager.install()
                impl.forward(layer, q2, k, v, cache, metadata, changed2)
                # Form the consumer on the tested stream before its completion
                # Event, not on the default stream after an extra device sync.
                side_equal = (reference2.view(torch.int16) == changed2.view(torch.int16)).all()
                side_finite = torch.isfinite(changed2[:total]).all()
                done.record()
            done.synchronize()
            after_hot = manager.snapshot()
            checks.update({"new_q_pointer": q2.data_ptr() != q.data_ptr(),
                           "new_output_pointer": changed2.data_ptr() != changed.data_ptr(),
                           "nondefault_stream": int(side.cuda_stream) != int(torch.cuda.default_stream().cuda_stream),
                           "new_pointer_output_bits_equal": bool(side_equal.item()),
                           "new_pointer_output_finite": bool(side_finite.item()),
                           "new_pointer_padding_untouched": bool((changed2[total:] == -17).all()),
                           "selected_on_new_pointer": delta(after_hot, before_hot, "selected_calls") == 1,
                           "other_2d_fallbacks": delta(after_hot, before_hot, "fallback_calls") == 0,
                           "original_3d_new_pointer_preserved": delta(after_hot, before_hot, "original_3d_calls") == 1,
                           "kv_unchanged_after_new_pointer": torch.equal(before_cache.view(torch.int16), cache.view(torch.int16)),
                           "rng_unchanged_after_new_pointer": torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state())})
            scale_check = None
            if plan is not None:
                errors = []
                before_scale = manager.snapshot()
                for enabled in (False, True):
                    manager.install() if enabled else manager.restore()
                    try:
                        impl.forward(layer, q, k, v, cache, metadata, changed,
                                     output_scale=layer._q_scale, output_block_scale=layer._k_scale)
                    except NotImplementedError as exc:
                        errors.append((type(exc).__name__, str(exc), exc.__context__ is None))
                    else:
                        raise AssertionError("non-None block output scale lost the original error")
                after_scale = manager.snapshot()
                scale_check = {"errors": errors, "before": before_scale, "after": after_scale}
                checks["unsupported_output_scales_original_error"] = (errors[0] == errors[1] and errors[0][2])
                checks["unsupported_output_scales_fallback"] = (delta(after_scale, before_scale, "fallback_calls") == 0
                                                                and delta(after_scale, before_scale, "selected_calls") == 0)
            checks["layer_scale_identity_preserved"] = all(a is b for a, b in zip(
                scale_objects, (layer._q_scale, layer._k_scale, layer._v_scale)))
            result["cases"].append({"case": label, "lengths": lengths, "kv_len": 16384,
                                    "random_physical_pages": True,
                                    "reused_old_prefix_blocks": 16 if len(lengths) > 1 else 0,
                                    "negative_padding_slots": 3, "correctness": checks,
                                    "bootstrap_before": before_bootstrap, "bootstrap_after": after_bootstrap,
                                    "hot_before": before_hot, "hot_after": after_hot,
                                    "nondefault_stream_handle": int(side.cuda_stream),
                                    "layer_scale_values": [0.75, 1.25, 0.5], "output_scale_guard": scale_check,
                                    "numerical_error": {"max_abs": float((baseline[:total].float()-changed[:total].float()).abs().max().item()),
                                        "max_relative_to_baseline_floor_1e_6": float(((baseline[:total].float()-changed[:total].float()).abs()/baseline[:total].float().abs().clamp_min(1e-6)).max().item()),
                                        "candidate_nan_count": int(torch.isnan(changed[:total]).sum().item()),
                                        "baseline_nan_count": int(torch.isnan(baseline[:total]).sum().item()),
                                        "allclose_atol_0_01_rtol_0_01": bool(torch.allclose(baseline[:total], changed[:total], atol=0.01, rtol=0.01))}})
            if not all(checks.values()):
                raise AssertionError("prefill late-V correctness/scope failed: " + repr(checks))
            if plan is not None:
                timed_case = (q, k, v, cache, metadata)

        q, k, v, cache, metadata = timed_case
        baseline_out, candidate_out = torch.empty_like(q), torch.empty_like(q)
        def invoke(output):
            impl.forward(layer, q, k, v, cache, metadata, output)
        for name, output in (("baseline", baseline_out), ("late_v_default", candidate_out), ("candidate", candidate_out)):
            pair.select(name)
            invoke(output); invoke(output)
            torch.cuda.synchronize()
        pairs = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in range(6)]
        for start, end in pairs:
            start.record(); end.record()
        torch.cuda.synchronize()
        result["timings"] = []
        for name, event_pair in zip(("baseline", "late_v_default", "candidate", "candidate", "late_v_default", "baseline"), pairs):
            pair.select(name)
            output = baseline_out if name == "baseline" else candidate_out
            before = manager.snapshot()
            row = timed_batch(torch, lambda: invoke(output), event_pair, 32)
            after = manager.snapshot()
            row.update(policy=name, counters_before=before, counters_after=after)
            if name != "baseline" and (delta(after, before, "selected_calls") != 32
                                         or delta(after, before, "fallback_calls") != 0
                                         or delta(after, before, "original_3d_calls") != 32):
                raise AssertionError("timing did not exercise exactly 32 prefill late-V selections")
            result["timings"].append(row)
        result["summary"] = {}
        for kind in ("wall", "event"):
            a = statistics.median(x[kind + "_per_call_ms"] for x in result["timings"] if x["policy"] == "baseline")
            b = statistics.median(x[kind + "_per_call_ms"] for x in result["timings"] if x["policy"] == "candidate")
            result["summary"][kind] = {"baseline_ms": a, "candidate_ms": b, "fraction_saved": 1 - b / a}
        result["cache_only_comparison"] = {}
        for kind in ("wall", "event"):
            a = statistics.median(x[kind + "_per_call_ms"] for x in result["timings"] if x["policy"] == "late_v_default")
            b = statistics.median(x[kind + "_per_call_ms"] for x in result["timings"] if x["policy"] == "candidate")
            result["cache_only_comparison"][kind] = {"late_v_default_ms": a, "late_v_cache_ms": b, "fraction_saved": 1 - b / a}
        result["final_counters"] = manager.snapshot()
        result["status"] = "correctness_passed_single_layer_signal_only"
    except BaseException:
        result["status"], result["error"] = "failed", traceback.format_exc()
        traceback.print_exc()
    finally:
        if manager is not None:
            try:
                manager.restore()
                result["restored_counters"] = manager.snapshot()
                result["original_forward_restored"] = (not manager.active
                    and manager.backend.TritonAttentionImpl.forward is manager.original_forward)
                if not result["original_forward_restored"]:
                    result["status"] = "failed"
            except BaseException:
                result["status"], result["restore_error"] = "failed", traceback.format_exc()
        if attention is not None and original is not None:
            result["original_global_bindings_retained"] = (attention.kernel_unified_attention is original[0]
                                                           and attention.reduce_segments is original[1]
                                                           and backend.TritonAttentionImpl.forward is original[2])
            if not result["original_global_bindings_retained"]:
                result["status"] = "failed"
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
    parser.add_argument("--cache-helper-path", type=Path)
    parser.add_argument("--cache-bridge-path", type=Path)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir, args.model)
    if any(path is None for path in (args.runtime_path, args.mixed_path, args.policy_path, args.cache_helper_path, args.cache_bridge_path)):
        parser.error("controller requires C2, C3 and late-V candidate paths")
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
                "kind": "D1/P2047 cache-only isolation; original anchors and V-late default/cache ABBA32; original correctness gate; no service/score",
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
        base_path = os.environ["PYTHONPATH"].split(os.pathsep)[0]
        if not base_path:
            raise RuntimeError("PYTHONPATH must begin with the clean base source directory")
        base_runner = Path(base_path) / "vllm_fl/worker/model_runner.py"
        manifest["base_runner_sha256"] = digest(base_runner)
        if manifest["base_runner_sha256"] != "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141":
            raise RuntimeError("gate requires the clean combined 6f runner")
        manifest["preflight"] = owner.preflight(args.ixsmi)
        gpu = subprocess.check_output([args.ixsmi], text=True, timeout=10)
        (run / "preflight-ixsmi.txt").write_text(gpu, encoding="utf-8")
        if "No running processes found" not in gpu:
            raise RuntimeError("accelerator process already active")
        source = run / "source"
        source.mkdir()
        for name, path in (("gate.py", Path(__file__)), ("runtime.py", args.runtime_path),
                           ("mixed.py", args.mixed_path), ("policy.py", args.policy_path),
                           ("cache_experiment.py", args.cache_helper_path),
                           ("cache_bridge.c", args.cache_bridge_path),
                           ("validate_hidden_row_gather.py", Path(utilities.__file__)),
                           ("validate_mixed_decode.py", Path(previous.__file__)),
                           ("bench_attention_dispatch.py", Path(shared.__file__)),
                           ("validate_block_table_candidate.py", Path(owner.__file__)),
                           ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh")):
            (source / name).write_bytes(path.read_bytes())
        for name, expected in (("runtime.py", EXPECTED_C2), ("mixed.py", EXPECTED_C3), ("policy.py", EXPECTED_POLICY),
                               ("cache_experiment.py", EXPECTED_CACHE_HELPER), ("cache_bridge.c", EXPECTED_CACHE_BRIDGE)):
            if expected is None or digest(source / name) != expected:
                raise RuntimeError("unaudited prefill late-V gate asset: " + name)
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
