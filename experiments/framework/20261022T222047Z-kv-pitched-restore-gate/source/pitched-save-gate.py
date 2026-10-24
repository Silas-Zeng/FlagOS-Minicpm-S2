#!/usr/bin/env python3
"""单层真实SAVE页序的C batch+2D组合门；只供外层唯一设备owner启动。"""
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
EXPECTED_RUNTIME = "818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd"
EXPECTED_CPP = "0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44"
EXPECTED_BASELINE = "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c"
EXPECTED_GEOMETRY = "489f1468956ff96e86188feeb89933df0ab5d35458b8d184b6adbb2729497dbc"
EXPECTED_ABI = "f9c348a60fa34469377fda671d2d57a42c108fca2554fd59963b6b7033ffb576"
EXPECTED_LIBCUDART = "d39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527"
PAGE, TIMING_LOOPS = 16384, 8
# 异步失败且不能settle时，保全部引用到设备子进程被外层定向清理。
EMERGENCY_KEEPALIVE = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2, allow_nan=False)
        file.write("\n")


def utc():
    return datetime.now(timezone.utc).isoformat()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_source(source, bridge_sha):
    expected = {"biv150_kv_pitched_copy.py": EXPECTED_RUNTIME, "bridge.cpp": EXPECTED_CPP,
                "biv150_kv_page_copy.py": EXPECTED_BASELINE,
                "save-arithmetic-evidence.json": EXPECTED_GEOMETRY, "memcpy2d-abi.json": EXPECTED_ABI,
                "bridge.so": bridge_sha}
    if len(bridge_sha) != 64 or any(c not in "0123456789abcdef" for c in bridge_sha):
        raise RuntimeError("需要外层实际编译bridge.so的完整SHA")
    for name, expected_sha in expected.items():
        path = source / name
        if path.is_symlink() or not path.is_file() or sha(path) != expected_sha:
            raise RuntimeError("设备门source资产不符：" + name)
    return {path.name: sha(path) for path in source.iterdir() if path.is_file()}


def loaded_runtime():
    records = {}
    for line in Path("/proc/self/maps").read_text(encoding="utf-8").splitlines():
        fields = line.split(None, 5)
        if len(fields) != 6 or "libcudart.so" not in Path(fields[5]).name:
            continue
        path = Path(fields[5])
        if not path.is_absolute() or not path.is_file():
            raise RuntimeError("实际加载libcudart路径不可确认：" + fields[5])
        resolved = path.resolve(strict=True)
        records[str(resolved)] = {"sha256": sha(resolved), "mapped_path": str(path)}
    if len(records) != 1 or next(iter(records.values()))["sha256"] != EXPECTED_LIBCUDART:
        raise RuntimeError("实际进程未唯一加载已核Corex libcudart：" + repr(records))
    return records


def memory_state():
    out = {}
    for name in ("/sys/fs/cgroup/memory.current", "/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/cpu.max"):
        try:
            out[name] = Path(name).read_text(encoding="utf-8").strip()
        except OSError:
            pass
    return out


