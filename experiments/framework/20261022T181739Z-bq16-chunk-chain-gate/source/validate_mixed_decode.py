#!/usr/bin/env python3
"""Short real-backend mixed split gate; no model weights, service or score.

Run only after review and while owning the single accelerator. A successful
result proves synthetic wrapper equivalence, not MiniCPM accuracy or speed.
"""

from __future__ import annotations

import argparse
import contextlib
from dataclasses import replace
from datetime import datetime, timezone
import gc
import hashlib
import importlib.metadata
import inspect
import itertools
import json
import math
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
import traceback
from types import SimpleNamespace
import weakref


EXPECTED_RUNTIME = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"
EXPECTED_CANDIDATE = "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42"
CASES = ((63, 1985, 4096), (63, 127, 4096), (29, 2019, 16384), (29, 127, 16384))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(value):
    if isinstance(value, dict):
        return {key: safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return str(value) if isinstance(value, float) and not math.isfinite(value) else value


def write_json(path, value):
    path.write_text(json.dumps(safe(value), indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


class Tee:
    def __init__(self, original, log):
        self.original, self.log = original, log

    def write(self, value):
        self.original.write(value)
        self.log.write(value)
        self.flush()
        return len(value)

    def flush(self):
        self.original.flush()
        self.log.flush()

    def __getattr__(self, name):
        return getattr(self.original, name)


def manual_children(metadata, prefix, count):
    """Independent reference: never use the candidate plan's child metadata."""
    total = metadata.num_actual_tokens
    decode = replace(metadata, num_actual_tokens=prefix, max_query_len=1,
                     query_start_loc=metadata.query_start_loc[:prefix + 1],
                     seq_lens=metadata.seq_lens[:prefix],
                     block_table=metadata.block_table[:prefix],
                     slot_mapping=metadata.slot_mapping[:prefix])
    prefill = replace(metadata, num_actual_tokens=total - prefix,
                      query_start_loc=metadata.query_start_loc[prefix:count + 1] - prefix,
                      seq_lens=metadata.seq_lens[prefix:count],
                      block_table=metadata.block_table[prefix:count],
                      slot_mapping=metadata.slot_mapping[prefix:total])
    return decode, prefill


def make_data(torch, lengths, kv_len):
    n, total = len(lengths), sum(lengths)
    blocks = (kv_len + 15) // 16
    offsets = [0, *itertools.accumulate(lengths)]
    cu_cpu = torch.tensor(offsets, dtype=torch.int32)
    # Cache and new K/V are realistic layouts; update once before all reads.
    cache = torch.randn((n * blocks, 2, 16, 2, 128), dtype=torch.bfloat16, device="cuda")
    query = torch.randn((total + 3, 16, 128), dtype=torch.bfloat16, device="cuda")
    key = torch.randn((total + 3, 2, 128), dtype=torch.bfloat16, device="cuda")
    value = torch.randn_like(key)
    slots = [row * blocks * 16 + kv_len - length + token
             for row, length in enumerate(lengths) for token in range(length)]
    common = SimpleNamespace(
        num_reqs=n, num_actual_tokens=total, max_query_len=max(lengths), max_seq_len=kv_len,
        query_start_loc_cpu=cu_cpu, query_start_loc=cu_cpu.to("cuda"),
        seq_lens=torch.full((n,), kv_len, dtype=torch.int32, device="cuda"),
        block_table_tensor=torch.arange(n * blocks, dtype=torch.int32, device="cuda").reshape(n, blocks),
        slot_mapping=torch.tensor(slots, dtype=torch.int64, device="cuda"),
        causal=True, mm_req_doc_ranges=None,
    )
    return common, query, key, value, cache


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--runtime-path", type=Path, required=True)
    parser.add_argument("--candidate-path", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args()
    # --help and importing this module stay CPU-only, also on Windows.
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
        "kind": "synthetic actual backend gate; no weights/service/accuracy/performance score",
        "environment": {key: os.environ[key] for key in (
            "VLLM_PLUGINS", "PYTHONPATH", "CUDA_VISIBLE_DEVICES", "IX_VISIBLE_DEVICES",
            "COREX_VISIBLE_DEVICES", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "TRITON_CACHE_DIR",
            "VLLM_FL_USE_FLAGGEMS_ATTN", "VLLM_FL_ILUVATAR_KEEP_SAMPLER_COMPILE", "USE_FLAGTUNE",
        ) if key in os.environ},
    }
    result = {"status": "started", "mixed_cases": [], "accuracy": "not evaluated", "limitations": [
        "Synthetic one-layer random Q/K/V, actual Builder/Impl and VllmConfig; no model weights are loaded.",
        "Manual split equality validates wrapper integration, not the numerical accuracy of 2D to 3D decode.",
        "Cross-stream wait/registration/release and opportunistic allocator churn are checked, not all possible schedules.",
        "No timings or official benchmark results are produced.",
    ]}
    lock, monitor, torch, monitor_log = None, None, None, None
    status = 1

    def checkpoint():
        write_json(run / "manifest.json", manifest)
        write_json(run / "results.json", result)

    checkpoint()
    write_json(run / "command.json", manifest["command"])
    with (run / "gate.log").open("x", encoding="utf-8") as log:
        with contextlib.redirect_stdout(Tee(sys.stdout, log)), contextlib.redirect_stderr(Tee(sys.stderr, log)):
            try:
                lock = (root / "framework-device.lock").open("a")
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                manifest["preflight"] = validator.preflight(args.ixsmi)
                manifest["lock_acquired_utc"] = validator.utc()
                source = run / "source"
                source.mkdir()
                for label, path in (
                    ("validation.py", Path(__file__)), ("runtime.py", args.runtime_path),
                    ("candidate.py", args.candidate_path), ("bench_attention_dispatch.py", Path(shared.__file__)),
                    ("validate_block_table_candidate.py", Path(validator.__file__)),
                    ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh"),
                ):
                    (source / label).write_bytes(path.read_bytes())
                manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
                checkpoint()
                if digest(source / "runtime.py") != EXPECTED_RUNTIME or digest(source / "candidate.py") != EXPECTED_CANDIDATE:
                    raise RuntimeError("runtime/candidate bytes differ from independently reviewed versions")
                import torch
                import vllm.v1.attention.backends.triton_attn as backend
                import vllm.v1.attention.ops.triton_unified_attention as attention
                import vllm.v1.attention.ops.triton_attention_helpers as helpers
                import vllm.engine.arg_utils as arg_utils
                import vllm.v1.kv_cache_interface as kv_interface
                from vllm.config import CompilationConfig, CUDAGraphMode
                api = {"EngineArgs": arg_utils.EngineArgs, "CompilationConfig": CompilationConfig,
                       "FullAttentionSpec": kv_interface.FullAttentionSpec,
                       "Builder": backend.TritonAttentionMetadataBuilder,
                       "Impl": backend.TritonAttentionImpl}
                manifest["api_signatures"] = {name: str(inspect.signature(value)) for name, value in api.items()}
                manifest["api_signatures"]["create_engine_config"] = str(inspect.signature(arg_utils.EngineArgs.create_engine_config))
                for label, module in (("backend", backend), ("attention", attention), ("helpers", helpers),
                                      ("arg_utils", arg_utils), ("kv_cache_interface", kv_interface)):
                    (source / (label + ".py")).write_bytes(Path(module.__file__).read_bytes())
                (source / "model-config.json").write_bytes((args.model / "config.json").read_bytes())
                manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
                manifest["packages"] = {}
                for name in ("torch", "vllm", "vllm-plugin-fl", "triton", "flag-gems", "flagtree"):
                    try:
                        manifest["packages"][name] = importlib.metadata.version(name)
                    except importlib.metadata.PackageNotFoundError:
                        manifest["packages"][name] = "distribution name unavailable"
                checkpoint()
                if torch.cuda.device_count() != 1:
                    raise RuntimeError("expected one accelerator")
                torch.cuda.set_device(0)
                torch.manual_seed(args.seed)
                manifest["device"] = str(torch.cuda.get_device_properties(0))
                monitor_log = (run / "monitor.log").open("x")
                monitor = subprocess.Popen(["bash", str(source / "monitor_gpu.sh"), str(os.getpid()), str(run / "gpu.csv")],
                                           stdout=monitor_log, stderr=subprocess.STDOUT)
                manifest["monitor_pid"] = monitor.pid
                runtime = shared.load("biv150_gate_runtime", source / "runtime.py")
                mixed = shared.load("biv150_gate_mixed", source / "candidate.py")
                original_build = backend.TritonAttentionMetadataBuilder.build
                original_forward = backend.TritonAttentionImpl.forward
                original_kv_update = backend.TritonAttentionImpl.do_kv_cache_update
                config_kwargs = dict(model=str(args.model), served_model_name=["minicpm"],
                                     gpu_memory_utilization=0.85, max_model_len=131072,
                                     compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY))
                manifest["engine_args"] = {**config_kwargs, "compilation_config": {"cudagraph_mode": "FULL_DECODE_ONLY"}}
                checkpoint()
                config = arg_utils.EngineArgs(**config_kwargs).create_engine_config()
                # Platform configuration can evict/reimport the attention op
                # and refresh the backend alias. Install only after that step,
                # exactly as the serving worker imports ModelRunnerFL later.
                attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
                manifest["runtime_install"] = runtime.install()
                manifest["mixed_install"] = mixed.install()
                if backend.TritonAttentionImpl.do_kv_cache_update is not original_kv_update:
                    raise RuntimeError("candidate unexpectedly replaced KV update")
                manifest["parsed_config"] = {
                    "model": str(config.model_config.model), "dtype": str(config.model_config.dtype),
                    "cudagraph_mode": str(config.compilation_config.cudagraph_mode),
                    "capture_sizes": config.compilation_config.cudagraph_capture_sizes,
                    "max_num_seqs": config.scheduler_config.max_num_seqs,
                    "max_num_batched_tokens": config.scheduler_config.max_num_batched_tokens,
                }
                spec = kv_interface.FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=128, dtype=torch.bfloat16)
                builder = backend.TritonAttentionMetadataBuilder(spec, ["synthetic.attn"], config, torch.device("cuda:0"))
                impl = backend.TritonAttentionImpl(num_heads=16, head_size=128, scale=128 ** -0.5,
                                                  num_kv_heads=2, alibi_slopes=None, sliding_window=None,
                                                  kv_cache_dtype="auto", attn_type=backend.AttentionType.DECODER)
                layer = SimpleNamespace(_q_scale=torch.ones((), device="cuda"),
                                        _k_scale=torch.ones((), device="cuda"), _v_scale=torch.ones((), device="cuda"))
                if not mixed._builder_eligible(builder, backend, torch):
                    raise RuntimeError("actual parsed configuration did not qualify; no synthetic config override allowed")
                checkpoint()

                def invoke(fn, data, metadata, output):
                    common, q, k, v, cache = data
                    return fn(impl, layer, q, k, v, cache, metadata, output)

                patched_forward = backend.TritonAttentionImpl.forward

                def mixed_case(d, p, kv_len, cross_stream=False):
                    data = make_data(torch, [1] * d + [p], kv_len)
                    cm, q, k, v, cache = data
                    row = {"decode_requests": d, "prefill_tokens": p, "kv_len": kv_len,
                           "cross_stream": cross_stream, "accuracy": "not evaluated"}
                    # Actual KV-update entry point runs once for all subsequent reads.
                    impl.do_kv_cache_update(layer, k[:cm.num_actual_tokens], v[:cm.num_actual_tokens], cache, cm.slot_mapping)
                    whole_md = original_build(builder, 0, cm)
                    decode_md, prefill_md = manual_children(whole_md, d, cm.num_reqs)
                    whole, expected, changed = [torch.full_like(q, -999) for _ in range(3)]
                    invoke(original_forward, data, whole_md, whole)
                    original_forward(impl, layer, q[:d], k[:d], v[:d], cache, decode_md, expected[:d])
                    original_forward(impl, layer, q[d:cm.num_actual_tokens], k[d:cm.num_actual_tokens],
                                     v[d:cm.num_actual_tokens], cache, prefill_md, expected[d:cm.num_actual_tokens])
                    torch.cuda.synchronize()
                    if cross_stream:
                        producer, consumer = torch.cuda.Stream(), torch.cuda.Stream()
                        producer.wait_stream(torch.cuda.current_stream())
                        with torch.cuda.stream(producer):
                            metadata = builder.build(0, cm)
                        plan = getattr(metadata, mixed._PLAN, None)
                        if plan is None:
                            raise RuntimeError("expected natural-prefix split plan")
                        suffix_ref = weakref.ref(plan.prefill.query_start_loc)
                        suffix_ptr = plan.prefill.query_start_loc.data_ptr()
                        if plan.producer_stream != producer:
                            raise RuntimeError("plan producer does not match builder stream")
                        before = attention.kernel_unified_attention.selected_launches
                        with torch.cuda.stream(consumer):
                            returned = invoke(patched_forward, data, metadata, changed)
                        row["fast_decode_launches"] = attention.kernel_unified_attention.selected_launches - before
                        row["consumer_registered"] = consumer in plan.consumer_streams
                        row["suffix_alive_while_plan_held"] = suffix_ref() is not None
                        # Drop the sole plan owner before synchronizing the consumer.
                        del metadata, plan
                        gc.collect()
                        row["suffix_python_released_before_consumer_sync"] = suffix_ref() is None
                        churn = [torch.full((2,), -1234, dtype=torch.int32, device="cuda") for _ in range(32)]
                        row["allocator_churn_reused_suffix_address"] = any(x.data_ptr() == suffix_ptr for x in churn)
                        consumer.synchronize()
                        torch.cuda.synchronize()
                        if not row["consumer_registered"] or not row["suffix_alive_while_plan_held"]:
                            raise RuntimeError("cross-stream plan lifecycle guard failed")
                    else:
                        metadata = builder.build(0, cm)
                        if getattr(metadata, mixed._PLAN, None) is None:
                            raise RuntimeError("expected natural-prefix split plan")
                        before = attention.kernel_unified_attention.selected_launches
                        returned = invoke(patched_forward, data, metadata, changed)
                        row["fast_decode_launches"] = attention.kernel_unified_attention.selected_launches - before
                        torch.cuda.synchronize()
                    row["returned_output_alias"] = returned is changed
                    row["patched_vs_manual_entire_storage"] = shared.compare(torch, changed, expected, q.shape[0])
                    row["whole2d_vs_split_decode"] = shared.compare(torch, whole[:d], changed[:d], d)
                    row["whole2d_vs_split_prefill"] = shared.compare(torch, whole[d:cm.num_actual_tokens], changed[d:cm.num_actual_tokens], p)
                    exact = row["patched_vs_manual_entire_storage"]
                    prefill = row["whole2d_vs_split_prefill"]
                    passed = (exact["finite"] and exact["bitwise_equal"] and prefill["finite"] and prefill["bitwise_equal"]
                              and row["whole2d_vs_split_decode"]["finite"] and row["returned_output_alias"]
                              and row["fast_decode_launches"] == 1)
                    row["status"] = "pass_wrapper_gate" if passed else "reject"
                    return row

                for index, (d, p, kv_len) in enumerate(CASES):
                    try:
                        row = mixed_case(d, p, kv_len, cross_stream=index == 1)
                    except Exception:
                        row = {"decode_requests": d, "prefill_tokens": p, "kv_len": kv_len,
                               "status": "reject_runtime_error", "error": traceback.format_exc()}
                    result["mixed_cases"].append(row)
                    checkpoint()
                    print(json.dumps(safe(row), allow_nan=False), flush=True)

                # Pure decode stays on original_forward; one real graph replay.
                data = make_data(torch, [1] * 8, 127)
                cm, q, k, v, cache = data
                impl.do_kv_cache_update(layer, k[:8], v[:8], cache, cm.slot_mapping)
                metadata = builder.build(0, cm)
                if hasattr(metadata, mixed._PLAN):
                    raise RuntimeError("pure decode unexpectedly received a split plan")
                reference, changed = torch.full_like(q, -999), torch.full_like(q, -999)
                invoke(original_forward, data, metadata, reference)
                invoke(patched_forward, data, metadata, changed)
                torch.cuda.synchronize()
                eager = shared.compare(torch, reference, changed, q.shape[0])
                stream = torch.cuda.Stream()
                stream.wait_stream(torch.cuda.current_stream())
                with torch.cuda.stream(stream):
                    invoke(patched_forward, data, metadata, changed)
                stream.synchronize()
                graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph, stream=stream):
                    invoke(patched_forward, data, metadata, changed)
                changed.fill_(-999)
                graph.replay()
                torch.cuda.synchronize()
                replay = shared.compare(torch, reference, changed, q.shape[0])
                result["pure_decode"] = {"no_split_plan": True, "graph_replays": 1,
                                         "eager": eager, "graph_replay": replay,
                                         "status": "pass" if all(c["finite"] and c["bitwise_equal"] for c in (eager, replay)) else "reject"}
                passed = (len(result["mixed_cases"]) == 4
                          and all(row["status"] == "pass_wrapper_gate" for row in result["mixed_cases"])
                          and result["pure_decode"]["status"] == "pass")
                result["status"] = "passed_synthetic_wrapper_gate" if passed else "completed_with_rejections"
                status = 0 if passed else 2
            except BaseException:
                result.update(status="failed", error=traceback.format_exc())
                print(result["error"], flush=True)
            finally:
                if torch is not None and torch.cuda.is_initialized():
                    try:
                        torch.cuda.synchronize()
                    except BaseException:
                        result.update(status="failed", shutdown_error=traceback.format_exc())
                        status = 1
                if monitor is not None:
                    try:
                        monitor.terminate()
                        monitor.wait(timeout=10)
                    except BaseException:
                        result.update(status="failed", monitor_error=traceback.format_exc())
                        status = 1
                if monitor_log is not None:
                    monitor_log.close()
                manifest.update(finished_utc=validator.utc(), exit_code=status)
                checkpoint()
                (run / "exit-code").write_text(str(status) + "\n", encoding="utf-8")
                (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n", encoding="utf-8")
                if lock is not None:
                    lock.close()
    print(json.dumps({"status": result["status"], "run_dir": str(run), "exit_code": status}), flush=True)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
