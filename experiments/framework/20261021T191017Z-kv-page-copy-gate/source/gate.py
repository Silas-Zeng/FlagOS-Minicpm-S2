#!/usr/bin/env python3
"""42层/16K KV保存→毒化→恢复最短成本门；不加载权重、不接服务协议。"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import gc
import hashlib
import importlib.util
import json
from math import prod
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace

EXPECTED_COPY = "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c"
EXPECTED_BACKEND = "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605"
EXPECTED_RESHAPE = "a351178df66fb5364cbe663ba7f25346c6317927fcc29a8c00f8972a23440ace"
EXPECTED_OWNER = "6072137cfb178dd77ebf4fbf9dd5ffc46534a56bbc07cbbc03f603d8ac1cb3b1"
EXPECTED_MODEL = "59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180"
LAYERS, BLOCKS, POOL, PAGE = 42, 1024, 1058, 16384


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def memory_state():
    result = {}
    for name in ("/sys/fs/cgroup/memory.current", "/sys/fs/cgroup/memory.max",
                 "/sys/fs/cgroup/memory/memory.usage_in_bytes", "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        try:
            result[name] = Path(name).read_text().strip()
        except OSError:
            pass
    return result


def load(path):
    spec = importlib.util.spec_from_file_location("kv_page_copy_policy", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def extract_function(path, name):
    """仅抽取已pin文件中的精确函数文本；不执行该模块import或decorator。"""
    source = Path(path).read_text()
    nodes = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(nodes) != 1:
        raise ValueError("实际函数不唯一：" + name)
    lines = source.splitlines(keepends=True)
    node = nodes[0]
    text = "".join(lines[node.lineno - 1:node.end_lineno])
    import textwrap
    return textwrap.dedent(text)


def factories(torch, source):
    if sha(source / "triton_attn.py") != EXPECTED_BACKEND or sha(source / "attn_utils.py") != EXPECTED_RESHAPE:
        raise RuntimeError("未经审阅的KV布局源码")
    def no_scales(dtype):
        if dtype != "auto":
            raise ValueError("只支持BF16 auto cache")
        return False
    namespace = {"torch": torch, "prod": prod,
                 "get_dtype_size": lambda dtype: torch.empty((), dtype=dtype).element_size(),
                 "kv_cache_uses_per_token_head_scales": no_scales, "get_kv_cache_layout": lambda: "NHD"}
    functions = (("triton_attn.py", "get_kv_cache_shape"),
                 ("triton_attn.py", "get_kv_cache_stride_order"),
                 ("attn_utils.py", "_reshape_attention_kv_cache"))
    for path, name in functions:
        exec(compile("from __future__ import annotations\n" + extract_function(source / path, name), name, "exec"), namespace)
    shape = namespace["get_kv_cache_shape"](POOL, 16, 2, 128, "auto")
    order = namespace["get_kv_cache_stride_order"]()
    if shape != (POOL, 2, 16, 2, 128) or order != (0, 1, 2, 3, 4):
        raise RuntimeError("NHD实际factory结果不符")
    return namespace["_reshape_attention_kv_cache"], shape, order


def make_views(torch, reshape, shape, order, raw, packed):
    spec = SimpleNamespace(dtype=torch.bfloat16, page_size_padded=None)
    return [reshape(raw[0 if packed else i].view(-1), spec, shape, order, POOL,
                    (i * PAGE, LAYERS * PAGE) if packed else None) for i in range(LAYERS)]


def maps(kind):
    if kind == "contiguous":
        return list(range(1, BLOCKS + 1)), list(range(1, BLOCKS + 1))
    source = [1 + group * 132 + offset for group in range(8) for offset in range(128)]
    destination = [1 + (7 - group) * 132 + offset for group in range(8) for offset in range(128)]
    return source, destination


def holes(ids):
    values = sorted(set(range(1, POOL - 1)) - set(ids))
    runs = []
    for value in values:
        if runs and value == runs[-1][0] + runs[-1][1]:
            s, n = runs[-1]
            runs[-1] = (s, n + 1)
        else:
            runs.append((value, 1))
    return runs


def submit_many(policy, sources, destinations, plan):
    results = [policy.submit_page_copy(s, d, plan) for s, d in zip(sources, destinations)]
    return {"submitted_bytes": sum(x["submitted_bytes"] for x in results),
            "copy_calls": sum(x["copy_calls"] for x in results), "completion_ack": False}


def pass_once(torch, policy, raw, golden, host, views, reshape, shape, order, packed, src_ids, dst_ids, timed):
    page_bytes = raw[0].shape[1]
    save = policy.make_plan(src_ids, range(BLOCKS), POOL, BLOCKS, page_bytes)
    restore = policy.make_plan(range(BLOCKS), dst_ids, BLOCKS, POOL, page_bytes)
    expected = policy.make_plan(src_ids, dst_ids, POOL, POOL, page_bytes)
    compute, transfer = torch.cuda.current_stream(), torch.cuda.Stream()
    ready, poisoned, consumed = (torch.cuda.Event() for _ in range(3))
    begin_save, end_save, begin_restore, end_restore = (torch.cuda.Event(enable_timing=True) for _ in range(4))
    with torch.cuda.stream(transfer):
        for event in (begin_save, end_save, begin_restore, end_restore):
            event.record()
    end_restore.synchronize()  # timing event首次初始化排除在copy窗口外。
    # setup不进传输窗口。正确性pass保留真实跨stream生产依赖；timed pass排除setup H2D。
    with torch.cuda.stream(compute):
        for device, reference in zip(raw, golden):
            device.copy_(reference, non_blocking=True)
        ready.record()
    if timed:
        ready.synchronize()
    start = time.perf_counter_ns()
    with torch.cuda.stream(transfer):
        transfer.wait_event(ready)
        begin_save.record()
        save_info = submit_many(policy, raw, host, save)
        end_save.record()
    end_save.synchronize()  # pinned host完成前绝不读取/复用源页。
    save_wall = (time.perf_counter_ns() - start) / 1e6
    saved = all(torch.equal(h.narrow(0, d, n), g.narrow(0, s, n))
                for h, g in zip(host, golden) for s, d, n in save.runs)
    with torch.cuda.stream(compute):
        compute.wait_event(end_save)
        for tensor in raw:
            tensor.narrow(0, 1, POOL - 2).fill_(165)
        poisoned.record()
    if timed:
        poisoned.synchronize()
    start = time.perf_counter_ns()
    with torch.cuda.stream(transfer):
        transfer.wait_event(poisoned)
        begin_restore.record()
        restore_info = submit_many(policy, host, raw, restore)
        end_restore.record()
    if timed:
        end_restore.synchronize()
    restore_wall = (time.perf_counter_ns() - start) / 1e6 if timed else None
    with torch.cuda.stream(compute):
        compute.wait_event(end_restore)
        consumers = [view.clone() for view in views]  # 读取actual factory的42层视图，非Attention数学证明。
        consumed.record()
    consumed.synchronize()
    cpu_raw = [tensor.cpu() for tensor in raw]
    restored = all(torch.equal(actual.narrow(0, d, n), reference.narrow(0, s, n))
                   for actual, reference in zip(cpu_raw, golden) for s, d, n in expected.runs)
    guards = all(bool((tensor.narrow(0, 0, 1) == 90).all())
                 and bool((tensor.narrow(0, POOL - 1, 1) == 90).all()) for tensor in cpu_raw)
    untouched = all(bool((tensor.narrow(0, s, n) == 165).all()) for tensor in cpu_raw for s, n in holes(dst_ids))
    cpu_views = make_views(torch, reshape, shape, order, cpu_raw, packed)
    consumer_ok = all(torch.equal(output.cpu().view(torch.int16), expected_view.view(torch.int16))
                      for output, expected_view in zip(consumers, cpu_views))
    result = {"timed": timed, "save": save_info, "restore": restore_info,
              "cgroup_memory_observation_not_peak": memory_state(),
              "checks": {"saved_all_bytes": saved, "restored_all_bytes": restored,
                         "guard_pages_untouched": guards, "unselected_pages_still_poison": untouched,
                         "event_ordered_42_layer_consumer": consumer_ok}}
    if timed:
        result["timing"] = {"save_wall_ms": save_wall, "restore_wall_ms": restore_wall,
                            "save_event_ms": begin_save.elapsed_time(end_save),
                            "restore_event_ms": begin_restore.elapsed_time(end_restore)}
        result["timing"]["roundtrip_wall_ms"] = save_wall + restore_wall
        if any(not (x > 0) for x in result["timing"].values()):
            raise RuntimeError("无效copy计时事件")
    if not all(result["checks"].values()):
        raise AssertionError("KV字节/生命周期门失败：" + repr(result["checks"]))
    return result


def worker(run):
    source, torch = run / "source", None
    result = {"status": "started", "cases": [], "accuracy": "not evaluated", "official_performance": "not evaluated",
              "model": "MiniCPM5-2B layout; no weights", "layers": LAYERS, "tokens": BLOCKS * 16,
              "transfer_bytes_per_direction": LAYERS * BLOCKS * PAGE,
              "layouts_observed_in_service": False,
              "limitations": ["NHD normal/packed are actual-source-supported constructions, not a captured live runner layout.",
                              "Byte-copy and event consumer gate only; no allocator, request, cancellation or restore service protocol.",
                              "One warm sample per geometry; no stable bandwidth/E2E claim or overlap assumption.",
                              "Timing excludes allocation, poison, consumer clones and CPU validation; includes Python copy submission and direction completion.",
                              "Test-only consumer clones add GPU memory; this is not a production service KV capacity result."]}
    try:
        if sha(source / "copy.py") != EXPECTED_COPY or sha(source / "model-config.json") != EXPECTED_MODEL:
            raise RuntimeError("未经审阅的copy模块/模型")
        policy = load(source / "copy.py")
        import torch
        if torch.cuda.device_count() != 1:
            raise RuntimeError("要求单BI-V150")
        torch.cuda.set_device(0)
        props = torch.cuda.get_device_properties(0)
        if "BI-V150" not in props.name or props.multi_processor_count != 16:
            raise RuntimeError("未经审阅的device slice")
        result["device"] = str(props)
        result["torch"] = torch.__version__
        result["cgroup_memory_before_setup"] = memory_state()
        torch.manual_seed(721601)
        reshape, shape, order = factories(torch, source)
        result["derived_shape"] = shape
        for packed in (False, True):
            page_bytes, count = (LAYERS * PAGE, 1) if packed else (PAGE, LAYERS)
            started = time.perf_counter_ns()
            golden = [torch.empty((POOL, page_bytes // 2), dtype=torch.bfloat16, pin_memory=True).uniform_(-1, 1).view(torch.uint8)
                      for _ in range(count)]
            for tensor in golden:
                tensor.narrow(0, 0, 1).fill_(90)
                tensor.narrow(0, POOL - 1, 1).fill_(90)
            host = [torch.empty((BLOCKS, page_bytes), dtype=torch.uint8, pin_memory=True) for _ in range(count)]
            raw = [torch.empty((POOL, page_bytes), dtype=torch.uint8, device="cuda") for _ in range(count)]
            views = make_views(torch, reshape, shape, order, raw, packed)
            setup_ms = (time.perf_counter_ns() - started) / 1e6
            expected_stride0 = (LAYERS if packed else 1) * PAGE // 2
            if any(tuple(v.shape) != shape or v.stride(0) != expected_stride0 for v in views):
                raise RuntimeError("actual reshape视图布局不符")
            cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
            for kind in ("contiguous", "fragmented8"):
                source_ids, destination_ids = maps(kind)
                if min(source_ids + destination_ids) < 1 or max(source_ids + destination_ids) >= POOL - 1:
                    raise RuntimeError("构造map触guard/null页")
                case = {"layout": "packed42" if packed else "normal42", "map": kind,
                        "logical_blocks": BLOCKS, "physical_pool_blocks": POOL, "setup_ms_not_timed": setup_ms,
                        "host_explicit_bytes": sum(x.numel() for x in golden + host),
                        "device_raw_bytes": sum(x.numel() for x in raw),
                        "layer0_shape": list(views[0].shape), "layer0_stride": list(views[0].stride()),
                        "layer41_storage_offset": views[-1].storage_offset(), "passes": []}
                result["cases"].append(case)
                for timed in (False, True):
                    case["passes"].append(pass_once(torch, policy, raw, golden, host, views,
                        reshape, shape, order, packed, source_ids, destination_ids, timed))
                case["rng_unchanged"] = torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state())
                if not case["rng_unchanged"]:
                    raise RuntimeError("copy过程改变RNG")
                write(run / "results.json", result)
            del raw, host, golden, views
            gc.collect()
        result["status"] = "byte_event_correctness_passed_single_cost_samples_only"
        result["gpu_peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
    except BaseException:
        result["status"], result["error"] = "failed", traceback.format_exc()
        traceback.print_exc()
    finally:
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
            except BaseException:
                result["status"], result["cleanup_error"] = "failed", traceback.format_exc()
        result["source_sha256"] = {p.name: sha(p) for p in source.iterdir() if p.is_file()}
        write(run / "results.json", result)
    return 0 if result["status"] == "byte_event_correctness_passed_single_cost_samples_only" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--copy-path", type=Path)
    parser.add_argument("--source-evidence", type=Path)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir)
    if args.copy_path is None or args.source_evidence is None:
        parser.error("controller requires --copy-path and --source-evidence")
    import fcntl
    import validate_block_table_candidate as owner
    if sha(owner.__file__) != EXPECTED_OWNER:
        raise RuntimeError("未经审阅的device owner helper")
    root, run = owner.ROOT.resolve(), args.run_dir.resolve()
    if not run.is_relative_to(root / "framework") or run == root / "framework":
        raise ValueError("run要求ROOT/framework新子目录")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {"started_utc": utc(), "pid": os.getpid(), "command": [sys.executable, *sys.argv],
                "command_shell": shlex.join([sys.executable, *sys.argv]), "kind": "synthetic42layer KV copy cost/correctness; no service/weights"}
    child = monitor = lock = log_handle = None
    status = 1
    def interrupted(signum, frame):
        raise SystemExit("controller signal " + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    try:
        lock = (root / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest["preflight"] = owner.preflight(args.ixsmi)
        table = subprocess.check_output([args.ixsmi], text=True, timeout=10)
        query = subprocess.check_output([args.ixsmi, "--query-gpu=memory.used,utilization.gpu",
                                         "--format=csv,noheader,nounits"], text=True, timeout=10)
        manifest["preflight_query"] = query
        (run / "preflight-ixsmi.txt").write_text(table)
        if "No running processes found" not in table or query.strip() != "68, 0":
            raise RuntimeError("已有GPU进程")
        source = run / "source"
        source.mkdir()
        files = (("gate.py", Path(__file__)), ("copy.py", args.copy_path),
                 ("triton_attn.py", args.source_evidence / "source/vllm/v1/attention/backends/triton_attn.py"),
                 ("attn_utils.py", args.source_evidence / "source/vllm/v1/worker/gpu/attn_utils.py"),
                 ("source-evidence-manifest.json", args.source_evidence / "manifest.json"),
                 ("model-config.json", args.model / "config.json"),
                 ("validate_block_table_candidate.py", Path(owner.__file__)),
                 ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh"))
        for name, path in files:
            (source / name).write_bytes(path.read_bytes())
        for name, expected in (("copy.py", EXPECTED_COPY), ("triton_attn.py", EXPECTED_BACKEND),
                               ("attn_utils.py", EXPECTED_RESHAPE), ("model-config.json", EXPECTED_MODEL)):
            if sha(source / name) != expected:
                raise RuntimeError("gate asset变化：" + name)
        manifest["source_sha256"] = {p.name: sha(p) for p in source.iterdir() if p.is_file()}
        manifest["worker_command"] = [sys.executable, str(source / "gate.py"), "--run-dir", str(run), "--worker"]
        write(run / "manifest.json", manifest)
        with (run / "worker.log").open("x") as out:
            child = subprocess.Popen(manifest["worker_command"], stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
            manifest["worker_pid"] = child.pid
            log_handle = (run / "monitor.log").open("x")
            monitor = subprocess.Popen(["bash", str(source / "monitor_gpu.sh"), str(child.pid), str(run / "gpu.csv")],
                stdout=log_handle, stderr=subprocess.STDOUT, start_new_session=True)
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
                    pass
                except BaseException:
                    manifest["cleanup_error"], status = traceback.format_exc(), 1
        if log_handle is not None:
            log_handle.close()
        if child is not None and child.poll() is not None:
            try:
                manifest["postflight"] = owner.preflight(args.ixsmi)
                table = subprocess.check_output([args.ixsmi], text=True, timeout=10)
                query = subprocess.check_output([args.ixsmi, "--query-gpu=memory.used,utilization.gpu",
                                                 "--format=csv,noheader,nounits"], text=True, timeout=10)
                manifest["postflight_query"] = query
                (run / "postflight-ixsmi.txt").write_text(table)
                if "No running processes found" not in table or query.strip() != "68, 0":
                    raise RuntimeError("GPU进程未清理")
            except BaseException:
                manifest["postflight_error"], status = traceback.format_exc(), 1
        manifest.update(finished_utc=utc(), exit_code=status)
        write(run / "manifest.json", manifest)
        (run / "exit-code").write_text(str(status) + "\n")
        (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n")
        if lock is not None:
            lock.close()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