def pattern(torch, target, physical_ids):
    """每4字节编码16bit物理页号及12bit页内word号；不依赖随机数或GPU索引。"""
    pages = torch.tensor(physical_ids, dtype=torch.int64, device="cpu")
    words = torch.arange(PAGE // 4, dtype=torch.int64, device="cpu")
    target[:, 0::4].copy_((pages & 255).to(torch.uint8).reshape(-1, 1))
    target[:, 1::4].copy_(((pages >> 8) & 255).to(torch.uint8).reshape(-1, 1))
    target[:, 2::4].copy_((words & 255).to(torch.uint8).reshape(1, -1))
    target[:, 3::4].copy_(((words >> 8) & 255).to(torch.uint8).reshape(1, -1))


def host_buffer(torch, count, first, last):
    backing = torch.empty((count + 2, PAGE), dtype=torch.uint8, device="cpu", pin_memory=True)
    backing.fill_(165)
    backing.narrow(0, 0, 1).fill_(first)
    backing.narrow(0, count + 1, 1).fill_(last)
    return backing, backing.narrow(0, 1, count)


def tensor_sha(tensor):
    if tensor.device.type != "cpu":
        raise RuntimeError("SHA只可读取已完成的CPU数据")
    return hashlib.sha256(tensor.contiguous().numpy().tobytes()).hexdigest()


def guard_checks(torch, backing, count, first, last):
    # 必须正数basic narrow；BI-V150历史advanced guard读取有异常，不能作唯一oracle。
    return {"first": bool(torch.equal(backing.narrow(0, 0, 1), torch.full((1, PAGE), first, dtype=torch.uint8))),
            "last": bool(torch.equal(backing.narrow(0, count + 1, 1), torch.full((1, PAGE), last, dtype=torch.uint8)))}


def all_true(value):
    return all(all_true(v) for v in value.values()) if isinstance(value, dict) else value is True


def assert_stream(torch, stream, handle):
    if (type(handle) is not int or handle == 0 or int(stream._as_parameter_.value) != handle
            or int(torch.cuda.current_stream(0).cuda_stream) != handle):
        raise RuntimeError("必须非0的同一个显式Torch stream/native handle")


def complete(event, stream):
    event.record(stream)
    event.synchronize()


def source_unchanged(torch, fixture, stream):
    fixture["source_readback"].copy_(fixture["source_backing"], non_blocking=True)
    complete(fixture["event"], stream)
    return bool(torch.equal(fixture["source_seed"], fixture["source_readback"]))


def expected_counts(plan, maximum_pitch):
    linear = pitched = fallback = 0
    for segment in plan.segments:
        if segment.height > 1 and segment.source_step > 1:
            if segment.source_step * PAGE > maximum_pitch:
                fallback += 1
                linear += segment.height
            else:
                pitched += 1
        else:
            linear += 1
    return {"submitted_bytes": plan.logical_pages * PAGE, "copy_calls": linear + pitched,
            "linear_calls": linear, "pitched_calls": pitched, "fallback_pitched_segments": fallback,
            "original_c95f_calls": plan.original_c95f_runs, "completion_ack": False}


def correctness_case(torch, old, new, bridge, raw_case, stream, handle, maximum_pitch, keepalive):
    ids = tuple(raw_case["source_page_ids_in_original_order"])
    pool, count = max(ids) + 1, len(ids)
    if pool > 65536 or count != raw_case["logical_pages"]:
        raise RuntimeError("pattern/page证据范围不符")
    t = time.perf_counter()
    old_plan = old.make_plan(ids, tuple(range(count)), pool, count, PAGE)
    old_plan_ms = (time.perf_counter() - t) * 1000
    t = time.perf_counter()
    new_plan = new.make_plan(ids, pool)
    new_plan_ms = (time.perf_counter() - t) * 1000
    if (len(old_plan.runs) != raw_case["actual_current_contiguous_run_count_per_layer"]
            or new_plan.original_c95f_runs != len(old_plan.runs)
            or len(new_plan.segments) != raw_case["hypothetical_cover_submission_count_per_layer"]):
        raise RuntimeError("原始实际页序几何不符")
    seed = torch.empty((pool + 2, PAGE), dtype=torch.uint8, device="cpu", pin_memory=True)
    seed.narrow(0, 0, 1).fill_(113)
    seed.narrow(0, pool + 1, 1).fill_(179)
    pattern(torch, seed.narrow(0, 1, pool), range(pool))
    source_backing = torch.empty((pool + 2, PAGE), dtype=torch.uint8, device="cuda:0")
    source = source_backing.narrow(0, 1, pool)
    source_readback = torch.empty_like(seed, pin_memory=True)
    old_backing, old_host = host_buffer(torch, count, 19, 89)
    new_backing, new_host = host_buffer(torch, count, 199, 225)
    oracle = torch.empty((count, PAGE), dtype=torch.uint8, device="cpu")
    pattern(torch, oracle, ids)
    event = torch.cuda.Event()
    t = time.perf_counter()
    prepared = new.prepare_save([source], [new_host], new_plan, max_pitch=maximum_pitch)
    prepare_ms = (time.perf_counter() - t) * 1000
    fixture = {"source_backing": source_backing, "source": source, "source_seed": seed,
               "source_readback": source_readback, "old_backing": old_backing, "old_host": old_host,
               "new_backing": new_backing, "new_host": new_host, "oracle": oracle, "event": event,
               "prepared": prepared, "old_plan": old_plan, "new_plan": new_plan, "count": count, "pool": pool}
    keepalive.append(fixture)  # 首次任何异步提交前强持所有src/host/event/descriptor。
    assert_stream(torch, stream, handle)
    # producer与新桥紧接在同流；先检查新host，再启动旧路，避免旧copy等待掩盖stream错误。
    source_backing.copy_(seed, non_blocking=True)
    candidate_info = bridge.submit(prepared, stream_handle=handle)
    complete(event, stream)
    checks = {"candidate_vs_CPU_page_offset_oracle": bool(torch.equal(new_host, oracle)),
              "candidate_guards_after_native": all_true(guard_checks(torch, new_backing, count, 199, 225)),
              "candidate_actual_submit_counts": candidate_info == expected_counts(new_plan, maximum_pitch)}
    if not all_true(checks):
        raise RuntimeError("新桥首轮正确性失败：" + repr(checks))
    baseline_info = old.submit_page_copy(source, old_host, old_plan)
    complete(event, stream)
    checks.update({"baseline_vs_CPU_page_offset_oracle": bool(torch.equal(old_host, oracle)),
                   "candidate_vs_frozen_c95f_all_bytes": bool(torch.equal(new_host, old_host)),
                   "baseline_submit_counts": baseline_info == {"submitted_bytes": count * PAGE,
                       "copy_calls": len(old_plan.runs), "completion_ack": False},
                   "baseline_guards": all_true(guard_checks(torch, old_backing, count, 19, 89)),
                   "candidate_guards_after_baseline": all_true(guard_checks(torch, new_backing, count, 199, 225)),
                   "entire_source_and_both_source_guards_unchanged": source_unchanged(torch, fixture, stream)})
    if not all_true(checks):
        raise RuntimeError("c95f/输入完整字节/guard门失败：" + repr(checks))
    report = {"run_id_evidence": raw_case["run_id"], "prefix_tokens_evidence": raw_case["prefix_tokens"],
              "logical_pages": count, "source_pool_pages": pool, "one_layer_bytes": count * PAGE,
              "source_storage_offset_bytes": source.storage_offset(), "host_storage_offset_bytes": new_host.storage_offset(),
              "original_runs": len(old_plan.runs), "new_plan_segments": len(new_plan.segments),
              "segments": [vars(segment) for segment in new_plan.segments],
              "required_max_source_pitch_bytes": max(segment.source_step * PAGE for segment in new_plan.segments),
              "actual_device_max_pitch_bytes": maximum_pitch, "candidate_submit": candidate_info,
              "baseline_submit": baseline_info, "checks": checks, "payload_sha256": tensor_sha(new_host),
              "CPU_prepare_excluded_ms": {"baseline_make_plan": old_plan_ms, "new_make_plan": new_plan_ms,
                                          "new_prepare_save_all_tensor_checks_and_ctypes_descriptors": prepare_ms}}
    return fixture, report


def timing(torch, old, bridge, fixture, stream, handle):
    def call(label):
        assert_stream(torch, stream, handle)
        if label == "baseline_c95f":
            return old.submit_page_copy(fixture["source"], fixture["old_host"], fixture["old_plan"])
        return bridge.submit(fixture["prepared"], stream_handle=handle)
    labels = ("baseline_c95f", "candidate_C_batch_plus_2D", "candidate_C_batch_plus_2D", "baseline_c95f")
    events = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in labels]
    # 惰性event构造/首record及每一实际submit函数预热在计时窗外。
    for start, end in events:
        start.record(stream)
        complete(end, stream)
    for label in labels[:2]:
        call(label)
        complete(fixture["event"], stream)
    batches = []
    for label, (start, end) in zip(labels, events):
        begin = time.perf_counter()
        start.record(stream)
        for _ in range(TIMING_LOOPS):
            info = call(label)
        end.record(stream)
        end.synchronize()
        wall_ms = (time.perf_counter() - begin) * 1000
        event_ms = start.elapsed_time(end)
        batches.append({"label": label, "loops": TIMING_LOOPS, "wall_ms_per_call": wall_ms / TIMING_LOOPS,
                        "same_stream_event_ms_per_call": event_ms / TIMING_LOOPS, "last_submit": info})
    checks = {"baseline_payload_still_equal": bool(torch.equal(fixture["old_host"], fixture["oracle"])),
              "candidate_payload_still_equal": bool(torch.equal(fixture["new_host"], fixture["oracle"])),
              "baseline_guards": all_true(guard_checks(torch, fixture["old_backing"], fixture["count"], 19, 89)),
              "candidate_guards": all_true(guard_checks(torch, fixture["new_backing"], fixture["count"], 199, 225)),
              "entire_source_and_both_guards_unchanged": source_unchanged(torch, fixture, stream)}
    if not all_true(checks):
        raise RuntimeError("计时后输入/完整输出/guard失败：" + repr(checks))
    return {"method": "首case固定8call ABBA；真实submit+同流event完成wall，含各自Python/C校验和event record/sync",
            "excluded": "双方plan、Tensor/ctypes descriptors准备、分配/填值/H2D producer/CPU比较/guard检查在窗外，准备耗时另列",
            "interpretation": "只比较c95f与C batch+2D组合；不分离2D贡献、不代表42层SAVE、服务或E2E",
            "batches": batches, "post_timing_checks": checks}


