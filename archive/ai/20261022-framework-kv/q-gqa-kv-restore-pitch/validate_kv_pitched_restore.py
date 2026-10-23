#!/usr/bin/env python3
"""单层真实 FULL 目的页 H2D 字节/间隙/事件门；仅外层唯一 owner 启动，无计时矩阵。"""
from __future__ import annotations
import argparse
import gc
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import sys
import traceback

sys.dont_write_bytecode = True
EXPECTED_SAVE_RUNTIME = "818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd"
EXPECTED_RESTORE = "a7439c2c0b2b588dcd2af5c66b6eb62e562132ef8b5bc1d54ce54fc4b6e9804c"
EXPECTED_CPP = "48295ffde897cce988d3a8460904ab4451669e1de2fbe2bd5257d3f75e35ab20"
EXPECTED_BASELINE = "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c"
EXPECTED_HELPERS = "c8c0f64e7293634a28949f4338800298b43d32daa7cbd866e64dcd59833d7dc6"
EXPECTED_ABI = "f9c348a60fa34469377fda671d2d57a42c108fca2554fd59963b6b7033ffb576"
EXPECTED_EVIDENCE = "55c383db7601041cbc9a0d464e2395f30b36637d22ffb65231414d17444ae308"
PAGE = 16384
EMERGENCY_KEEPALIVE = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_source(source, bridge_sha):
    if (len(bridge_sha) != 64 or any(c not in "0123456789abcdef" for c in bridge_sha)):
        raise RuntimeError("必须传外层实际编译归档 bridge.so 的 SHA")
    expected = {"biv150_kv_pitched_copy.py": EXPECTED_SAVE_RUNTIME,
        "biv150_kv_pitched_restore.py": EXPECTED_RESTORE, "bridge.cpp": EXPECTED_CPP,
        "biv150_kv_page_copy.py": EXPECTED_BASELINE, "pitched-save-gate.py": EXPECTED_HELPERS,
        "restore-page-evidence.json": EXPECTED_EVIDENCE, "memcpy2d-abi.json": EXPECTED_ABI,
        "bridge.so": bridge_sha}
    for name, pin in expected.items():
        path = source / name
        if path.is_symlink() or not path.is_file() or sha(path) != pin:
            raise RuntimeError("归档 source 资产不符：" + name)
    return {p.name: sha(p) for p in source.iterdir() if p.is_file()}


def expected_info(restore, plan, maximum_pitch):
    pieces, fallback = restore.segments_for_pitch(plan, max_pitch=maximum_pitch)
    pitched = sum(s.height > 1 and s.physical_step > 1 for s in pieces)
    return {"submitted_bytes": plan.logical_pages * PAGE, "copy_calls": len(pieces),
        "linear_calls": len(pieces) - pitched, "pitched_calls": pitched,
        "fallback_pitched_segments": fallback, "original_c95f_calls": plan.original_c95f_runs,
        "completion_ack": False}


