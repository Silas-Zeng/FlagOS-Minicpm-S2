#!/usr/bin/env python3
"""Two-case, no-weight token-bucket CUDA gate; no service, profile or timings.

Uses the actual Triton Builder/Impl/KV writer and reviewed C2+C3 wrappers.
The row-padding wrapper runs on a small harness with real CUDA buffers; this
does not instantiate ModelRunnerFL or prove its full input-prep lifecycle.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import traceback
from types import SimpleNamespace as NS


EXPECTED_BUCKET = "d2620ff750beb3fab97f372d64a1ec0e5550ee133cc6ca33adb8ba3f43de4605"
CASES = ((259, 384), (952, 1024))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--runtime-path", type=Path, required=True)
    parser.add_argument("--mixed-path", type=Path, required=True)
    parser.add_argument("--bucket-path", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    args = parser.parse_args()
    # --help and py_compile are CPU-only, including on Windows.
    import fcntl
    import bench_attention_dispatch as shared
    import validate_block_table_candidate as owner
    import validate_mixed_decode as previous

    root, run = owner.ROOT.resolve(), args.run_dir.resolve()
    if not run.is_relative_to(root) or run == root:
        raise ValueError("new run directory must be inside experiment workspace")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {"started_utc": owner.utc(), "pid": os.getpid(), "run_dir": str(run),
                "command": [sys.executable, *sys.argv],
                "command_shell": shlex.join([sys.executable, *sys.argv]),
                "kind": "synthetic two-case CUDA row/KV isolation gate; no weights/service/timings"}
    manifest["environment"] = {key: os.environ[key] for key in (
        "VLLM_PLUGINS", "PYTHONPATH", "CUDA_VISIBLE_DEVICES", "IX_VISIBLE_DEVICES",
        "COREX_VISIBLE_DEVICES", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "TRITON_CACHE_DIR",
        "USE_FLAGTUNE") if key in os.environ}
    result = {"status": "started", "cases": [], "accuracy": "not evaluated",
              "performance": "not evaluated", "limitations": [
                  "Actual one-layer Builder/Impl/KV writer; synthetic QKV and a small padding harness.",
                  "Does not instantiate ModelRunnerFL or validate its full H2D/event lifecycle.",
                  "No full-model GEMM/hidden/logits/LM-head/sampler equivalence or accuracy claim.",
                  "Only the padding operations' RNG state is checked, not a real sampling invocation."]}
    lock, monitor, monitor_log, torch = None, None, None, None
    status = 1

    def checkpoint():
        previous.write_json(run / "manifest.json", manifest)
        previous.write_json(run / "results.json", result)

    checkpoint()
    with (run / "gate.log").open("x", encoding="utf-8") as log:
        with contextlib.redirect_stdout(previous.Tee(sys.stdout, log)), contextlib.redirect_stderr(previous.Tee(sys.stderr, log)):
            try:
                lock = (root / "framework-device.lock").open("a")
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                manifest["preflight"] = owner.preflight(args.ixsmi)
                source = run / "source"
                source.mkdir()
                for label, path in (("gate.py", Path(__file__)), ("runtime.py", args.runtime_path),
                                    ("mixed.py", args.mixed_path), ("bucket.py", args.bucket_path),
                                    ("validate_mixed_decode.py", Path(previous.__file__)),
                                    ("bench_attention_dispatch.py", Path(shared.__file__)),
                                    ("validate_block_table_candidate.py", Path(owner.__file__)),
                                    ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh")):
                    (source / label).write_bytes(path.read_bytes())
                for label, expected in (("runtime.py", previous.EXPECTED_RUNTIME),
                                        ("mixed.py", previous.EXPECTED_CANDIDATE),
                                        ("bucket.py", EXPECTED_BUCKET)):
                    if previous.digest(source / label) != expected:
                        raise RuntimeError(f"unaudited candidate: {label}")
                manifest["source_sha256"] = {p.name: previous.digest(p) for p in source.iterdir()}
                checkpoint()
                import torch
                import vllm.envs as envs
                import vllm.v1.attention.backends.triton_attn as backend
                import vllm.v1.attention.ops.triton_reshape_and_cache_flash as writer
                from vllm.config import CompilationConfig, CUDAGraphMode
                from vllm.engine.arg_utils import EngineArgs
                from vllm.forward_context import BatchDescriptor
                from vllm.v1.kv_cache_interface import FullAttentionSpec

                config = EngineArgs(model=str(args.model), served_model_name=["minicpm"],
                                    gpu_memory_utilization=0.85, max_model_len=131072,
                                    compilation_config=CompilationConfig(
                                        cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
                runtime = shared.load("biv150_bucket_gate_runtime", source / "runtime.py")
                mixed = shared.load("biv150_bucket_gate_mixed", source / "mixed.py")
                bucket = shared.load("biv150_bucket_gate_bucket", source / "bucket.py")
                bucket._require_source(backend, bucket.EXPECTED_BACKEND_SHA256)
                bucket._require_source(writer, bucket.EXPECTED_KV_WRITER_SHA256)
                if backend.triton_reshape_and_cache_flash is not writer.triton_reshape_and_cache_flash:
                    raise RuntimeError("actual cache-writer binding changed")
                manifest["runtime_install"] = runtime.install()
                manifest["mixed_install"] = mixed.install()
                attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
                helpers = importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
                for label, module in (("backend.py", backend), ("writer.py", writer),
                                      ("attention.py", attention), ("helpers.py", helpers)):
                    (source / label).write_bytes(Path(module.__file__).read_bytes())
                (source / "model-config.json").write_bytes((args.model / "config.json").read_bytes())
                manifest["source_sha256"] = {p.name: previous.digest(p) for p in source.iterdir()}
                manifest["packages"] = {}
                for name in ("torch", "vllm", "vllm-plugin-fl", "flag-gems"):
                    try:
                        manifest["packages"][name] = importlib.metadata.version(name)
                    except importlib.metadata.PackageNotFoundError:
                        manifest["packages"][name] = "unavailable distribution metadata"
                if torch.cuda.device_count() != 1:
                    raise RuntimeError("expected exactly one visible accelerator")
                torch.cuda.set_device(0)
                torch.manual_seed(721401)
                manifest["device"] = str(torch.cuda.get_device_properties(0))
                manifest["parsed_config"] = {
                    "model": str(config.model_config.model), "dtype": str(config.model_config.dtype),
                    "cudagraph_mode": str(config.compilation_config.cudagraph_mode),
                    "max_num_batched_tokens": config.scheduler_config.max_num_batched_tokens,
                    "max_num_seqs": config.scheduler_config.max_num_seqs}
                monitor_log = (run / "monitor.log").open("x")
                monitor = subprocess.Popen(["bash", str(source / "monitor_gpu.sh"),
                                            str(os.getpid()), str(run / "gpu.csv")],
                                           stdout=monitor_log, stderr=subprocess.STDOUT)
                manifest["monitor_pid"] = monitor.pid
                spec = FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=128, dtype=torch.bfloat16)
                builder = backend.TritonAttentionMetadataBuilder(
                    spec, ["synthetic.attn"], config, torch.device("cuda:0"))
                impl = backend.TritonAttentionImpl(
                    num_heads=16, head_size=128, scale=128 ** -0.5, num_kv_heads=2,
                    alibi_slopes=None, sliding_window=None, kv_cache_dtype="auto",
                    attn_type=backend.AttentionType.DECODER)
                layer = NS(_q_scale=torch.ones((), device="cuda"),
                           _k_scale=torch.ones((), device="cuda"),
                           _v_scale=torch.ones((), device="cuda"))
                if not mixed._builder_eligible(builder, backend, torch):
                    raise RuntimeError("actual configuration excluded; no synthetic config override")

                class Harness:
                    def __init__(self):
                        self.vllm_config, self.device = config, torch.device("cuda:0")
                        self.is_pooling_model = self.supports_mm_inputs = self.enable_prompt_embeds = False
                        self.uses_mrope = self.use_aux_hidden_state_outputs = self.broadcast_pp_output = False
                        self.uses_xdrope_dim, self.uniform_decode_query_len = 0, 1
                        self.calculate_kv_scales = False
                        self.cross_layers_kv_cache = self.cross_layers_attn_backend = None
                        self.shared_kv_cache_layers = {}
                        self.attn_groups = [[NS(backend=backend.TritonAttentionBackend)]]
                        self.max_num_tokens = config.scheduler_config.max_num_batched_tokens
                        self.input_ids = NS(gpu=torch.full((self.max_num_tokens,), 130577,
                                                          dtype=torch.int32, device=self.device))
                        self.positions = torch.full((self.max_num_tokens,), 999999999999,
                                                    dtype=torch.int64, device=self.device)

                    def _determine_batch_execution_and_padding(self, count, n, lengths, max_query,
                                                              cascade, **kwargs):
                        return CUDAGraphMode.NONE, BatchDescriptor(num_tokens=count, num_reqs=n, uniform=False), False, None, None

                    def _preprocess(self, scheduler, count, intermediate_tensors=None):
                        self.positions[scheduler.total_num_scheduled_tokens:count].zero_()
                        return self.input_ids.gpu[:count], None, self.positions[:count], None, {}, None

                    def execute_model(self, scheduler, intermediate_tensors=None):
                        dispatched = self._determine_batch_execution_and_padding(
                            scheduler.total_num_scheduled_tokens, 32, None, scheduler.max_query, False)
                        return dispatched, self._preprocess(scheduler, dispatched[1].num_tokens)

                api = NS(CUDAGraphMode=CUDAGraphMode, envs=envs,
                         has_kv_transfer_group=lambda: False, has_ec_transfer=lambda: False)
                bucket._wrap_runner(Harness, api, backend, torch)
                checkpoint()
                for actual, padded in CASES:
                    row = {"actual": actual, "padded": padded, "requests": 32,
                           "decode_prefix": 31, "prefill_tokens": actual - 31, "status": "started"}
                    result["cases"].append(row)
                    checkpoint()
                    harness = Harness()
                    if not bucket._eligible(harness, api, backend, torch):
                        raise RuntimeError("actual config/device scope excluded the harness")
                    ids = torch.arange(actual, dtype=torch.int32, device="cuda") % 127
                    harness.input_ids.gpu[:actual].copy_(ids)
                    harness.positions[:actual].copy_(torch.arange(actual, device="cuda"))
                    scheduler = NS(total_num_scheduled_tokens=actual, max_query=actual - 31,
                                   scheduled_encoder_inputs={}, scheduled_spec_decode_tokens={})
                    rng = torch.cuda.get_rng_state()
                    dispatched, prepared = harness.execute_model(scheduler)
                    assert dispatched[1].num_tokens == padded
                    assert torch.equal(rng, torch.cuda.get_rng_state())
                    assert torch.equal(prepared[0][:actual], ids)
                    assert not bool(prepared[0][actual:].any())
                    assert not bool(prepared[2][actual:].any())
                    # A tiny synthetic embedding would reject the poisoned IDs
                    # if the actual candidate's same-stream tail zero failed.
                    torch.nn.functional.embedding(prepared[0].long(), torch.zeros((128, 8), device="cuda"))
                    common, q, k, v, cache = previous.make_data(torch, [1] * 31 + [actual - 31], 1023)
                    reference_cache, changed_cache = cache.clone(), cache.clone()
                    qp = torch.full((padded, 16, 128), float("nan"), dtype=q.dtype, device="cuda")
                    kp = torch.full((padded, 2, 128), float("nan"), dtype=k.dtype, device="cuda")
                    vp = torch.full_like(kp, float("nan"))
                    qp[:actual].copy_(q[:actual]); kp[:actual].copy_(k[:actual]); vp[:actual].copy_(v[:actual])
                    slots = torch.full((padded,), -1, dtype=torch.int64, device="cuda")
                    slots[:actual].copy_(common.slot_mapping)
                    padded_common = NS(**{**vars(common), "slot_mapping": slots})
                    impl.do_kv_cache_update(layer, k[:actual], v[:actual], reference_cache, common.slot_mapping)
                    impl.do_kv_cache_update(layer, kp, vp, changed_cache, slots)
                    md, mdp = builder.build(0, common), builder.build(0, padded_common)
                    assert mdp.num_actual_tokens == actual and mdp.query_start_loc.shape[0] == 33
                    assert getattr(mdp, mixed._PLAN, None) is not None
                    expected, changed = torch.empty_like(q[:actual]), torch.full_like(qp, float("nan"))
                    impl.forward(layer, q[:actual], k[:actual], v[:actual], reference_cache, md, expected)
                    impl.forward(layer, qp, kp, vp, changed_cache, mdp, changed)
                    torch.cuda.synchronize()
                    row["attention"] = shared.compare(torch, expected, changed, actual)
                    row["kv_bitwise_equal"] = torch.equal(reference_cache, changed_cache)
                    row["out_tail_stays_poisoned"] = bool(torch.isnan(changed[actual:]).all())
                    assert row["attention"]["finite"] and row["attention"]["bitwise_equal"]
                    assert row["kv_bitwise_equal"] and row["out_tail_stays_poisoned"]
                    # One subsequent real decode per request reuses the caches
                    # and poisoned backing buffers, with no padding authorized.
                    next_common, nq, nk, nv, _ = previous.make_data(torch, [1] * 32, 1024)
                    harness.input_ids.gpu[:32].fill_(3)
                    harness.positions[:32].fill_(1023)
                    next_scheduler = NS(total_num_scheduled_tokens=32, max_query=1,
                                        scheduled_encoder_inputs={}, scheduled_spec_decode_tokens={})
                    next_dispatch, _ = harness.execute_model(next_scheduler)
                    assert next_dispatch[1].num_tokens == 32
                    qp[:32].copy_(nq[:32]); kp[:32].copy_(nk[:32]); vp[:32].copy_(nv[:32])
                    impl.do_kv_cache_update(layer, nk[:32], nv[:32], reference_cache, next_common.slot_mapping)
                    impl.do_kv_cache_update(layer, kp, vp, changed_cache, next_common.slot_mapping)
                    next_md = builder.build(0, next_common)
                    next_expected = torch.empty_like(nq[:32])
                    untouched_tail = changed[32:].clone()
                    impl.forward(layer, nq[:32], nk[:32], nv[:32], reference_cache, next_md, next_expected)
                    impl.forward(layer, qp, kp, vp, changed_cache, next_md, changed)
                    torch.cuda.synchronize()
                    row["next_decode"] = shared.compare(torch, next_expected, changed, 32)
                    row["next_kv_bitwise_equal"] = torch.equal(reference_cache, changed_cache)
                    torch.testing.assert_close(changed[32:], untouched_tail, rtol=0, atol=0, equal_nan=True)
                    assert row["next_decode"]["finite"] and row["next_decode"]["bitwise_equal"]
                    assert row["next_kv_bitwise_equal"] and bucket._EXECUTION.get() is None
                    row.update(status="pass", padding_only_rng_unchanged=True, next_unused_output_untouched=True)
                    checkpoint()
                    print(json.dumps(row), flush=True)
                result["status"], status = "passed_synthetic_row_kv_gate", 0
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
                manifest.update(finished_utc=owner.utc(), exit_code=status)
                checkpoint()
                (run / "exit-code").write_text(str(status) + "\n", encoding="utf-8")
                (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n", encoding="utf-8")
                if lock is not None:
                    lock.close()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
