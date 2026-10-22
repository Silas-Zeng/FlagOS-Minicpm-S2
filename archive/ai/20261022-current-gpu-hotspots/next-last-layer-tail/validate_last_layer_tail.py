#!/usr/bin/env python3
"""原始末层真实类的局部尾段门；无模型权重、KV、服务或生产Inductor接线。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys
import time
import traceback

EXPECTED_MODEL = "59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180"
EXPECTED_HELPER = "99d5a8c86dac67b7a2c0029842576fbd1439060525d4c6789b0ddd32703fc9ec"
LOOPS = 32


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def cpu_stat():
    path = Path("/sys/fs/cgroup/cpu/cpu.stat")
    return {"path": str(path), "observed": path.exists(),
            "raw": path.read_text() if path.exists() else None}


def worker(run, source, model):
    result = {"status": "started", "kind": "actual-class local eager tail only",
              "limitations": ["Synthetic attention output/residual and random BF16 weights; no 2B model weights.",
                              "No Attention/QKV/KV calls: this does not validate the full model cache or hook.",
                              "Actual class/native RMSNorm calls, not production Inductor/AOT tail timing.",
                              "M2048/N2 is one upper-bound fixture, not full workload coverage.",
                              "Tolerance gate is local only; bitwise and error values are retained separately.",
                              "No server, sampler, accuracy or end-to-end speed conclusion."],
              "cases": [], "timings": []}
    torch, held = None, []
    try:
        path = source / "last_layer_tail.py"
        if EXPECTED_HELPER is None or sha(path) != EXPECTED_HELPER:
            raise RuntimeError("unreviewed tail helper")
        spec = importlib.util.spec_from_file_location("local_last_layer_tail", path)
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        import torch
        import flag_gems
        import vllm_fl.envs as fl_envs
        from vllm_fl.utils import get_flag_gems_whitelist_blacklist
        from vllm.config import CompilationConfig, CUDAGraphMode, set_current_vllm_config
        from vllm.engine.arg_utils import EngineArgs

        if torch.cuda.device_count() != 1:
            raise RuntimeError("one visible accelerator required")
        torch.cuda.set_device(0)
        result["device"] = str(torch.cuda.get_device_properties(0))
        result["torch_num_threads"] = torch.get_num_threads()
        config = EngineArgs(model=str(model), served_model_name=["minicpm"],
                            gpu_memory_utilization=0.85, max_model_len=131072,
                            compilation_config=CompilationConfig(
                                cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
        if sha(model / "config.json") != EXPECTED_MODEL:
            raise RuntimeError("model configuration drift")
        white, black = get_flag_gems_whitelist_blacklist()
        result["flaggems"] = {"enabled": bool(fl_envs.USE_FLAGGEMS), "whitelist": white, "blacklist": black}
        if fl_envs.USE_FLAGGEMS:
            if white:
                flag_gems.only_enable(include=white, record=False, once=True)
            else:
                flag_gems.enable(unused=black, record=False, once=True)

        with torch.inference_mode(), set_current_vllm_config(config):
            tail = helper.create(config, source)
            result["installed_sources"] = tail.sources
            result["local_parts"] = [type(part).__module__ + "." + type(part).__name__ for part in tail.parts]
            torch.manual_seed(721508)
            for part in (tail.parts[0], tail.parts[2]):
                for name, parameter in part.named_parameters():
                    if parameter.ndim != 2 or parameter.dtype != torch.bfloat16:
                        raise RuntimeError("unexpected local projection parameter: " + name)
                    parameter.normal_(0, 1 / math.sqrt(parameter.shape[1]))
            for norm in (tail.parts[1], tail.parts[3]):
                norm.weight.fill_(1)

            rows, lengths = 2048, [1, 2047]
            ends = helper.query_end_rows(lengths, rows)
            indices = torch.tensor(ends, dtype=torch.int64, device="cuda")
            attention_output = torch.randn((rows, 2048), dtype=torch.bfloat16, device="cuda").mul_(0.5)
            residual = torch.randn_like(attention_output).mul_(0.5)
            held.extend((tail, indices, attention_output, residual))

            def snapshot(tensor):
                return tensor.detach().cpu().view(torch.int16).clone()

            def compare(a, b):
                af, bf = a.float(), b.float()
                difference = (af - bf).abs()
                def number(value):
                    result = float(value.item())
                    return result if math.isfinite(result) else str(result)
                return {"bitwise_equal": bool(torch.equal(a.view(torch.int16), b.view(torch.int16))),
                        "finite": bool(torch.isfinite(af).all() and torch.isfinite(bf).all()),
                        "max_abs": number(difference.max()),
                        "max_rel_floor_1e_6": number((difference / af.abs().clamp_min(1e-6)).max()),
                        "allclose_atol_0_01_rtol_0_01": bool(torch.allclose(af, bf, atol=0.01, rtol=0.01))}

            before_attention, before_residual = snapshot(attention_output), snapshot(residual)
            cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()

            def check_case(a, r, label):
                baseline_residual = r.clone()
                baseline_full, baseline_final_residual = tail(a, baseline_residual)
                expected = torch.index_select(baseline_full, 0, indices)
                expected_residual = torch.index_select(baseline_final_residual, 0, indices)
                actual, actual_residual = tail.selected(a, r, indices)
                return {"case": label, "hidden": compare(expected, actual),
                        "final_residual": compare(expected_residual, actual_residual)}

            # 首次真实调用也承担编译／调优，正确性后才计warm窗口。
            result["cases"].append(check_case(attention_output, residual, "M2048-N2-default-stream"))
            ready, done = torch.cuda.Event(), torch.cuda.Event()
            side = torch.cuda.Stream()
            changed_a = attention_output.clone().mul_(0.5)
            changed_r = residual.clone().mul_(0.75)
            before_changed_a, before_changed_r = snapshot(changed_a), snapshot(changed_r)
            ready.record()
            side.wait_event(ready)
            with torch.cuda.stream(side):
                result["cases"].append(check_case(changed_a, changed_r, "new-values-pointers-nondefault-stream"))
                done.record()
            held.extend((ready, done, side, changed_a, changed_r))
            done.synchronize()
            result["nondefault_stream_handle"] = int(side.cuda_stream)
            result["inputs_unchanged"] = (torch.equal(snapshot(attention_output), before_attention)
                                          and torch.equal(snapshot(residual), before_residual)
                                          and torch.equal(snapshot(changed_a), before_changed_a)
                                          and torch.equal(snapshot(changed_r), before_changed_r))
            result["rng_unchanged"] = (torch.equal(cpu_rng, torch.get_rng_state())
                                        and torch.equal(gpu_rng, torch.cuda.get_rng_state()))
            if not result["inputs_unchanged"] or not result["rng_unchanged"]:
                raise AssertionError("local tail unexpectedly changed immutable input or RNG")
            if not all(part["finite"] and part["allclose_atol_0_01_rtol_0_01"]
                       for case in result["cases"] for part in (case["hidden"], case["final_residual"])):
                raise AssertionError("local tail exceeds the declared tolerance; no timing")

            # 真实norm可能原地消费residual。每窗32份独占工作副本在时钟外重置，
            # 不把额外baseline输入clone计成候选收益；每份在窗内只消费一次。
            work_residuals = [residual.clone() for _ in range(LOOPS)]
            pairs = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in range(4)]
            for begin, end in pairs:
                begin.record(); end.record()
            torch.cuda.synchronize()
            held.extend((work_residuals, pairs))
            for ordinal, (name, pair) in enumerate(zip(("baseline", "candidate", "candidate", "baseline"), pairs)):
                for work in work_residuals:
                    work.copy_(residual)
                torch.cuda.synchronize()
                stats_before = cpu_stat()
                begin, end = pair
                wall_begin, thread_begin, process_begin = time.perf_counter_ns(), time.thread_time_ns(), time.process_time_ns()
                begin.record()
                outputs = []
                for work in work_residuals:
                    if name == "baseline":
                        full_hidden, _ = tail(attention_output, work)
                        # 原Model最终丢弃residual；计时不能多算第二份baseline gather。
                        outputs.append(torch.index_select(full_hidden, 0, indices))
                    else:
                        outputs.append(tail.selected(attention_output, work, indices)[0])
                end.record()
                submit_thread = time.thread_time_ns() - thread_begin
                submit_process = time.process_time_ns() - process_begin
                end.synchronize()
                elapsed_wall = (time.perf_counter_ns() - wall_begin) / 1e6
                event_ms = begin.elapsed_time(end)
                if not math.isfinite(event_ms) or event_ms <= 0:
                    raise RuntimeError("invalid timing event")
                result["timings"].append({"policy": name, "window": ordinal, "calls": LOOPS,
                    "wall_per_call_ms": elapsed_wall / LOOPS, "event_per_call_ms": event_ms / LOOPS,
                    "submit_thread_per_call_ms": submit_thread / 1e6 / LOOPS,
                    "submit_process_per_call_ms": submit_process / 1e6 / LOOPS,
                    "cpu_stat_before": stats_before, "cpu_stat_after": cpu_stat()})
                del outputs
            result["summary"] = {}
            for kind in ("wall", "event"):
                medians = {name: statistics.median(row[kind + "_per_call_ms"] for row in result["timings"] if row["policy"] == name)
                           for name in ("baseline", "candidate")}
                result["summary"][kind] = dict(medians, local_time_reduction_percent=(1 - medians["candidate"] / medians["baseline"]) * 100)
            result["status"] = "local_tolerance_passed_not_model_accuracy_or_production_speed"
    except BaseException:
        result["status"], result["error"] = "failed", traceback.format_exc()
    finally:
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
                result["device_settled"] = True
            except BaseException:
                result["status"], result["settle_error"] = "failed", traceback.format_exc()
                # 若设备未settle，强持资源直到worker退出，不进行原路重试。
                globals()["_UNSETTLED_TAIL_RESOURCES"] = held
        result["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write(run / "results.json", result)
    return 0 if result["status"] == "local_tolerance_passed_not_model_accuracy_or_production_speed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-worker", action="store_true", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    args = parser.parse_args()
    if not args.output_dir.is_dir() or not args.source_dir.is_dir():
        parser.error("outer owner must create output/source directories first")
    return worker(args.output_dir, args.source_dir, args.model)


if __name__ == "__main__":
    raise SystemExit(main())