def correctness(torch, helpers, old, save, restore, bridge, evidence, stream, handle, maximum_pitch, keepalive):
    ids = tuple(evidence["destination_page_ids_in_original_order"])
    digest = hashlib.sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest()
    pool, count = max(ids) + 1, len(ids)
    if (digest != evidence["pages_sha256"] or count != 1043 or pool > 65536
            or count != evidence["logical_pages"] or len(set(ids)) != count):
        raise RuntimeError("唯一原始目的页证据/范围不符")
    plan = restore.make_restore_plan(ids, pool, save_runtime=save)
    old_plan = old.make_plan(range(count), ids, count, pool, PAGE)
    if (len(old_plan.runs) != 66 or plan.original_c95f_runs != 66 or len(plan.segments) != 14):
        raise RuntimeError("实际目的页几何不符")
    # 真 pinned host 和真 GPU raw 均取 backing 内部 view，主动覆盖非零 offset。
    host_backing, host = helpers.host_buffer(torch, count, 19, 89)
    helpers.pattern(torch, host, ids)
    host_original = host_backing.clone()
    initial = torch.empty((pool + 2, PAGE), dtype=torch.uint8, device="cpu", pin_memory=True)
    initial.fill_(165)
    initial.narrow(0, 0, 1).fill_(113)
    initial.narrow(0, pool + 1, 1).fill_(179)
    oracle = initial.clone()
    for logical, physical in enumerate(ids):
        oracle.narrow(0, physical + 1, 1).copy_(host.narrow(0, logical, 1))
    candidate_backing = torch.empty((pool + 2, PAGE), dtype=torch.uint8, device="cuda:0")
    baseline_backing = torch.empty_like(candidate_backing)
    candidate, baseline = (x.narrow(0, 1, pool) for x in (candidate_backing, baseline_backing))
    readback = torch.empty_like(initial, pin_memory=True)
    consumer = torch.empty((count, PAGE), dtype=torch.uint8, device="cuda:0")
    consumer_backing, consumer_host = helpers.host_buffer(torch, count, 199, 225)
    event = torch.cuda.Event()
    prepared = restore.prepare_restore([host], [candidate], plan, max_pitch=maximum_pitch)
    fixture = {"host_backing": host_backing, "host": host, "host_original": host_original,
        "initial": initial, "oracle": oracle, "candidate_backing": candidate_backing, "candidate": candidate,
        "baseline_backing": baseline_backing, "baseline": baseline, "readback": readback,
        "consumer": consumer, "consumer_backing": consumer_backing, "consumer_host": consumer_host,
        "event": event, "plan": plan, "old_plan": old_plan, "prepared": prepared}
    keepalive.append(fixture)  # 任一异步提交前，全部 Tensor/descriptor/event 都已被外层列表强持。
    helpers.assert_stream(torch, stream, handle)
    candidate_backing.copy_(initial, non_blocking=True)
    info = bridge.submit(prepared, stream_handle=handle)
    # 真同流消费者先读 selected GPU 行，再回读 compact 输出，随后才记录完成事件。
    # 先通过此门才启动全 pool 诊断或旧 c95f，避免后者掩盖 native 流/完成错误。
    for logical, physical, length in old_plan.runs:
        consumer.narrow(0, logical, length).copy_(candidate.narrow(0, physical, length), non_blocking=True)
    consumer_host.copy_(consumer, non_blocking=True)
    helpers.complete(event, stream)
    checks = {"native_submit_counts_and_not_ACK": info == expected_info(restore, plan, maximum_pitch),
        "same_stream_consumer_all_selected_bytes": bool(torch.equal(consumer_host, host)),
        "consumer_host_guards": helpers.all_true(helpers.guard_checks(torch, consumer_backing, count, 199, 225)),
        "host_and_destination_nonzero_storage_offsets": host.storage_offset() == candidate.storage_offset() == PAGE,
        "pinned_host_source_and_both_guards_unchanged": bool(torch.equal(host_backing, host_original))}
    if not helpers.all_true(checks):
        raise RuntimeError("native H2D 首完成/selected bytes 门失败：" + repr(checks))
    readback.copy_(candidate_backing, non_blocking=True)
    helpers.complete(event, stream)
    checks.update(candidate_all_selected_gap_and_guards_match_CPU_oracle=bool(torch.equal(readback, oracle)),
        candidate_positive_basic_guard_reads=helpers.all_true(helpers.guard_checks(torch, readback, pool, 113, 179)))
    if not helpers.all_true(checks):
        raise RuntimeError("native H2D 整 pool/gap/guard 门失败：" + repr(checks))
    # 只验证 c95f 的 H2D 参考；不调用旧 SAVE/D2H 提交，不做任何性能窗口。
    baseline_backing.copy_(initial, non_blocking=True)
    baseline_info = old.submit_page_copy(host, baseline, old_plan)
    helpers.complete(event, stream)
    readback.copy_(baseline_backing, non_blocking=True)
    helpers.complete(event, stream)
    checks.update(baseline_c95f_all_selected_gap_and_guards_match_same_oracle=bool(torch.equal(readback, oracle)),
        baseline_c95f_submit=baseline_info == {"submitted_bytes": count * PAGE, "copy_calls": 66, "completion_ack": False},
        host_source_and_both_guards_still_unchanged=bool(torch.equal(host_backing, host_original)))
    if not helpers.all_true(checks):
        raise RuntimeError("c95f H2D 参考/host 保留门失败：" + repr(checks))
    return {"source_evidence": evidence, "constructed_minimum_pool_pages": pool, "logical_pages": count,
        "one_layer_bytes": count * PAGE, "raw_layout": "单层normal raw uint8[pool,16384]，不是42层事务",
        "host_storage_offset_bytes": host.storage_offset(), "GPU_destination_storage_offset_bytes": candidate.storage_offset(),
        "actual_max_pitch_bytes": maximum_pitch, "required_destination_pitch_bytes": 33570816,
        "candidate_submit": info, "baseline_H2D_submit": baseline_info, "checks": checks,
        "selected_payload_sha256": helpers.tensor_sha(host), "native_completion_event": "同非0 current stream 的消费及回读之后 record/synchronize",
        "normal42_coverage": "未执行；本门不证明私有页资格/epoch/事务ACK/consumer恢复或42层生命周期"}


