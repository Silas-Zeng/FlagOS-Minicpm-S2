#!/usr/bin/env python3
"""原Event门小fork：generic、typed blocking、直接Corex blocking；固定原负载。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import sys
import time
import traceback

sys.dont_write_bytecode = True
PAYLOAD_BYTES, COPIES, TRIALS = 32 * 1024 * 1024, 8, 4
GUARD = 4096
LABELS = ("A", "B", "C", "C", "B", "A")
EXPECTED_CUDART = "d39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527"
EXPECTED_NATIVE = "327e8aff211f33fd9f7fe0bd841b330e4205a5c0677e7a5e9b7c28ce0fec7365"
EXPECTED_CPP = "ee01eb013f054fe5ebcd057794bdce9b57a977c6f3745de77e48d4411f0b31d7"
EMERGENCY_KEEPALIVE = []


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2, allow_nan=False)
        file.write("\n")


def cpu_snapshot():
    paths = {"stat": "/sys/fs/cgroup/cpu/cpu.stat",
             "quota": "/sys/fs/cgroup/cpu/cpu.cfs_quota_us",
             "period": "/sys/fs/cgroup/cpu/cpu.cfs_period_us"}
    raw = {key: Path(path).read_text(encoding="utf-8").strip() for key, path in paths.items()}
    counters = {line.split()[0]: int(line.split()[1]) for line in raw["stat"].splitlines()}
    if not {"nr_periods", "nr_throttled", "throttled_time"} <= counters.keys():
        raise RuntimeError("实际v1 cpu.stat缺必要字段")
    if (int(raw["quota"]), int(raw["period"])) != (600000, 100000):
        raise RuntimeError("仅观测本实例原6CPU quota，不调整参数")
    return {"paths": paths, "raw": raw, "counters": counters, "recorded_utc": utc()}


def loaded_runtime():
    paths = set()
    for line in Path("/proc/self/maps").read_text(encoding="utf-8").splitlines():
        fields = line.split(None, 5)
        if len(fields) == 6 and "libcudart.so" in Path(fields[5]).name:
            paths.add(Path(fields[5]).resolve(strict=True))
    records = {str(path): sha(path) for path in sorted(paths)}
    if len(records) != 1 or next(iter(records.values())) != EXPECTED_CUDART:
        raise RuntimeError("实际进程libcudart不是本实例已核唯一Corex库：" + repr(records))
    return records


def constant_bytes(array, value):
    # NumPy min/max读取全部uint8，不创建32MiB临时bool或改变Torch线程设置。
    return int(array.min()) == value and int(array.max()) == value


def load_native(source, bridge_sha):
    if len(bridge_sha) != 64 or any(c not in "0123456789abcdef" for c in bridge_sha):
        raise RuntimeError("需要outer实际编译SO完整SHA")
    expected = {"biv150_native_blocking_event.py": EXPECTED_NATIVE,
                "bridge.cpp": EXPECTED_CPP, "bridge.so": bridge_sha}
    for name, expected_sha in expected.items():
        path = source / name
        if path.is_symlink() or not path.is_file() or sha(path) != expected_sha:
            raise RuntimeError("native Event素材SHA不符：" + name)
    spec = importlib.util.spec_from_file_location("biv150_native_event_gate", source / "biv150_native_blocking_event.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # adapter导入仅stdlib，NativeEvent构造才载SO。
    return module


def record_tested(event, stream, fixture):
    if event is fixture["native_event"]:
        event.record(stream_handle=int(stream.cuda_stream), keepalive=(stream, fixture))
    else:
        event.record()


def trial(torch, event, stream, fixture):
    source, host = fixture["source"], fixture["host"]
    # 前一trial已真实完成；仅payload poison，不重置guard掩盖越界。
    fixture["host_array"].fill(0xA5)
    begin, end = fixture["begin"], fixture["end"]
    submit_begin = time.perf_counter_ns()
    begin.record()
    for _ in range(COPIES):
        host.copy_(source, non_blocking=True)
    end.record()
    record_tested(event, stream, fixture)  # C显式native handle；A/B保原record。
    submit_ns = time.perf_counter_ns() - submit_begin
    early = bool(event.query())  # 窗外；记录进入synchronize前是否已经完成。
    thread_begin = time.thread_time_ns()
    process_begin = time.process_time_ns()
    wall_begin = time.perf_counter_ns()
    event.synchronize()  # 唯一被测等待，不把提交、query或验证计入wait。
    wall_ns = time.perf_counter_ns() - wall_begin
    process_ns = time.process_time_ns() - process_begin
    thread_ns = time.thread_time_ns() - thread_begin
    # 必须在任何额外同步/复制之前验证被测事件确实完成和payload全字节。
    checks = {"tested_event_complete": bool(event.query()), "timing_end_complete": bool(end.query()),
              "host_all_bytes_0x5a": constant_bytes(fixture["host_array"], 0x5A),
              "host_first_guard": constant_bytes(fixture["first_guard"], 0x13),
              "host_last_guard": constant_bytes(fixture["last_guard"], 0xE1)}
    if not all(checks.values()):
        raise RuntimeError("被测synchronize返回后尚未完成/字节或guard错误：" + repr(checks))
    elapsed_ms = float(begin.elapsed_time(end))
    # 前面检查通过后才另核源；该同步不能掩盖被测等待的错误。
    fixture["source_array"].fill(0x3C)
    fixture["source_readback"].copy_(source, non_blocking=True)
    fixture["verify"].record()
    fixture["verify"].synchronize()
    checks["source_all_bytes_unchanged"] = constant_bytes(fixture["source_array"], 0x5A)
    if not checks["source_all_bytes_unchanged"]:
        raise RuntimeError("GPU源全字节改变或源回读未完成")
    if int(torch.cuda.current_stream(0).cuda_stream) != int(stream.cuda_stream):
        raise RuntimeError("实际copy stream发生变化")
    return {"wait_wall_ns": wall_ns, "wait_thread_CPU_ns": thread_ns,
            "wait_process_CPU_ns": process_ns, "D2H_device_event_ms": elapsed_ms,
            "submission_wall_ns_excluded": submit_ns, "complete_before_wait": early,
            "copies": COPIES, "submitted_bytes": COPIES * PAYLOAD_BYTES, "checks": checks}


def device_worker(args):
    output, source_dir = Path(args.output_dir).resolve(), Path(args.source_dir).resolve()
    if (not output.is_dir() or source_dir != output / "source"
            or Path(__file__).resolve() != source_dir / "gate.py"):
        raise RuntimeError("须由外层创建独占RUN/source并归档为gate.py")
    if any((output / name).exists() for name in ("results.json", "failed.json")):
        raise RuntimeError("不覆盖已有原件")
    state = {"started_utc": utc(), "pid": os.getpid(), "command": shlex.join([sys.executable, *sys.argv]),
             "kind": "BI-V150 native Corex Event A/B/C/C/B/A wait gate, no model/service",
             "source_sha256": {p.name: sha(p) for p in source_dir.iterdir() if p.is_file()},
             "payload_bytes": PAYLOAD_BYTES, "copies_per_trial": COPIES, "trials_per_window": TRIALS,
             "routes": {"A": "torch.Event()", "B": "torch.cuda.Event(blocking=True)",
                        "C": "NativeEvent(Corex BlockingSync|DisableTiming)"},
             "bridge_sha256": args.bridge_sha256}
    keepalive, torch, settled, code = [], None, None, 1
    native_event = None
    try:
        setup_begin = time.perf_counter_ns()
        native = load_native(source_dir, args.bridge_sha256)
        import torch as actual_torch
        torch = actual_torch
        if torch.cuda.device_count() != 1 or torch.get_num_threads() != 56:
            raise RuntimeError("仅此实例单卡及原56Torch CPU线程；不改设置")
        device = torch.cuda.get_device_properties(0)
        if "BI-V150" not in device.name or device.multi_processor_count != 16:
            raise RuntimeError("不是本实例BI-V150/16SM")
        cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state(0).clone()
        stream = torch.cuda.Stream(device=0)
        if int(stream.cuda_stream) == 0:
            raise RuntimeError("必须显式非默认copy stream")
        keepalive.extend([stream, cpu_rng, gpu_rng])
        state.update({"torch": torch.__version__, "platform": platform.platform(),
                      "torch_CPU_threads": torch.get_num_threads(),
                      "device": {"name": device.name, "SM": device.multi_processor_count,
                                 "total_memory": device.total_memory},
                      "actual_loaded_libcudart": loaded_runtime(),
                      "explicit_nondefault_stream_handle": int(stream.cuda_stream)})
        with torch.cuda.stream(stream):
            native_event = native.NativeEvent(source_dir / "bridge.so", expected_sha256=args.bridge_sha256)
            keepalive.append(native_event)
            state["actual_loaded_libcudart_after_bridge"] = loaded_runtime()
            state["native_event_creation_flags"] = native_event.creation_flags
            state["native_event_bridge_sha256"] = native_event.bridge_sha256
            if state["native_event_creation_flags"] != 3:
                raise RuntimeError("实际SDK桥未返回BlockingSync|DisableTiming的预期flags3")
            gpu_source = torch.empty(PAYLOAD_BYTES, dtype=torch.uint8, device="cuda:0")
            keepalive.append(gpu_source)
            gpu_source.fill_(0x5A)
            backing = torch.empty(PAYLOAD_BYTES + 2 * GUARD, dtype=torch.uint8, pin_memory=True)
            host = backing.narrow(0, GUARD, PAYLOAD_BYTES)
            source_readback = torch.empty(PAYLOAD_BYTES, dtype=torch.uint8, pin_memory=True)
            events = {"A": torch.Event(), "B": torch.cuda.Event(blocking=True), "C": native_event}
            fixture = {"source": gpu_source, "host": host, "source_readback": source_readback,
                       "native_event": native_event,
                       "host_array": host.numpy(), "source_array": source_readback.numpy(),
                       "first_guard": backing.narrow(0, 0, GUARD).numpy(),
                       "last_guard": backing.narrow(0, GUARD + PAYLOAD_BYTES, GUARD).numpy(),
                       "begin": torch.cuda.Event(enable_timing=True),
                       "end": torch.cuda.Event(enable_timing=True), "verify": torch.cuda.Event()}
            keepalive.extend([backing, source_readback, events, fixture])
            fixture["first_guard"].fill(0x13)
            fixture["last_guard"].fill(0xE1)
            fixture["host_array"].fill(0xA5)
            fixture["source_array"].fill(0x3C)
            # 全部allocation/首次record/synchronize及copy路径预热均在六窗之前。
            source_readback.copy_(gpu_source, non_blocking=True)
            for event in [*events.values(), fixture["begin"], fixture["end"], fixture["verify"]]:
                record_tested(event, stream, fixture)
            fixture["verify"].synchronize()
            for event in events.values():
                event.synchronize()
            if not constant_bytes(fixture["source_array"], 0x5A):
                raise RuntimeError("源初始化/预热回读失败")
            state["event_types"] = {k: type(v).__module__ + "." + type(v).__qualname__ for k, v in events.items()}
            state["setup_wall_ns"] = time.perf_counter_ns() - setup_begin
            state["setup_scope"] = "含Torch导入/设备/RNG/库身份/全部buffer及事件惰性初始化/单次源回读，不计入wait"
            state["timing"] = {"method": "固定A/B/C/C/B/A，每窗4trial，每trial连续8次32MiB D2H",
                               "wait_scope": "仅被测event.synchronize及读取时钟开销；submit/query/poison/全字节验证均排除",
                               "cpu_stat_scope": "每窗外v1计数覆盖该窗四trial的等待及窗内计时外poison/验证，不等同纯wait节流",
                               "batches": []}
            for label in LABELS:
                before = cpu_snapshot()
                row = {"label": label, "cpu_stat_before": before, "trials": []}
                state["timing"]["batches"].append(row)
                for _ in range(TRIALS):
                    row["trials"].append(trial(torch, events[label], stream, fixture))
                after = cpu_snapshot()
                delta = {k: after["counters"][k] - v for k, v in before["counters"].items()}
                if any(v < 0 for v in delta.values()):
                    raise RuntimeError("CPUstat计数重置")
                row.update(cpu_stat_after=after, cpu_stat_delta=delta,
                           complete_before_wait_count=sum(t["complete_before_wait"] for t in row["trials"]))
                for key in ("wait_wall_ns", "wait_thread_CPU_ns", "wait_process_CPU_ns", "D2H_device_event_ms"):
                    row[key + "_mean"] = sum(t[key] for t in row["trials"]) / TRIALS
        state["RNG_unchanged"] = {"CPU": bool(torch.equal(cpu_rng, torch.get_rng_state())),
                                  "GPU": bool(torch.equal(gpu_rng, torch.cuda.get_rng_state(0)))}
        if not all(state["RNG_unchanged"].values()) or torch.get_num_threads() != 56:
            raise RuntimeError("RNG或原CPU线程设置改变")
        state["performance_gain_claim"] = None
        state["limits"] = ["仅实际Corex事件行为/完成性，不是模型prepare_inputs_event的暴露时间或服务收益。",
                           "CPU下降与wall不回退需读真实镜像窗口；不假设typed或direct blocking生效。",
                           "v1 throttled_time是累计节流ns，不作为wall损失；不改线程/额度/参数。"]
        settled, code = True, 0  # 每trial已通过被测完成及独立源回读事件；成功不全卡同步。
    except BaseException as error:
        state.update(error=repr(error), traceback=traceback.format_exc())
        print(state["traceback"], file=sys.stderr)
    finally:
        owner_device_sync, native_closed = False, None
        if torch is not None and settled is not True:
            try:
                torch.cuda.synchronize(0)  # 仅失败清理，不把失败补成pass。
                settled, owner_device_sync = True, True
            except BaseException as error:
                settled = False
                state["settle_error"] = repr(error)
        if native_event is not None and settled is True:
            try:
                native_event.close(owner_settled=owner_device_sync)
                native_closed = True
            except BaseException as error:
                native_closed, code = False, 1
                state["native_close_error"] = repr(error)
        retained = settled is False or native_closed is False
        if retained:
            EMERGENCY_KEEPALIVE.extend(keepalive)
        state["cleanup"] = {"device_settled": settled, "native_event_closed": native_closed,
                            "failure_owner_device_sync_completed": owner_device_sync,
                            "retained_until_process_exit_if_unsettled": retained,
                            "no_retry_after_submission_failure": True}
        if not retained:
            keepalive.clear()
            gc.collect()
    state.update(status="pass" if code == 0 else "reject", finished_utc=utc())
    write_new(output / ("results.json" if code == 0 else "failed.json"), state)
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-worker", action="store_true")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--bridge-sha256", required=True)
    args = parser.parse_args()
    if not args.device_worker:
        parser.error("只有设备子进程；锁/idle/超时/封存由外层负责")
    return device_worker(args)


if __name__ == "__main__":
    raise SystemExit(main())
