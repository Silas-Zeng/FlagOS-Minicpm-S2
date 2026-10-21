#!/usr/bin/env python3
"""Four actual-layer mapped-decode gates; optional one warm 32-call ABBA.

No weights/service/score. Controller is CPU-only; its one owned child alone
uses the accelerator. The original C3 and full-2D outputs are both retained.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import gc
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
import weakref

from validate_hidden_row_gather import digest, load, utc, write

EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"
EXPECTED_C3 = "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42"
EXPECTED_WRITER = "f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb"
EXPECTED_POLICY = "d085ad6dcc0fd5dc26188d3e0f5801b8e394dc07a79c05a376192ec9e1e95b4b"
EXPECTED_TRANSFORM = "919e80abf5b95c55ea63aa8619fa3202cd78b0c4cc0e303df7b4197bf1898316"
EXPECTED_DERIVED = "72713a90584bc6567706fb881188afa04335230afc13e021c10f862f88d054a1"
TIMING_METHOD = "optional first-case actual build+forward ABBA; pre-recorded Events; 32 calls/window; one final drain/window"


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
    return {"calls": loops, "wall_per_call_ms": wall / loops,
            "event_per_call_ms": event / loops}


def pages_and_slots(torch, common, key, value, kv_len):
    rows, blocks = common.block_table_tensor.shape
    table = torch.randperm(rows * blocks, device="cuda", dtype=torch.int64).to(torch.int32).reshape(rows, blocks)
    if rows > 1:
        table[-1, :16] = table[0, :16]  # Only cached old positions are shared.
    common.block_table_tensor = table
    pages = table.cpu().tolist()
    lengths = (common.query_start_loc_cpu[1:] - common.query_start_loc_cpu[:-1]).tolist()
    slots = [pages[r][pos // 16] * 16 + pos % 16
             for r, length in enumerate(lengths) for pos in range(kv_len - length, kv_len)]
    common.slot_mapping = torch.tensor(slots + [-1] * 3, dtype=torch.int64, device="cuda")
    key[common.num_actual_tokens:] = float("nan")
    value[common.num_actual_tokens:] = float("nan")


def float_reference(torch, q, cache, metadata, lengths, offsets, changed):
    """Few FP32 causal rows, independent of both Triton address implementations.

    This small numerical gate is additional to exact same-config C2 equality;
    its 3e-2 relative / 3e-2 absolute tolerance is explicitly not model accuracy.
    """
    refs = []
    single = next(r for r, length in enumerate(lengths) if length == 1)
    multi = next(r for r, length in enumerate(lengths) if length > 1)
    for r, local in ((single, 0), (multi, 0), (multi, lengths[multi] - 1)):
        t = offsets[r] + local
        seq_len = int(metadata.seq_lens[r].item())
        visible = seq_len - lengths[r] + local + 1
        table = metadata.block_table[r, :(seq_len + 15) // 16].long()
        logical = cache.index_select(0, table)
        k = logical[:, 0].reshape(-1, 2, 128)[:visible].float().repeat_interleave(8, dim=1)
        v = logical[:, 1].reshape(-1, 2, 128)[:visible].float().repeat_interleave(8, dim=1)
        scores = torch.einsum("hd,lhd->hl", q[t].float(), k) * (128 ** -0.5)
        expected = torch.einsum("hl,lhd->hd", scores.softmax(-1), v)
        actual = changed[t].float()
        refs.append({"request": r, "token": t, "visible_kv": visible,
                     "max_abs_diff": float((actual - expected).abs().max()),
                     "passed": bool(torch.allclose(actual, expected, atol=3e-2, rtol=3e-2))})
    return refs


def worker(run, model, timing):
    result = {"status": "started", "accuracy": "not evaluated", "official_performance": "not evaluated",
              "timing": timing, "timing_method": TIMING_METHOD, "cases": [],
              "worker_command": [sys.executable, *sys.argv],
              "limitations": ["Actual Builder/Impl/writer; synthetic BF16 inputs; no weights or runner execution.",
                              "New singleton 3D reduction can differ from original C3/2D; old accuracy is not inherited.",
                              "FP32 three-row tolerance is not whole-model accuracy; FIRST_SELECTED real_execute=0 is expected."]}
    torch, backend, handles = None, None, None
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
        backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
        attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
        writer = importlib.import_module("vllm.v1.attention.ops.triton_reshape_and_cache_flash")
        if (digest(Path(writer.__file__)) != EXPECTED_WRITER
                or backend.triton_reshape_and_cache_flash is not writer.triton_reshape_and_cache_flash):
            raise RuntimeError("unaudited actual KV writer source/binding")
        c2, c3 = load("mapped_gate_c2", run / "source/runtime.py"), load("mapped_gate_c3", run / "source/mixed.py")
        policy = load("mapped_gate_policy", run / "source/policy.py")
        transform = load("mapped_gate_transform", run / "source/transform.py")
        result["c2_install"], result["c3_install"] = c2.install(), c3.install()
        for name, expected in policy.EXPECTED.items():
            # Gate loads C2/C3 by independent archive names; their actual files
            # were pinned by controller and C3 checks the installed C2 object.
            if name.startswith("vllm_fl.patches."):
                continue
            module = importlib.import_module(name)
            policy._require(module, expected)
            (run / "source" / (name.rsplit(".", 1)[-1] + ".py")).write_bytes(Path(module.__file__).read_bytes())
        helpers = importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
        if transform.transform_attention(Path(attention.__file__).read_bytes(), Path(helpers.__file__).read_bytes()) != (run / "source/candidate_attention.py").read_bytes():
            raise RuntimeError("derived source not byte-identical to exact transform")
        derived = policy.load_derived(run / "source/candidate_attention.py")
        (run / "source/writer.py").write_bytes(Path(writer.__file__).read_bytes())
        (run / "source/model-config.json").write_bytes((model / "config.json").read_bytes())
        if torch.cuda.device_count() != 1:
            raise RuntimeError("expected exactly one accelerator")
        torch.cuda.set_device(0)
        torch.manual_seed(721803)
        result["device"] = str(torch.cuda.get_device_properties(0))
        spec = FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=128, dtype=torch.bfloat16)
        builder = backend.TritonAttentionMetadataBuilder(spec, ["synthetic.attn"], config, torch.device("cuda:0"))
        impl = backend.TritonAttentionImpl(num_heads=16, head_size=128, scale=128 ** -0.5, num_kv_heads=2,
                                         alibi_slopes=None, sliding_window=None, kv_cache_dtype="auto",
                                         attn_type=backend.AttentionType.DECODER)
        if not c3._builder_eligible(builder, backend, torch) or not policy._extra_builder_scope(builder):
            raise RuntimeError("actual model configuration is ineligible; no override allowed")
        layer = NS(_q_scale=torch.ones((), device="cuda"), _k_scale=torch.ones((), device="cuda"),
                   _v_scale=torch.ones((), device="cuda"))
        handles = policy._wrap_backend(backend, derived, torch, c3)
        base_forward = handles["original_forward"].__wrapped__
        mapped_forward = backend.TritonAttentionImpl.forward
        cases = (("D29-nonprefix", [1] * 10 + [2019] + [1] * 19),
                 ("D1-tail", [127, 1]), ("D1-middle", [7, 1, 9]),
                 ("D64-N65", [1984] + [1] * 64))
        timed = None
        for label, lengths in cases:
            # Reserve one extra page per request for an actual append at
            # position 16384 after this 16K step; metadata remains length16K.
            common, q, k, v, cache = previous.make_data(torch, lengths, 16385)
            common.max_seq_len = 16384
            common.seq_lens.fill_(16384)
            pages_and_slots(torch, common, k, v, 16384)
            total, offsets = common.num_actual_tokens, common.query_start_loc_cpu.tolist()
            q[total:] = float("nan")
            expected_write = cache.clone()
            valid_slots = common.slot_mapping[:total]
            expected_write[valid_slots // 16, 0, valid_slots % 16] = k[:total]
            expected_write[valid_slots // 16, 1, valid_slots % 16] = v[:total]
            impl.do_kv_cache_update(layer, k, v, cache, common.slot_mapping)
            writer_exact = torch.equal(expected_write.view(torch.int16), cache.view(torch.int16))
            del expected_write
            if not writer_exact:
                raise AssertionError("actual KV writer changed padding/unmapped slots")
            before_cache = cache.clone()
            metadata = builder.build(0, common)
            plan = getattr(metadata, policy._PLAN, None)
            if plan is None:
                raise RuntimeError("expected mapped plan: " + label)
            indices = [r for r, length in enumerate(lengths) if length == 1]
            token_indices = torch.tensor([offsets[r] for r in indices], dtype=torch.long, device="cuda")
            request_indices = torch.tensor(indices, dtype=torch.long, device="cuda")
            whole, old_c3, oracle, changed, skip = [torch.full_like(q, -17) for _ in range(5)]
            captured = {}
            def capture(**kwargs):
                captured.update(kwargs)
                return handles["original_unified"](**kwargs)
            backend.unified_attention = capture
            base_forward(impl, layer, q, k, v, cache, metadata, whole)
            backend.unified_attention = handles["proxy"]
            handles["original_forward"](impl, layer, q, k, v, cache, metadata, old_c3)
            oracle.copy_(whole)
            d = len(indices)
            decode = replace(metadata, num_actual_tokens=d, max_query_len=1,
                             query_start_loc=torch.arange(d + 1, dtype=torch.int32, device="cuda"),
                             seq_lens=metadata.seq_lens.index_select(0, request_indices),
                             block_table=metadata.block_table.index_select(0, request_indices),
                             slot_mapping=metadata.slot_mapping.index_select(0, token_indices))
            compact_q, compact_k, compact_v = [value.index_select(0, token_indices) for value in (q, k, v)]
            compact_out = torch.empty_like(compact_q)
            base_forward(impl, layer, compact_q, compact_k, compact_v, cache, decode, compact_out)
            oracle.index_copy_(0, token_indices, compact_out)
            captured["out"] = skip[:total]
            derived.unified_attention(**captured, biv150_skip_single_query=True)
            cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
            before_stats = policy.snapshot_stats()
            mapped_forward(impl, layer, q, k, v, cache, metadata, changed)
            torch.cuda.synchronize()
            non_single_tokens = [t for r, length in enumerate(lengths) if length > 1
                                 for t in range(offsets[r], offsets[r + 1])]
            checks = {
                "map_all_singletons_once": plan.cpu_indices.tolist() == indices,
                "actual_writer_all_slots_exact": writer_exact,
                "all_output_bits_equal_independent_oracle": torch.equal(oracle.view(torch.int16), changed.view(torch.int16)),
                "prefill_bits_unchanged": torch.equal(whole[non_single_tokens].view(torch.int16), changed[non_single_tokens].view(torch.int16)),
                "skip_2d_leaves_singleton_sentinel": bool((skip.index_select(0, token_indices) == -17).all()),
                "skip_2d_writes_every_prefill": torch.equal(skip[non_single_tokens].view(torch.int16), whole[non_single_tokens].view(torch.int16)),
                "padding_untouched": bool((changed[total:] == -17).all()),
                "valid_output_finite": bool(torch.isfinite(changed[:total]).all()),
                "entire_kv_bits_unchanged": torch.equal(before_cache.view(torch.int16), cache.view(torch.int16)),
                "rng_unchanged": torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state()),
                "one_selected_forward": policy.snapshot_stats()["forward_selected"] - before_stats["forward_selected"] == 1,
                "one_skip_and_one_mapped_dispatch": all(policy.snapshot_stats()[key] - before_stats[key] == 1 for key in ("skip_2d_dispatches", "mapped_3d_dispatches")),
            }
            references = float_reference(torch, q, cache, metadata, lengths, offsets, changed)
            checks["three_fp32_rows"] = all(row["passed"] for row in references)
            row = {"case": label, "lengths": lengths, "kv_len": 16384, "correctness": checks,
                   "fp32_reference": references, "original_c3_max_abs_difference": float((old_c3[:total].float() - changed[:total].float()).abs().max()),
                   "original_2d_max_abs_difference": float((whole[:total].float() - changed[:total].float()).abs().max())}
            result["cases"].append(row)
            if not all(checks.values()):
                raise AssertionError("mapped gate rejection: " + repr(checks))
            if label == "D1-middle":
                # New map allocated per step on producer; consumer submits
                # without host sync, drops plan, then allocation churns.
                producer, consumer = torch.cuda.Stream(), torch.cuda.Stream()
                producer.wait_stream(torch.cuda.current_stream())
                with torch.cuda.stream(producer):
                    cross_md = builder.build(0, common)
                cross_plan = getattr(cross_md, policy._PLAN)
                weak = weakref.ref(cross_plan.gpu_indices)
                cross = torch.full_like(q, -17)
                # Output initialization was on main; establish that dependency
                # separately from runtime's metadata producer wait.
                consumer.wait_stream(torch.cuda.current_stream())
                with torch.cuda.stream(consumer):
                    mapped_forward(impl, layer, q, k, v, cache, cross_md, cross)
                    consumed = cross.clone()
                registered = consumer in cross_plan.consumers
                del cross_md, cross_plan
                gc.collect()
                churn = [torch.full((d,), -999, dtype=torch.int32, device="cuda") for _ in range(16)]
                consumer.synchronize()
                row["cross_stream"] = {"registered": registered, "python_map_released": weak() is None,
                                       "bits_equal": torch.equal(consumed.view(torch.int16), oracle.view(torch.int16))}
                if not all(row["cross_stream"].values()):
                    raise AssertionError("mapped cross-stream lifetime rejected")
                del churn
                # A mixed graph uses the original full-2D path even though
                # this metadata carries a mapped plan built outside capture.
                graph_out = torch.full_like(q, -17)
                graph_stream = torch.cuda.Stream()
                graph_stream.wait_stream(torch.cuda.current_stream())
                before_capture = policy.snapshot_stats()["forward_selected"]
                graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph, stream=graph_stream):
                    mapped_forward(impl, layer, q, k, v, cache, metadata, graph_out)
                graph_out.fill_(-17)
                graph.replay()
                torch.cuda.synchronize()
                row["capture_fallback"] = {"no_mapped_selection": policy.snapshot_stats()["forward_selected"] == before_capture,
                                           "full_2d_bits_equal": torch.equal(graph_out.view(torch.int16), whole.view(torch.int16))}
                if not all(row["capture_fallback"].values()):
                    raise AssertionError("capture did not preserve original full-2D path")
            if timed is None:
                timed = (common, q, k, v, cache)

            # Append at position16384 in the SAME physical cache. The extra
            # page was reserved above, so all old logical positions survive.
            next_common, nq, nk, nv, discarded = previous.make_data(torch, [1] * len(lengths), 16385)
            del discarded
            next_common.block_table_tensor = common.block_table_tensor
            next_common.slot_mapping = torch.tensor([int(common.block_table_tensor[r, 1024].item()) * 16 for r in range(len(lengths))], dtype=torch.int64, device="cuda")
            expected_next = cache.clone()
            next_slots = next_common.slot_mapping
            expected_next[next_slots // 16, 0, next_slots % 16] = nk[:len(lengths)]
            expected_next[next_slots // 16, 1, next_slots % 16] = nv[:len(lengths)]
            impl.do_kv_cache_update(layer, nk, nv, cache, next_common.slot_mapping)
            next_md = builder.build(0, next_common)
            na, nb = torch.full_like(nq, -17), torch.full_like(nq, -17)
            before_next = policy.snapshot_stats()["forward_selected"]
            handles["original_forward"](impl, layer, nq, nk, nv, cache, next_md, na)
            mapped_forward(impl, layer, nq, nk, nv, cache, next_md, nb)
            torch.cuda.synchronize()
            row["next_decode"] = {"mapped_plan_absent": not hasattr(next_md, policy._PLAN),
                                  "bits_equal": torch.equal(na.view(torch.int16), nb.view(torch.int16)),
                                  "entire_kv_matches_only_append": torch.equal(expected_next.view(torch.int16), cache.view(torch.int16)),
                                  "selected_unchanged": policy.snapshot_stats()["forward_selected"] == before_next}
            del expected_next
            if not all(row["next_decode"].values()):
                raise AssertionError("successor pure-decode fallback rejected")
            write(run / "results.json", result)

        if timing:
            common, q, k, v, cache = timed
            outputs = {name: torch.empty_like(q) for name in ("baseline", "candidate")}
            def invoke(name):
                if name == "candidate":
                    md = builder.build(0, common)
                    mapped_forward(impl, layer, q, k, v, cache, md, outputs[name])
                else:
                    md = handles["original_build"](builder, 0, common)
                    handles["original_forward"](impl, layer, q, k, v, cache, md, outputs[name])
            for name in outputs:
                invoke(name); invoke(name)
            pairs = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in range(4)]
            for start, end in pairs:
                start.record(); end.record()
            torch.cuda.synchronize()
            result["timings"] = []
            for name, pair in zip(("baseline", "candidate", "candidate", "baseline"), pairs):
                row = timed_batch(torch, lambda: invoke(name), pair, 32)
                row["policy"] = name
                result["timings"].append(row)
            result["summary"] = {}
            for kind in ("wall", "event"):
                a = statistics.median(row[kind + "_per_call_ms"] for row in result["timings"] if row["policy"] == "baseline")
                b = statistics.median(row[kind + "_per_call_ms"] for row in result["timings"] if row["policy"] == "candidate")
                result["summary"][kind] = {"baseline_ms": a, "candidate_ms": b, "fraction_saved": 1 - b / a}
        result["runtime_stats"] = policy.snapshot_stats()
        result["status"] = "correctness_passed_single_layer_only"
    except BaseException:
        result["status"], result["error"] = "failed", traceback.format_exc()
        traceback.print_exc()
    finally:
        if backend is not None and handles is not None:
            backend.TritonAttentionMetadataBuilder.build = handles["original_build"]
            backend.TritonAttentionImpl.forward = handles["original_forward"]
            backend.unified_attention = handles["original_unified"]
            result["original_backend_wrappers_restored"] = True
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
            except BaseException:
                result["status"], result["shutdown_error"] = "failed", traceback.format_exc()
        result["source_sha256"] = {p.name: digest(p) for p in (run / "source").iterdir() if p.is_file()}
        write(run / "results.json", result)
    return 0 if result["status"] == "correctness_passed_single_layer_only" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--runtime-path", type=Path)
    parser.add_argument("--mixed-path", type=Path)
    parser.add_argument("--policy-path", type=Path)
    parser.add_argument("--transform-path", type=Path)
    parser.add_argument("--derived-path", type=Path)
    parser.add_argument("--timing", action="store_true", help="after correctness, one 32-call ABBA includes actual metadata build")
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir, args.model, args.timing)
    if any(path is None for path in (args.runtime_path, args.mixed_path, args.policy_path, args.transform_path, args.derived_path)):
        parser.error("controller requires C2, C3, mapped policy, transform and derived paths")
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
                "kind": "four actual-layer mapped-decode correctness cases; optional one ABBA; no weights/service/score",
                "timing_loops": 32 if args.timing else 0, "timing_method": TIMING_METHOD,
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
                           ("transform.py", args.transform_path), ("candidate_attention.py", args.derived_path),
                           ("validate_hidden_row_gather.py", Path(utilities.__file__)),
                           ("validate_mixed_decode.py", Path(previous.__file__)),
                           ("bench_attention_dispatch.py", Path(shared.__file__)),
                           ("validate_block_table_candidate.py", Path(owner.__file__)),
                           ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh")):
            (source / name).write_bytes(path.read_bytes())
        for name, expected in (("runtime.py", EXPECTED_C2), ("mixed.py", EXPECTED_C3), ("policy.py", EXPECTED_POLICY),
                               ("transform.py", EXPECTED_TRANSFORM), ("candidate_attention.py", EXPECTED_DERIVED)):
            if expected is None or digest(source / name) != expected:
                raise RuntimeError("unaudited mapped-decode gate asset: " + name)
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["packages"] = {}
        for package in ("torch", "vllm", "FlagGems", "SQLAlchemy"):
            try:
                manifest["packages"][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][package] = "unavailable"
        manifest["worker_command"] = [sys.executable, str(source / "gate.py"), "--worker", "--run-dir", str(run),
                                      "--model", str(args.model)]
        if args.timing:
            manifest["worker_command"].append("--timing")
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