def device_worker(args):
    output, source = Path(args.output_dir).resolve(), Path(args.source_dir).resolve()
    if not output.is_dir() or source != output / "source" or any((output / n).exists() for n in ("results.json", "failed.json")):
        raise RuntimeError("外层独占 RUN/source 且不得覆盖旧结果")
    helpers = torch = None
    keepalive = []
    state = {"kind": "单层真实目的页 H2D pitched 正确性，无性能测量", "pid": os.getpid(),
        "command": shlex.join([sys.executable, *sys.argv])}
    try:
        state["source_sha256"] = check_source(source, args.bridge_sha256)
        helpers = load(source / "pitched-save-gate.py", "restore_gate_existing_helpers")
        state.update(started_utc=helpers.utc(), memory_before=helpers.memory_state())
        old = load(source / "biv150_kv_page_copy.py", "restore_gate_c95f")
        save = load(source / "biv150_kv_pitched_copy.py", "restore_gate_818e")
        restore = load(source / "biv150_kv_pitched_restore.py", "restore_gate_H2D")
        import torch as actual_torch
        torch = actual_torch
        if torch.cuda.device_count() != 1:
            raise RuntimeError("仅此单 BI-V150 实例")
        device = torch.cuda.get_device_properties(0)
        if "BI-V150" not in device.name or device.multi_processor_count != 16:
            raise RuntimeError("需实际 BI-V150/16SM")
        bridge = restore.RestoreBridge(source / "bridge.so", expected_sha256=args.bridge_sha256, save_runtime=save)
        maximum_pitch = bridge.max_pitch(device=0)
        if maximum_pitch < 33570816:
            raise RuntimeError("此实际目的数组需33,570,816B pitch；不以全线性回退冒充二维H2D验证")
        stream = torch.cuda.Stream(device=0)
        handle = int(stream.cuda_stream)
        keepalive.extend([stream, bridge, save, restore])
        state.update(platform=platform.platform(), torch=torch.__version__, torch_CPU_threads=torch.get_num_threads(),
            device={"name": device.name, "SM": device.multi_processor_count, "total_memory": device.total_memory},
            actual_loaded_libcudart=helpers.loaded_runtime(), bridge_sha256=args.bridge_sha256,
            explicit_nondefault_stream_handle=handle)
        cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state(0).clone()
        evidence = json.loads((source / "restore-page-evidence.json").read_text(encoding="utf-8"))
        with torch.cuda.stream(stream):
            helpers.assert_stream(torch, stream, handle)
            state["case"] = correctness(torch, helpers, old, save, restore, bridge, evidence,
                                        stream, handle, maximum_pitch, keepalive)
        state["RNG_unchanged"] = {"CPU": bool(torch.equal(cpu_rng, torch.get_rng_state())),
            "GPU": bool(torch.equal(gpu_rng, torch.cuda.get_rng_state(0)))}
        if not helpers.all_true(state["RNG_unchanged"]):
            raise RuntimeError("本门改变 RNG 状态")
        state.update(status="pass", finished_utc=helpers.utc(), memory_after=helpers.memory_state(),
            performance_gain_claim=None, scope="仅独立单层H2D真实页序/selected+gap+guard/offset/事件；无模型/性能/42层事务")
        helpers.write_new(output / "results.json", state)
        keepalive.clear()
        gc.collect()
        return 0
    except BaseException as error:
        settled = None
        if torch is not None:
            try:
                # 仅失败路径允许全设备 settle；submitted=0 也不豁免。
                torch.cuda.synchronize(0)
                settled = True
            except BaseException as settle_error:
                settled = False
                state["settle_error"] = repr(settle_error)
                EMERGENCY_KEEPALIVE.extend(keepalive)
        state.update(status="reject", error=repr(error), traceback=traceback.format_exc(),
            failure_device_settled=settled, retained_until_process_exit_if_unsettled=settled is False,
            no_old_route_retry_after_native_failure=True)
        with (output / "failed.json").open("x", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write("\n")
        print(state["traceback"], file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-worker", action="store_true")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--bridge-sha256", required=True)
    args = parser.parse_args()
    if not args.device_worker:
        parser.error("仅复用外层 controller 的唯一设备子进程")
    return device_worker(args)


if __name__ == "__main__":
    raise SystemExit(main())
