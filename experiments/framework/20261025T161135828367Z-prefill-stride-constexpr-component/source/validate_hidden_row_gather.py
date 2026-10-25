#!/usr/bin/env python3
"""Owned no-weight BF16 row-copy correctness gate; no service or speed claim.

The controller imports no accelerator runtime. One child owns its CUDA context;
pre/postflight, exact source snapshots and original stdout are preserved.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import signal
import shlex
import subprocess
import sys
import traceback
from types import SimpleNamespace as NS


EXPECTED_RUNNER = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
EXPECTED_RUNTIME = "109905b3d276d6e4ff6cc74a7b97dfe6e8ee31a517b0ac7c4fdb163cc37ad8fd"
EXPECTED_TRANSFORM = "881f2cf209da11842577aab01cca3830e985ad7c9030554156757a5de7e791f2"
EXPECTED_PATCHED = "e68d6886d788a2f56d470fccaee62558d4622545eede2a59fbeb083a5264016e"


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def runner_fixture(torch, np, count, lengths):
    text = NS(architectures=["LlamaForCausalLM"], hidden_size=2048, intermediate_size=6144,
              num_hidden_layers=42, num_attention_heads=16, num_key_value_heads=2)
    model = NS(model="/workspace/MiniCPM5-2B", dtype=torch.bfloat16, quantization=None,
               hf_text_config=text, is_encoder_decoder=False)
    parallel = NS(tensor_parallel_size=1, pipeline_parallel_size=1, data_parallel_size=1,
                  decode_context_parallel_size=1, use_ubatching=False)
    config = NS(model_config=model, parallel_config=parallel, speculative_config=None,
                lora_config=None, cache_config=NS(kv_sharing_fast_prefill=False),
                compilation_config=NS(pass_config=NS(enable_sp=False)))
    return NS(vllm_config=config, is_pooling_model=False, supports_mm_inputs=False,
              enable_prompt_embeds=False, use_aux_hidden_state_outputs=False, broadcast_pp_output=False,
              uses_mrope=False, uses_xdrope_dim=0, num_spec_tokens=0, use_async_spec_decode=False,
              _draft_token_ids=None, max_num_tokens=2048, device=torch.device("cuda:0"),
              input_batch=NS(num_reqs=count),
              query_start_loc=NS(np=np.r_[np.int32(0), np.cumsum(lengths, dtype=np.int32)]))


def worker(run):
    import numpy as np
    import torch
    from validate_async_token_update import cache_snapshot

    result = {"status": "started", "cases": [], "accuracy": "not evaluated", "performance": "not evaluated",
              "limitations": ["Fixture config, not a constructed full ModelRunnerFL.",
                              "CPU bit pattern reference; no weights, LM-head, sampling or end-to-end timing.",
                              "Source/query-end proof assumes the exact non-spec runner indices construction."]}
    try:
        runtime = load("hidden_row_runtime", run / "source/runtime.py")
        result["runtime_versions"] = {"torch": torch.__version__, "triton": runtime.triton.__version__}
        properties = torch.cuda.get_device_properties(0)
        result["device"] = {name: getattr(properties, name, None) for name in (
            "name", "total_memory", "multi_processor_count", "warp_size")}
        source = torch.empty((2048, 2048), dtype=torch.bfloat16, device="cuda")
        indices = torch.empty((64,), dtype=torch.int32, device="cuda")
        caches = []
        for ordinal, (rows, total, count) in enumerate(((259, 259, 29), (952, 952, 16),
                                                       (2048, 2048, 64), (64, 62, 62))):
            lengths = np.array([1] * (count - 1) + [total - count + 1], dtype=np.int32)
            ends = np.cumsum(lengths, dtype=np.int64) - 1
            runner = runner_fixture(torch, np, count, lengths)
            # Covers all BF16 payloads, including NaN, infinities and signed zero.
            bits = ((torch.arange(rows * 2048, dtype=torch.int32) + ordinal * 31) % 65536).to(torch.int16).reshape(rows, 2048)
            source[:rows].copy_(bits.view(torch.bfloat16))
            indices[:count].copy_(torch.tensor(ends, dtype=torch.int32))
            cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
            out = runtime.try_gather_hidden_rows(runner, source[:rows], indices[:count], lengths)
            torch.cuda.synchronize()
            expected = bits[torch.tensor(ends, dtype=torch.int64)]
            checks = {"selected": out is not None,
                      "entire_bits_equal": out is not None and torch.equal(out.cpu().view(torch.int16), expected),
                      "shape": out is not None and tuple(out.shape) == (count, 2048),
                      "fresh_storage": out is not None and out.untyped_storage().data_ptr() not in
                          (source.untyped_storage().data_ptr(), indices.untyped_storage().data_ptr()),
                      "rng_unchanged": torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state())}
            cache = cache_snapshot(runtime._copy_hidden_rows)
            caches.append(cache)
            result["cases"].append({"rows": rows, "total_real_tokens": total, "count": count,
                                    "checks": checks, "kernel_cache": cache})
            if not all(checks.values()):
                raise AssertionError("runtime-bound BF16 copy differs: " + str(checks))
        available = all(x["status"] == "available" for x in caches)
        result["dynamic_specialization"] = {
            "available": available,
            "stable": available and len({json.dumps(x["devices"], sort_keys=True) for x in caches}) == 1,
            "scope": "same addresses/dtypes/strides; only actual M and N change"}

        # A second supported dtype; cached entry count may grow for the dtype.
        lengths = np.array([1, 2, 256], dtype=np.int32)
        runner = runner_fixture(torch, np, 3, lengths)
        idx64 = torch.tensor([0, 2, 258], dtype=torch.int64, device="cuda")
        out64 = runtime.try_gather_hidden_rows(runner, source[:259], idx64, lengths)
        assert out64 is not None
        assert torch.equal(out64.cpu().view(torch.int16), source[:259].cpu().view(torch.int16)[[0, 2, 258]])
        result["int64_indices_bits_equal"] = True

        fallback = {}
        for label, hidden, ix in (
            ("cpu", source[:259].cpu(), idx64.cpu()),
            ("wrong_dtype", source[:259].to(torch.float16), idx64),
            ("wrong_width", source[:259, :1024], idx64),
            ("row_stride", source[:518:2], idx64),
            ("index_stride", torch.empty((259, 2048), dtype=torch.bfloat16, device="cuda"),
             torch.tensor([0, 99, 2, 99, 258, 99], dtype=torch.int64, device="cuda")[::2]),
            ("aliased_storage", source[:259], source.view(torch.int32).flatten()[:3])):
            fallback[label] = runtime.try_gather_hidden_rows(runner, hidden, ix, lengths) is None
        malformed = lengths.copy()
        malformed[0] = 0
        fallback["invalid_cpu_proof"] = runtime.try_gather_hidden_rows(runner, source[:259], idx64, malformed) is None
        config_spec = runner.vllm_config.speculative_config
        runner.vllm_config.speculative_config = object()
        fallback["spec"] = runtime.try_gather_hidden_rows(runner, source[:259], idx64, lengths) is None
        runner.vllm_config.speculative_config = config_spec
        assert all(fallback.values()), fallback
        result["fallbacks"] = fallback

        # Private copy semantics only: repeated, reordered and valid negative rows.
        arbitrary = [0, -1, 0, 258, 1, -259]
        ix = torch.tensor(arbitrary, dtype=torch.int32, device="cuda")
        private_out = torch.empty((6, 2048), dtype=torch.bfloat16, device="cuda")
        runtime._copy_hidden_rows[(6,)](source[:259], ix, private_out, 259, 6,
                                       WIDTH=2048, num_warps=2, num_stages=1)
        assert torch.equal(private_out.cpu().view(torch.int16), source[:259].cpu().view(torch.int16)[arbitrary])
        result["private_negative_duplicate_reordered_copy"] = "bitwise pass; public seam remains query-end only"

        producer, consumer = torch.cuda.Stream(), torch.cuda.Stream()
        producer.wait_stream(torch.cuda.current_stream())
        expected = torch.arange(259 * 2048, dtype=torch.int32).to(torch.int16).reshape(259, 2048)
        with torch.cuda.stream(producer):
            cross_hidden = expected.view(torch.bfloat16).to("cuda")
            cross_indices = torch.tensor([0, 2, 258], dtype=torch.int64, device="cuda")
        consumer.wait_stream(producer)
        with torch.cuda.stream(consumer):
            cross_out = runtime.try_gather_hidden_rows(runner, cross_hidden, cross_indices, lengths)
        del cross_hidden, cross_indices
        consumer.synchronize()
        assert torch.equal(cross_out.cpu().view(torch.int16), expected[[0, 2, 258]])
        result["cross_stream"] = "bitwise pass; producer readiness explicit, allocator record_stream in candidate"
        result["selected_launches"] = runtime.selected_launches
        result["copy_correctness"] = "pass"
        result["status"] = ("pass" if result["dynamic_specialization"]["stable"]
                            else "reject_specialization" if available
                            else "inconclusive_specialization")
    except BaseException:
        result["status"] = "reject"
        result["error"] = traceback.format_exc()
        traceback.print_exc()
    write(run / "results.json", result)
    return 0 if result["status"] == "pass" else 2 if result["status"] == "inconclusive_specialization" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--runtime-path", type=Path)
    parser.add_argument("--transform-path", type=Path)
    parser.add_argument("--runner-path", type=Path)
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir)
    if any(path is None for path in (args.runtime_path, args.transform_path, args.runner_path)):
        parser.error("controller requires runtime, transform and exact original runner paths")
    import fcntl
    import validate_block_table_candidate as owner
    from validate_async_token_update import cache_snapshot

    root, run = owner.ROOT.resolve(), args.run_dir.resolve()
    if not run.is_relative_to(root) or run == root:
        raise ValueError("run must be a new child of experiment root")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {"started_utc": utc(), "pid": os.getpid(), "command": [sys.executable, *sys.argv],
                "command_shell": shlex.join([sys.executable, *sys.argv]),
                "kind": "synthetic BF16 final-hidden row copy; no weights/service/performance score",
                "environment": {key: os.environ[key] for key in (
                    "VLLM_PLUGINS", "PYTHONPATH", "CUDA_VISIBLE_DEVICES", "IX_VISIBLE_DEVICES",
                    "COREX_VISIBLE_DEVICES", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "TRITON_CACHE_DIR") if key in os.environ}}
    lock, child, monitor, monitor_log = None, None, None, None
    status = 1
    def interrupted(signum, frame):
        raise SystemExit(f"controller interrupted by signal {signum}")
    signal.signal(signal.SIGTERM, interrupted)
    try:
        lock = (root / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest["preflight"] = owner.preflight(args.ixsmi)
        pre_gpu = subprocess.check_output([args.ixsmi], text=True, timeout=10)
        (run / "preflight-ixsmi.txt").write_text(pre_gpu, encoding="utf-8")
        if "No running processes found" not in pre_gpu:
            raise RuntimeError("accelerator has a process; no second device experiment allowed")
        source = run / "source"
        source.mkdir()
        for label, path in (("gate.py", Path(__file__)), ("runtime.py", args.runtime_path),
                            ("transform.py", args.transform_path), ("runner.py", args.runner_path),
                            ("validate_block_table_candidate.py", Path(owner.__file__)),
                            ("validate_async_token_update.py", Path(sys.modules[cache_snapshot.__module__].__file__)),
                            ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh")):
            (source / label).write_bytes(path.read_bytes())
        for label, expected in (("runner.py", EXPECTED_RUNNER), ("runtime.py", EXPECTED_RUNTIME),
                                ("transform.py", EXPECTED_TRANSFORM)):
            if digest(source / label) != expected:
                raise RuntimeError("unaudited source: " + label)
        transform = load("hidden_row_transform", source / "transform.py")
        transformed = transform.transform_source((source / "runner.py").read_bytes())
        compile(transformed, "isolated:transformed-runner", "exec")
        (source / "runner-transformed.py").write_bytes(transformed)
        if digest(source / "runner-transformed.py") != EXPECTED_PATCHED:
            raise RuntimeError("transformed runner differs from reviewed candidate")
        manifest["source_sha256"] = {path.name: digest(path) for path in source.iterdir() if path.is_file()}
        manifest["packages"] = {}
        for package in ("torch", "vllm", "FlagGems", "numpy", "SQLAlchemy", "flagtree"):
            try:
                manifest["packages"][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][package] = "unavailable"
        write(run / "manifest.json", manifest)
        with (run / "worker.log").open("x") as log:
            manifest["worker_command"] = [sys.executable, str(source / "gate.py"), "--worker", "--run-dir", str(run)]
            child = subprocess.Popen(manifest["worker_command"],
                                     stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            manifest["worker_pid"] = child.pid
            monitor_log = (run / "gpu-monitor-launcher.log").open("x")
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
                    manifest["cleanup_error"] = traceback.format_exc()
                    status = 1
        if monitor_log is not None:
            monitor_log.close()
        if child is not None and child.poll() is not None:
            try:
                manifest["postflight"] = owner.preflight(args.ixsmi)
                post_gpu = subprocess.check_output([args.ixsmi], text=True, timeout=10)
                (run / "postflight-ixsmi.txt").write_text(post_gpu, encoding="utf-8")
                if "No running processes found" not in post_gpu:
                    raise RuntimeError("accelerator process remains after owned child exit")
            except BaseException:
                manifest["postflight_error"] = traceback.format_exc()
                status = 1
        manifest.update(finished_utc=utc(), exit_code=status)
        write(run / "manifest.json", manifest)
        (run / "exit-code").write_text(str(status) + "\n", encoding="utf-8")
        (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n", encoding="utf-8")
        if lock is not None:
            lock.close()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
