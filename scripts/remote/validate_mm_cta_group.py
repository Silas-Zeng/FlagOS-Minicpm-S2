#!/usr/bin/env python3
"""两种真实 MLP 形状的固定 tile CTA 门；无权重、服务、调优或官方计分。

控制器不导入加速器运行时。仅持锁 child 初始化 CUDA，保存原输出、完整源码、
设备信息及前后占用；每形状只做 baseline/group8 和一次 32-call ABBA。
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import inspect
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


EXPECTED_POLICY = "06c7cd9216907886e7d66a81d4fd5d9f78edef9daac2380ca263ce8c1770b8e1"
EXPECTED_MM = "4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090"
EXPECTED_LIBENTRY = "414e8a3f74e2522e40659e7fccd84e301f4517220837a87af0311f050bbf3025"
EXPECTED_TRITON = "df3092178f70be89b50d22905cedae5bac414cc38677053616fc56802c91af30"
EXPECTED_MODEL = "59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180"
LOOPS = 32
TIMING_METHOD = "per shape one ABBA; 32 compiled-kernel launches/window; Event pairs pre-recorded; record/submit/final sync inside wall"


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def timed_batch(torch, callback, pair):
    torch.cuda.synchronize()
    start, end = pair
    begin = time.perf_counter_ns()
    start.record()
    for _ in range(LOOPS):
        callback()
    end.record()
    torch.cuda.synchronize()
    wall = (time.perf_counter_ns() - begin) / 1e6
    event = start.elapsed_time(end)
    if not math.isfinite(event) or event <= 0:
        raise RuntimeError("invalid timing Event elapsed time")
    return {"calls": LOOPS, "wall_total_ms": wall, "wall_per_call_ms": wall / LOOPS,
            "event_total_ms": event, "event_per_call_ms": event / LOOPS}


def guard_snapshot(torch, run, phase, storages):
    """正数 basic view 的完整 CPU bits 是判据；旧高级索引仅作诊断。"""
    directory = run / "guard-bits"
    directory.mkdir(exist_ok=True)
    expected = int(torch.tensor(-17, dtype=torch.bfloat16).view(torch.int16))
    result = {"phase": phase, "expected_int16": expected, "storages": {}}
    for name, storage in storages.items():
        record = {"data_ptr": storage.data_ptr(), "storage_ptr": storage.untyped_storage().data_ptr(),
                  "storage_offset": storage.storage_offset(), "stride": list(storage.stride()), "rows": {}}
        basic = []
        for label, index in (("first", 0), ("last", storage.shape[0] - 1)):
            bits = storage[index].detach().cpu().view(torch.int16).contiguous()
            basic.append(bits)
            path = directory / (phase + "-" + name + "-" + label + ".i16")
            path.write_bytes(bits.numpy().tobytes())
            record["rows"][label] = {"positive_index": index, "file": str(path.relative_to(run)),
                                      "sha256": digest(path), "elements": bits.numel(),
                                      "unexpected_elements": int((bits != expected).sum()),
                                      "first_16_int16": bits[:16].tolist(), "last_16_int16": bits[-16:].tolist()}
        # 原门的读法也保留；比对均在CPU上，避免让GPU比较自身成为唯一oracle。
        advanced = storage[[0, -1]].detach().cpu().view(torch.int16).contiguous()
        path = directory / (phase + "-" + name + "-advanced.i16")
        path.write_bytes(advanced.numpy().tobytes())
        record["advanced"] = {"file": str(path.relative_to(run)), "sha256": digest(path),
                              "matches_basic": all(torch.equal(advanced[i], row) for i, row in enumerate(basic)),
                              "unexpected_elements_cpu": int((advanced != expected).sum()),
                              "original_gpu_predicate": bool((storage[[0, -1]] == -17).all())}
        record["advanced_read_kept_storage"] = all(
            torch.equal(storage[index].detach().cpu().view(torch.int16), row)
            for index, row in zip((0, storage.shape[0] - 1), basic))
        result["storages"][name] = record
    return result


def guard_bits_unchanged(snapshot, initial):
    """仅比较 CPU basic 读数；高级索引异常不能把正确 guard 判为失败。"""
    return all(
        record["advanced_read_kept_storage"]
        and all(row["unexpected_elements"] == 0
                and row["sha256"] == initial["storages"][name]["rows"][label]["sha256"]
                for label, row in record["rows"].items())
        for name, record in snapshot["storages"].items())


def worker(run, *, guard_diagnostic=False):
    source = run / "source"
    result = {"status": "started", "phase": "source", "cases": [],
              "worker_command": [sys.executable, *sys.argv],
              "worker_command_shell": shlex.join([sys.executable, *sys.argv]),
              "guard_diagnostic": guard_diagnostic,
              "timing_loops": 0 if guard_diagnostic else LOOPS,
              "timing_method": "not timed; gate-up guard phase diagnosis" if guard_diagnostic else TIMING_METHOD,
              "accuracy": "not evaluated", "official_performance": "not evaluated",
              "limitations": ["Synthetic BF16 inputs and weight layouts, no model weights or runner.",
                              "Only two M2048 shapes; no other M/config coverage or graph capture.",
                              "No autotuner; original JIT body with explicit audited C0 values.",
                              "Single ABBA signals are not end-to-end or stable-gain evidence."]}
    torch = None
    try:
        if digest(source / "policy.py") != EXPECTED_POLICY or digest(source / "mm_original.py") != EXPECTED_MM:
            raise RuntimeError("unreviewed worker input")
        policy = load("fixed_mm_cta_policy", source / "policy.py")
        result["cpu_mapping"] = policy.mapping_coverage()
        text = json.loads((source / "model-config.json").read_text(encoding="utf-8"))
        if (digest(source / "model-config.json") != EXPECTED_MODEL
                or (text.get("hidden_size"), text.get("intermediate_size"), text.get("num_hidden_layers"),
                    text.get("num_attention_heads"), text.get("num_key_value_heads")) != (2048, 6144, 42, 16, 2)):
            raise RuntimeError("requires the pinned MiniCPM5-2B configuration")
        import importlib
        import torch
        import triton
        entry = importlib.import_module("flag_gems.utils.libentry")
        mm_spec = importlib.util.find_spec("flag_gems.runtime.backend._iluvatar.ops.mm")
        if mm_spec is None or mm_spec.origin is None or digest(mm_spec.origin) != EXPECTED_MM:
            raise RuntimeError("installed Iluvatar MM differs from the official source")
        if digest(entry.__file__) != EXPECTED_LIBENTRY or digest(triton.__file__) != EXPECTED_TRITON:
            raise RuntimeError("unaudited fixed-launch runtime")
        for filename, path in (("installed_mm.py", mm_spec.origin), ("libentry.py", entry.__file__),
                               ("triton-init.py", triton.__file__)):
            (source / filename).write_bytes(Path(path).read_bytes())
        result["runtime_versions"] = {"torch": torch.__version__, "triton": triton.__version__}
        result["phase"] = "device"
        if torch.cuda.device_count() != 1:
            raise RuntimeError("requires exactly one visible accelerator")
        torch.cuda.set_device(0)
        props = torch.cuda.get_device_properties(0)
        if "BI-V150" not in props.name or props.multi_processor_count != 16:
            raise RuntimeError("requires the audited BI-V150 slice")
        result["device"] = str(props)
        torch.manual_seed(721503)
        pair = policy.create((source / "mm_original.py").read_bytes(), source)
        shapes = (("gate-up", (2048, 12288, 2048)), ("down", (2048, 2048, 6144)))
        for label, (m, n, k) in (shapes[:1] if guard_diagnostic else shapes):
            result["phase"] = "inputs:" + label
            a = torch.randn((m, k), dtype=torch.bfloat16, device="cuda").mul_(0.125)
            weights = torch.randn((n, k), dtype=torch.bfloat16, device="cuda").mul_(0.125)
            # F.linear 权重为 [N,K] 连续布局，实际 GEMM 的 B 是其转置 view。
            b = weights.T
            a[0].zero_()
            a[1, 0::2] = 0.125
            a[1, 1::2] = -0.125
            before_a, before_weights = a.clone(), weights.clone()
            baseline_storage = torch.full((m + 2, n), -17, dtype=torch.bfloat16, device="cuda")
            candidate_storage = torch.full_like(baseline_storage, -17)
            baseline_out, candidate_out = baseline_storage[1:-1], candidate_storage[1:-1]
            cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
            case = {"case": label}
            result["cases"].append(case)
            storages = {"baseline": baseline_storage, "candidate": candidate_storage}
            case["guard_phases"] = []
            def record_guards(phase):
                snapshot = guard_snapshot(torch, run, label + "-" + phase, storages)
                case["guard_phases"].append(snapshot)
                snapshot["basic_bits_match_expected_and_initial"] = guard_bits_unchanged(
                    snapshot, case["guard_phases"][0])
                if not guard_diagnostic and not snapshot["basic_bits_match_expected_and_initial"]:
                    raise AssertionError("basic CPU guard bits changed: " + phase)
            record_guards("after_full_initialization")
            if guard_diagnostic:
                case["out_views"] = {name: {"data_ptr": tensor.data_ptr(),
                                             "storage_ptr": tensor.untyped_storage().data_ptr(),
                                             "storage_offset": tensor.storage_offset(),
                                             "stride": list(tensor.stride()),
                                             "pointer_offset_bytes": tensor.data_ptr() - tensor.untyped_storage().data_ptr(),
                                             "expected_offset_bytes": tensor.storage_offset() * tensor.element_size()}
                                     for name, tensor in (("baseline", baseline_out), ("candidate", candidate_out))}
            result["phase"] = "compile:" + label
            baseline, base_info = pair.prepare(a, b, baseline_out, grouped=False)
            record_guards("after_baseline_jit")
            candidate, group_info = pair.prepare(a, b, candidate_out, grouped=True)
            case.update(baseline=base_info, candidate=group_info)
            record_guards("after_candidate_jit")
            if guard_diagnostic:
                case["compiled_C"] = {}
                for name, callback in (("baseline", baseline), ("candidate", candidate)):
                    tensor = inspect.getclosurevars(callback).nonlocals["all_args"][2]
                    case["compiled_C"][name] = {"data_ptr": tensor.data_ptr(),
                                                 "storage_offset": tensor.storage_offset(),
                                                 "is_prepared_out": tensor is (baseline_out if name == "baseline" else candidate_out)}
            # 首次 JIT launch 已完成；此处实际走与 LibEntry 相同的 compiled 热接口。
            # 先覆盖初次 JIT 结果，保证正确性门检查的是热 launcher 的实际写入。
            baseline_out.fill_(float("nan"))
            record_guards("after_baseline_poison")
            candidate_out.fill_(float("nan"))
            record_guards("after_candidate_poison")
            baseline()
            record_guards("after_baseline_compiled")
            candidate()
            record_guards("after_candidate_compiled")
            torch.cuda.synchronize()
            result["phase"] = "correctness:" + label
            def checks():
                return {"all_output_bits_equal": torch.equal(baseline_out.view(torch.int16), candidate_out.view(torch.int16)),
                        "valid_output_finite": bool(torch.isfinite(candidate_out).all()),
                        "guard_rows_untouched": case["guard_phases"][-1]["basic_bits_match_expected_and_initial"],
                        "inputs_unchanged": torch.equal(a.view(torch.int16), before_a.view(torch.int16))
                                            and torch.equal(weights.view(torch.int16), before_weights.view(torch.int16)),
                        "rng_unchanged": torch.equal(cpu_rng, torch.get_rng_state())
                                         and torch.equal(gpu_rng, torch.cuda.get_rng_state())}
            case["correctness"] = checks()
            if guard_diagnostic:
                initial = case["guard_phases"][0]["storages"]
                case["guard_changes_from_initial"] = [
                    {"phase": entry["phase"], "baseline": {row: entry["storages"]["baseline"]["rows"][row]["sha256"]
                                                           != initial["baseline"]["rows"][row]["sha256"] for row in ("first", "last")},
                     "candidate": {row: entry["storages"]["candidate"]["rows"][row]["sha256"]
                                    != initial["candidate"]["rows"][row]["sha256"] for row in ("first", "last")}}
                    for entry in case["guard_phases"]]
                continue
            if not all(case["correctness"].values()):
                raise AssertionError("fixed-mm correctness failed: " + repr(case["correctness"]))
            for callback in (baseline, candidate):
                callback(); callback()
            torch.cuda.synchronize()
            result["phase"] = "timing:" + label
            events = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in range(4)]
            for first, last in events:
                first.record(); last.record()
            torch.cuda.synchronize()
            case["timings"] = []
            for name, callback, event_pair in zip(("baseline", "candidate", "candidate", "baseline"),
                                                 (baseline, candidate, candidate, baseline), events):
                row = timed_batch(torch, callback, event_pair)
                row["policy"] = name
                case["timings"].append(row)
            case["summary"] = {}
            for kind in ("wall", "event"):
                old = statistics.median(x[kind + "_per_call_ms"] for x in case["timings"] if x["policy"] == "baseline")
                new = statistics.median(x[kind + "_per_call_ms"] for x in case["timings"] if x["policy"] == "candidate")
                case["summary"][kind] = {"baseline_ms": old, "candidate_ms": new, "fraction_saved": 1 - new / old}
            record_guards("after_timing")
            case["after_timing"] = checks()
            if not all(case["after_timing"].values()):
                raise AssertionError("post-timing output/input/RNG mismatch")
        result["status"] = "guard_diagnostic_complete_not_a_correctness_pass" if guard_diagnostic else "correctness_passed_fixed_tile_signal_only"
        result["phase"] = "complete"
    except BaseException:
        result["status"], result["error"] = "failed", traceback.format_exc()
        traceback.print_exc()
    finally:
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
            except BaseException:
                result["status"], result["shutdown_error"] = "failed", traceback.format_exc()
        result["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        write(run / "results.json", result)
    return 0 if result["status"] in ("correctness_passed_fixed_tile_signal_only",
                                     "guard_diagnostic_complete_not_a_correctness_pass") else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--policy-path", type=Path)
    parser.add_argument("--mm-source", type=Path)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--guard-diagnostic", action="store_true", help="only gate-up phase guard snapshots; no timing/down")
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir, guard_diagnostic=args.guard_diagnostic)
    if args.policy_path is None or args.mm_source is None:
        parser.error("controller requires --policy-path and --mm-source")
    import fcntl
    import validate_block_table_candidate as owner
    root, run = owner.ROOT.resolve(), args.run_dir.resolve()
    if not run.is_relative_to(root) or run == root:
        raise ValueError("run must be a new child of the experiment root")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {"started_utc": utc(), "pid": os.getpid(), "command": [sys.executable, *sys.argv],
                "command_shell": shlex.join([sys.executable, *sys.argv]), "timing_loops": 0 if args.guard_diagnostic else LOOPS,
                "guard_diagnostic": args.guard_diagnostic,
                "kind": "gate-up guard phase diagnosis; no timing/down" if args.guard_diagnostic else "two fixed-tile MLP enumeration cases; no weights/service/tuning/score",
                "timing_method": "not timed; guard snapshots" if args.guard_diagnostic else TIMING_METHOD,
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
        for name, path in (("gate.py", Path(__file__)), ("policy.py", args.policy_path),
                           ("mm_original.py", args.mm_source), ("model-config.json", args.model / "config.json"),
                           ("validate_block_table_candidate.py", Path(owner.__file__)),
                           ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh")):
            (source / name).write_bytes(path.read_bytes())
        for name, expected in (("policy.py", EXPECTED_POLICY), ("mm_original.py", EXPECTED_MM),
                               ("model-config.json", EXPECTED_MODEL)):
            if expected is None or digest(source / name) != expected:
                raise RuntimeError("unreviewed MM gate asset: " + name)
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["packages"] = {}
        for package in ("torch", "vllm", "FlagGems", "SQLAlchemy"):
            try:
                manifest["packages"][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][package] = "unavailable"
        manifest["worker_command"] = [sys.executable, str(source / "gate.py"), "--worker", "--run-dir", str(run)]
        if args.guard_diagnostic:
            manifest["worker_command"].append("--guard-diagnostic")
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
