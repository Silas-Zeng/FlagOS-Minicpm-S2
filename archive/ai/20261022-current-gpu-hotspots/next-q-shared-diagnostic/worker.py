#!/usr/bin/env python3
"""只运行原 C2/C3 Attention；硬件指标诊断，不产生吞吐或候选收益结论。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import sys
import time
import traceback
from types import SimpleNamespace as NS

LOOPS, WARMUP = 128, 8
EXPECTED_RUNNER = "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141"
EXPECTED_MODEL = "59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180"
EXPECTED = {
    "runtime.py": "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f",
    "mixed.py": "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42",
}
MODULES = {
    "backend": ("vllm.v1.attention.backends.triton_attn", "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605"),
    "attention": ("vllm.v1.attention.ops.triton_unified_attention", "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"),
    "helpers": ("vllm.v1.attention.ops.triton_attention_helpers", "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"),
    "writer": ("vllm.v1.attention.ops.triton_reshape_and_cache_flash", "f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb"),
}


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def scalar(value):
    return value if isinstance(value, (str, int, float, bool, type(None))) else str(value)


class Capture:
    """仅一次 warmup 观察；原 launch 恰一次、args/kwargs/返回/异常不变。"""
    def __init__(self, original, name):
        self.original, self.name, self.observed = original, name, []

    def __getattr__(self, name):
        return getattr(self.original, name)

    def __getitem__(self, grid):
        launch = self.original[grid]
        def invoke(*args, **kwargs):
            compiled = launch(*args, **kwargs)
            meta = compiled.metadata
            raw_meta = meta if isinstance(meta, dict) else (meta._asdict() if hasattr(meta, "_asdict") else vars(meta))
            self.observed.append({
                "name": self.name, "hash": compiled.hash,
                "n_regs": compiled.n_regs, "n_spills": compiled.n_spills,
                "metadata": {key: scalar(value) for key, value in raw_meta.items()},
                "launch": {key: kwargs.get(key) for key in ("IS_3D", "BLOCK_M", "BLOCK_Q", "TILE_SIZE", "NUM_SEGMENTS_PER_SEQ", "num_warps", "num_stages")},
                "grid": list(grid) if isinstance(grid, tuple) else str(grid),
                "asm_sha256": {key: hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()
                               for key, value in compiled.asm.items() if isinstance(value, (str, bytes))},
            })
            return compiled
        return invoke


def worker(run, model):
    source = run / "source"
    result = {"status": "started", "kind": "baseline-only synthetic Attention hardware diagnostic",
              "started_utc": utc(), "worker_pid": os.getpid(), "calls": LOOPS, "warmup_calls": WARMUP,
              "command": [sys.executable, *sys.argv], "command_shell": shlex.join([sys.executable, *sys.argv]),
              "environment": {key: os.environ[key] for key in (
                  "VLLM_PLUGINS", "PYTHONPATH", "CUDA_VISIBLE_DEVICES", "IX_VISIBLE_DEVICES", "COREX_VISIBLE_DEVICES",
                  "OMP_NUM_THREADS", "MKL_NUM_THREADS", "TRITON_CACHE_DIR", "USE_FLAGTUNE") if key in os.environ},
              "limitations": ["Synthetic D1/P2047 KV16K, original C2/C3, no model weights/service/accuracy/throughput.",
                              "Repeated identical Q and cached KV; warm-cache hardware observation, not the full serving workload.",
                              "Profiler/metrics affect execution. UTC and wall boundaries locate the trace, not a performance measurement.",
                              "No GEMM and no DB-equivalence claim; no candidate loaded or installed."],
              "profile": {}, "compiled": []}
    torch, attention, backend = None, None, None
    preinstall, baseline, profile_pending = None, None, False
    try:
        for name, expected in EXPECTED.items():
            if digest(source / name) != expected:
                raise RuntimeError("unreviewed baseline asset: " + name)
        manifest = json.loads((source / "asset-pins.json").read_text(encoding="utf-8"))
        for name in ("worker.py", "fixture.py"):
            if digest(source / name) != manifest[name]:
                raise RuntimeError("diagnostic asset drift: " + name)
        fixture = load("q_shared_fixture", source / "fixture.py")
        base = Path(os.environ["PYTHONPATH"].split(os.pathsep)[0]) / "vllm_fl/worker/model_runner.py"
        if digest(base) != EXPECTED_RUNNER or digest(model / "config.json") != EXPECTED_MODEL:
            raise RuntimeError("exact combined runner/model required")
        import torch
        from vllm.config import CompilationConfig, CUDAGraphMode
        from vllm.engine.arg_utils import EngineArgs
        from vllm.v1.kv_cache_interface import FullAttentionSpec
        modules = {}
        for name, (qualified, expected) in MODULES.items():
            module = importlib.import_module(qualified)
            if digest(module.__file__) != expected:
                raise RuntimeError("installed baseline drift: " + qualified)
            modules[name] = module
            (source / (name + ".py")).write_bytes(Path(module.__file__).read_bytes())
        backend, attention, writer = modules["backend"], modules["attention"], modules["writer"]
        if backend.triton_reshape_and_cache_flash is not writer.triton_reshape_and_cache_flash:
            raise RuntimeError("actual KV writer binding changed")
        preinstall = (attention.kernel_unified_attention, attention.reduce_segments,
                      backend.TritonAttentionMetadataBuilder.build, backend.TritonAttentionImpl.forward)
        c2 = load("q_shared_c2", source / "runtime.py")
        c3 = load("q_shared_c3", source / "mixed.py")
        result["c2_install"], result["c3_install"] = c2.install(), c3.install()
        baseline = (attention.kernel_unified_attention, attention.reduce_segments,
                    backend.TritonAttentionMetadataBuilder.build, backend.TritonAttentionImpl.forward)
        config = EngineArgs(model=str(model), served_model_name=["minicpm"], gpu_memory_utilization=0.85,
                            max_model_len=131072, compilation_config=CompilationConfig(
                                cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
        (source / "model-config.json").write_bytes((model / "config.json").read_bytes())
        if torch.cuda.device_count() != 1:
            raise RuntimeError("one accelerator required")
        torch.cuda.set_device(0)
        torch.manual_seed(721502)
        result.update(device=str(torch.cuda.get_device_properties(0)), torch_version=torch.__version__,
                      torch_num_threads=torch.get_num_threads(), fixture={"lengths": [1, 2047], "kv_len": 16384,
                      "random_physical_pages": True, "shared_old_prefix_blocks": 16, "negative_padding_slots": 3})
        spec = FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=128, dtype=torch.bfloat16)
        builder = backend.TritonAttentionMetadataBuilder(spec, ["synthetic.attn"], config, torch.device("cuda:0"))
        impl = backend.TritonAttentionImpl(num_heads=16, head_size=128, scale=128 ** -0.5, num_kv_heads=2,
                                         alibi_slopes=None, sliding_window=None, kv_cache_dtype="auto",
                                         attn_type=backend.AttentionType.DECODER)
        layer = NS(_q_scale=torch.full((), 0.75, device="cuda"), _k_scale=torch.full((), 1.25, device="cuda"),
                   _v_scale=torch.full((), 0.5, device="cuda"))
        common, q, k, v, cache = fixture.make_data(torch, [1, 2047], 16384)
        fixture.prepare_pages(torch, common, k, v, 16384)
        total = common.num_actual_tokens
        q[total:] = float("nan")
        metadata = builder.build(0, common)
        plan = getattr(metadata, c3._PLAN, None)
        if plan is None or plan.prefix_tokens != 1 or plan.prefill.num_actual_tokens != 2047:
            raise RuntimeError("actual C3 D1/P2047 plan required")
        impl.do_kv_cache_update(layer, k, v, cache, common.slot_mapping)
        before_cache = cache.clone()
        cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
        output = torch.full_like(q, -17)
        observers = (Capture(baseline[0], "attention"), Capture(baseline[1], "reducer"))
        try:
            attention.kernel_unified_attention, attention.reduce_segments = observers
            impl.forward(layer, q, k, v, cache, metadata, output)
            torch.cuda.synchronize()
        finally:
            attention.kernel_unified_attention, attention.reduce_segments = baseline[:2]
        result["compiled"] = [record for observer in observers for record in observer.observed]
        selected = [row["launch"]["IS_3D"] for row in result["compiled"] if row["name"] == "attention"]
        if selected != [True, False] or len(observers[1].observed) != 1:
            raise RuntimeError("expected one original 3D, reducer and 2D launch")
        for _ in range(WARMUP - 1):
            impl.forward(layer, q, k, v, cache, metadata, output)
        torch.cuda.synchronize()
        reference = output.clone()
        torch.cuda.synchronize()
        result["observer_restored_before_profile"] = (attention.kernel_unified_attention is baseline[0]
                                                     and attention.reduce_segments is baseline[1]
                                                     and backend.TritonAttentionImpl.forward is baseline[3])
        if not result["observer_restored_before_profile"]:
            raise RuntimeError("observer still active")
        result["profile"]["start_utc"] = utc()
        result["profile"]["start_perf_counter_ns"] = time.perf_counter_ns()
        write(run / "results.json", result)
        profile_pending = True
        torch.cuda.profiler.start()
        result["profile"]["start_returned"] = True
        for _ in range(LOOPS):
            impl.forward(layer, q, k, v, cache, metadata, output)
        torch.cuda.synchronize()
        torch.cuda.profiler.stop()
        profile_pending = False
        result["profile"].update(stop_returned=True, end_utc=utc(), end_perf_counter_ns=time.perf_counter_ns(),
                                 completed_calls=LOOPS)
        checks = {"entire_kv_bits_unchanged": bool(torch.equal(before_cache.view(torch.int16), cache.view(torch.int16))),
                  "rng_unchanged": bool(torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state())),
                  "valid_output_finite": bool(torch.isfinite(output[:total]).all()),
                  "padding_untouched": bool((output[total:] == -17).all()),
                  "same_q_repeat_output_bits": bool(torch.equal(reference.view(torch.int16), output.view(torch.int16)))}
        result["checks"] = checks
        if not all(checks.values()):
            raise RuntimeError("baseline-only diagnostic invariant failed")
        result["status"] = "diagnostic_complete_no_performance_verdict"
    except BaseException:
        result["status"], result["error"] = "failed", traceback.format_exc()
        traceback.print_exc()
    finally:
        if profile_pending and torch is not None:
            try:
                torch.cuda.synchronize()
                torch.cuda.profiler.stop()
                result["profile"]["stopped_in_cleanup"] = True
            except BaseException:
                result["profile"]["cleanup_error"] = traceback.format_exc()
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
                result["device_settled"] = True
            except BaseException:
                result["status"], result["settle_error"] = "failed", traceback.format_exc()
        if preinstall is not None:
            attention.kernel_unified_attention, attention.reduce_segments = preinstall[:2]
            backend.TritonAttentionMetadataBuilder.build, backend.TritonAttentionImpl.forward = preinstall[2:]
            result["entry_bindings_restored"] = (attention.kernel_unified_attention is preinstall[0]
                and attention.reduce_segments is preinstall[1] and backend.TritonAttentionMetadataBuilder.build is preinstall[2]
                and backend.TritonAttentionImpl.forward is preinstall[3])
        result["source_sha256"] = {path.name: digest(path) for path in source.iterdir() if path.is_file()}
        result["finished_utc"] = utc()
        write(run / "results.json", result)
    return 0 if result["status"] == "diagnostic_complete_no_performance_verdict" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", required=True, action="store_true")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    args = parser.parse_args()
    if not (args.run_dir / "source").is_dir():
        parser.error("controller must create unique run/source first")
    return worker(args.run_dir, args.model)


if __name__ == "__main__":
    raise SystemExit(main())