def device_worker(args):
    output, source = Path(args.output_dir).resolve(), Path(args.source_dir).resolve()
    if not output.is_dir() or source != output / "source":
        raise RuntimeError("外层须先创建独立RUN/source")
    if any((output / name).exists() for name in ("results.json", "failed.json")):
        raise RuntimeError("不覆盖原设备门结果")
    state = {"started_utc": utc(), "kind": "BI-V150 one-layer SAVE C-batch plus pitched-copy gate",
             "command": shlex.join([sys.executable] + sys.argv), "pid": os.getpid(),
             "source_sha256": check_source(source, args.bridge_sha256), "memory_before": memory_state()}
    keepalive, torch = [], None
    try:
        old = load(source / "biv150_kv_page_copy.py", "biv150_frozen_c95f_gate")
        new = load(source / "biv150_kv_pitched_copy.py", "biv150_pitched_gate_runtime")
        import torch as actual_torch
        torch = actual_torch
        if torch.cuda.device_count() != 1:
            raise RuntimeError("只支持此实例单BI-V150")
        device = torch.cuda.get_device_properties(0)
        if "BI-V150" not in device.name or device.multi_processor_count != 16:
            raise RuntimeError("未匹配此实例BI-V150/16SM")
        bridge = new.Bridge(source / "bridge.so", expected_sha256=args.bridge_sha256)
        maximum_pitch = bridge.max_pitch(device=0)
        state.update({"platform": platform.platform(), "torch": torch.__version__,
                      "device": {"name": device.name, "SM": device.multi_processor_count, "total_memory": device.total_memory},
                      "torch_CPU_threads": torch.get_num_threads(), "actual_loaded_libcudart": loaded_runtime(),
                      "bridge_sha256": args.bridge_sha256, "max_pitch_bytes": maximum_pitch})
        stream = torch.cuda.Stream(device=0)
        handle = int(stream.cuda_stream)
        state["explicit_nondefault_stream_handle"] = handle
        keepalive.extend([stream, bridge])
        rng_cpu, rng_gpu = torch.get_rng_state().clone(), torch.cuda.get_rng_state(0).clone()
        geometry = json.loads((source / "save-arithmetic-evidence.json").read_text(encoding="utf-8"))["results"]
        if len(geometry) != 2:
            raise RuntimeError("只验证两组冻结实际SAVE数组")
        state["cases"] = []
        with torch.cuda.stream(stream):
            assert_stream(torch, stream, handle)
            fixtures = []
            for case in geometry:
                fixture, report = correctness_case(torch, old, new, bridge, case, stream, handle, maximum_pitch, keepalive)
                fixtures.append(fixture)
                state["cases"].append(report)
            # 两组正确性都已真完成才计首case；不扩形状/层数/配置扫描。
            state["timing"] = timing(torch, old, bridge, fixtures[0], stream, handle)
            complete(fixtures[0]["event"], stream)
        state["RNG_unchanged"] = {"CPU": bool(torch.equal(rng_cpu, torch.get_rng_state())),
                                  "GPU": bool(torch.equal(rng_gpu, torch.cuda.get_rng_state(0)))}
        if not all_true(state["RNG_unchanged"]):
            raise RuntimeError("复制门改变RNG状态")
        state.update({"status": "pass", "finished_utc": utc(), "memory_after": memory_state(),
                      "performance_gain_claim": None,
                      "scope": "仅单层两真实SAVE页序、完整原KV bytes和组合submit成本；无模型/worker/service/accuracy或DMA描述符声称"})
        write_new(output / "results.json", state)
        keepalive.clear()
        gc.collect()
        return 0
    except BaseException as error:
        settled = None
        if torch is not None:
            try:
                # 仅失败清理允许全设备settle；成功路径从不靠它证明stream正确。
                torch.cuda.synchronize(0)
                settled = True
            except BaseException as settle_error:
                settled = False
                state["settle_error"] = repr(settle_error)
                EMERGENCY_KEEPALIVE.extend(keepalive)
        state.update({"status": "reject", "finished_utc": utc(), "error": repr(error),
                      "traceback": traceback.format_exc(), "failure_device_settled": settled,
                      "retained_until_process_exit_if_unsettled": settled is False,
                      "no_baseline_retry_after_candidate_submit_failure": True})
        write_new(output / "failed.json", state)
        print(state["traceback"], file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-worker", action="store_true", help="仅由外层唯一锁/idle/编译/封存控制器启动")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--bridge-sha256", required=True)
    args = parser.parse_args()
    if not args.device_worker:
        parser.error("本脚本没有controller；必须--device-worker")
    return device_worker(args)


if __name__ == "__main__":
    raise SystemExit(main())
