#!/usr/bin/env python3
"""Strict pure-decode CPU gather elimination gate; correctness only.

The controller imports no accelerator packages. Its one child executes the
actual pinned _prepare_inputs and input-ID helpers using fixture runner state,
actual CpuGpuBuffer and actual BlockTable. Timing is not end-to-end evidence.
"""
from __future__ import annotations

import argparse
import ast
import copy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import traceback
from types import SimpleNamespace as NS


sys.dont_write_bytecode = True

EXPECTED = {
    "runner.py": "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141",
    "runtime.py": "0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f",
    "async-runtime.py": "1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc",
    "gather-runtime.py": "1a9de781b2f9504c627991071c5ee4b52eda59ca8af283f28a15b9fab38ef7bd",
    "gpu_input_batch.py": "de1ea4fc9d43fc6079dd375e407c2b6d93f5e1a11f49732d13654c41eaf30a65",
    "utils.py": "4e4cda209e10d4477d251003779dec26ea5ef47541c3310995c007c7ee5fdcdb",
    "block_table.py": "b3a6649b968fba0b48c333d7ac96e65cc713a86133cc7eef0a8399f5339ec600",
}
CASES = (("decode62", [1] * 62), ("mixed259", [1] * 31 + [228]),
         ("mixed952", [1] * 31 + [921]), ("mixed2048", [1] * 29 + [2019]),
         ("prefill2048", [2048]), ("decode_identity", [1] * 62),
         ("decode_new_request", [1] * 62))


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


def extract_methods(source, namespace):
    tree = ast.parse(source)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ModelRunnerFL")
    names = ("_compute_prev_positions", "_get_cumsum_and_arange", "_prepare_input_ids",
             "_prepare_inputs", "synchronize_input_prep")
    nodes = [copy.deepcopy(next(node for node in cls.body
                               if isinstance(node, ast.FunctionDef) and node.name == name)) for name in names]
    assert all(not node.decorator_list for node in nodes[:-1])
    assert len(nodes[-1].decorator_list) == 1 and ast.unparse(nodes[-1].decorator_list[0]) == "contextmanager"
    unit = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *nodes], type_ignores=[])
    ast.fix_missing_locations(unit)
    exec(compile(unit, "audited:_prepare_inputs", "exec"), namespace)
    return {name: namespace[name] for name in names}


def make_runner(torch, np, methods, buffers, tables):
    device = torch.device("cuda:0")
    maximum, requests, model_len = 2048, 64, 131072
    text = NS(hidden_size=2048, num_hidden_layers=42, num_attention_heads=16, num_key_value_heads=2)
    model = NS(model="/workspace/MiniCPM5-2B", dtype=torch.bfloat16, quantization=None,
               hf_text_config=text, is_encoder_decoder=False)
    config = NS(model_config=model, parallel_config=NS(tensor_parallel_size=1, pipeline_parallel_size=1,
        decode_context_parallel_size=1, data_parallel_size=1, use_ubatching=False), speculative_config=None,
        lora_config=None, cache_config=NS(kv_sharing_fast_prefill=False))
    class Runner:
        pass
    for name, function in methods.items():
        setattr(Runner, name, function)
    runner = Runner()
    runner.vllm_config, runner.device, runner.pin_memory = config, device, True
    runner.max_num_tokens, runner.max_num_reqs = maximum, requests
    runner.is_pooling_model = runner.supports_mm_inputs = runner.enable_prompt_embeds = False
    runner.use_aux_hidden_state_outputs = runner.uses_mrope = runner.use_async_spec_decode = False
    runner.use_async_scheduling = True
    runner.prepare_inputs_event = torch.Event()
    runner.uses_xdrope_dim = runner.num_spec_tokens = runner.prev_num_spec_tokens = 0
    runner._draft_token_ids = runner.mamba_prev_last_scheduled_idx = runner.num_accepted_tokens_event = None
    runner.cache_config, runner.lora_config = NS(mamba_cache_mode="none"), None
    buffer = lambda size, dtype: buffers(size, dtype=dtype, device=device, pin_memory=True)
    runner.input_ids = buffer(maximum, torch.int32)
    runner.query_start_loc = buffer(requests + 1, torch.int32)
    runner.query_pos = buffer(maximum, torch.int64)
    runner.req_indices = buffer(maximum, torch.int64)
    runner.prev_positions = buffer(requests, torch.int64)
    runner.num_scheduled_tokens = buffer(requests, torch.int32)
    runner.discard_request_mask = buffer(requests, torch.bool)
    runner.num_accepted_tokens = buffer(requests, torch.int32)
    runner.positions = torch.full((maximum,), -111, dtype=torch.int64, device=device)
    runner.seq_lens = torch.full((requests,), -112, dtype=torch.int32, device=device)
    runner.num_computed_tokens = torch.full((requests,), -113, dtype=torch.int32, device=device)
    runner.optimistic_seq_lens_cpu = torch.zeros(requests, dtype=torch.int32, pin_memory=True)
    runner.arange_np = np.arange(maximum, dtype=np.int64)
    computed = torch.zeros(requests, dtype=torch.int32, pin_memory=True)
    tokens = torch.arange(requests * model_len, dtype=torch.int32).reshape(requests, model_len)
    table = tables(max_num_reqs=requests, max_model_len=model_len, max_num_batched_tokens=maximum,
        pin_memory=True, device=device, block_sizes=[16], kernel_block_sizes=[16], max_num_blocks=[8192])
    for row in range(requests):
        table.add_row(([(row * 257 + column * 7) % 65536 for column in range(8192)],), row)
    runner.input_batch = NS(block_table=table, token_ids_cpu_tensor=tokens, token_ids_cpu=tokens.numpy(),
        num_computed_tokens_cpu_tensor=computed, num_computed_tokens_cpu=computed.numpy(),
        req_prompt_embeds={}, prev_sampled_token_ids=None, prev_req_id_to_index={}, req_ids=[], num_reqs=0)
    return runner


def configure(runner, np, torch, lengths, ordinal, *, previous=True):
    count, total = len(lengths), sum(lengths)
    ids = [f"fixture-{index}" for index in range(count)]
    batch = runner.input_batch
    batch.num_reqs, batch.req_ids = count, ids
    # Changes every consecutive call, including the page-offset residue.
    values = np.array([16300 + (index * 3 + ordinal) % 37 for index in range(count)], dtype=np.int32)
    batch.num_computed_tokens_cpu[:count] = values
    batch.prev_req_id_to_index = ({name: count - index - 1 for index, name in enumerate(ids)} if previous else {})
    batch.prev_sampled_token_ids = (torch.arange(count, dtype=torch.int32, device="cuda").reshape(count, 1)
                                   + ordinal * 100) if previous else None
    runner.requests = {name: NS(num_tokens=int(done + length + 1))
                       for name, done, length in zip(ids, values, lengths)}
    scheduled = np.array(lengths, dtype=np.int32)
    output = NS(total_num_scheduled_tokens=total, scheduled_spec_decode_tokens={})
    return output, scheduled


def selection_counts(runner, metadata, asynchronous, gather):
    state = getattr(runner, metadata._STATE, None)
    gather_state = getattr(runner, gather.STATE, {})
    return {"metadata": 0 if state is None else state["selected"],
            "async_token": asynchronous.selected_launches,
            "cpu_gather_skips": gather_state.get("selected", 0),
            "cpu_gather_fallbacks": gather_state.get("fallback", 0)}


def pointers(runner):
    return (runner.positions.data_ptr(), runner.seq_lens.data_ptr(), runner.input_ids.gpu.data_ptr(),
            runner.input_batch.block_table[0].slot_mapping.gpu.data_ptr())


def worker(run):
    import contextlib
    import numpy as np
    import torch
    import vllm.v1.utils as utils
    import vllm.v1.worker.block_table as table_module
    import vllm.v1.worker.gpu_input_batch as input_module

    result = {"status": "started", "cases": [], "accuracy": "not evaluated", "end_to_end": "not evaluated",
              "limitations": ["AST-extracted actual methods, fixture runner/InputBatch fields, no model weights.",
                              "Original dispatch in this isolated method is not proof of compiled service dispatch.",
                              "CPU input_ids scratch may remain stale only when every valid GPU token is overwritten; no service/accuracy claim."]}
    try:
        if torch.cuda.device_count() != 1:
            raise RuntimeError("expected exactly one visible accelerator")
        torch.cuda.set_device(0)
        for label, module in (("utils.py", utils), ("gpu_input_batch.py", input_module), ("block_table.py", table_module)):
            if digest(Path(module.__file__)) != EXPECTED[label]:
                raise RuntimeError("installed source mismatch: " + label)
        runtime = load("vllm_fl.patches.biv150_cpu_metadata", run / "source/runtime.py")
        asynchronous = load("vllm_fl.patches.biv150_async_token_update", run / "source/async-runtime.py")
        gather = load("vllm_fl.patches.biv150_decode_cpu_gather", run / "source/gather-runtime.py")
        original_source = (run / "source/runner.py").read_bytes()
        candidate_source = (run / "source/runner-combined.py").read_bytes()
        common = {"np": np, "torch": torch, "contextmanager": contextlib.contextmanager}
        common.update(_biv150_try_cpu_metadata=runtime.try_cpu_metadata,
                      _biv150_fused_sampled_token_update=asynchronous.fused_sampled_token_update)
        assert gather.reverse(candidate_source) == original_source
        original = extract_methods(original_source, dict(common))
        candidate = extract_methods(candidate_source, {**common,
                    "_biv150_skip_dead_cpu_gather": gather.skip_dead_cpu_gather})
        result["async_platform_vendor"] = str(asynchronous.current_platform.vendor_name)
        cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
        baseline = make_runner(torch, np, original, utils.CpuGpuBuffer, table_module.MultiGroupBlockTable)
        changed = make_runner(torch, np, candidate, utils.CpuGpuBuffer, table_module.MultiGroupBlockTable)
        fixed_pointers = [pointers(r) for r in (baseline, changed)]
        for ordinal, (name, lengths) in enumerate(CASES):
            outputs, selection = [], None
            for runner in (baseline, changed):
                # Observe and update reused host state only after its original event.
                with runner.synchronize_input_prep():
                    previous = name not in ("mixed259", "mixed2048")
                    output, scheduled = configure(runner, np, torch, lengths, ordinal, previous=previous)
                    if name == "decode_identity":
                        runner.input_batch.prev_req_id_to_index = {rid: index for index, rid in enumerate(runner.input_batch.req_ids)}
                    elif name == "decode_new_request":
                        old = runner.input_batch.req_ids[-1]
                        runner.input_batch.req_ids[-1] = "new-request"
                        runner.requests["new-request"] = runner.requests.pop(old)
                    runner.input_ids.cpu.fill_(-905)
                    runner.input_ids.gpu.fill_(-906)
                    before = selection_counts(changed, runtime, asynchronous, gather)
                    outputs.append(runner._prepare_inputs(output, scheduled))
                    if runner is changed:
                        after = selection_counts(changed, runtime, asynchronous, gather)
                        selection = {"before": before, "after": after,
                                     "delta": {key: after[key] - value for key, value in before.items()}}
            torch.cuda.synchronize()
            checks = {}
            for key in ("positions", "seq_lens", "num_computed_tokens"):
                checks[key] = torch.equal(getattr(baseline, key), getattr(changed, key))
            for key in ("input_ids", "query_start_loc", "discard_request_mask", "num_accepted_tokens"):
                checks[key] = torch.equal(getattr(baseline, key).gpu, getattr(changed, key).gpu)
            checks["logits_indices"] = torch.equal(outputs[0][0], outputs[1][0]) and outputs[0][1] is outputs[1][1] is None
            checks["slots"] = torch.equal(baseline.input_batch.block_table[0].slot_mapping.gpu,
                                         changed.input_batch.block_table[0].slot_mapping.gpu)
            checks["cpu_mirrors"] = (np.array_equal(baseline.req_indices.np, changed.req_indices.np)
                                      and np.array_equal(baseline.num_scheduled_tokens.np, changed.num_scheduled_tokens.np))
            checks["fixed_addresses"] = fixed_pointers == [pointers(r) for r in (baseline, changed)]
            assert all(checks.values()), (name, checks)
            should_skip = name in ("decode62", "decode_identity")
            expected_async = int(name not in ("mixed259", "mixed2048", "decode_identity"))
            selection_checks = {"metadata_selected": selection["delta"]["metadata"] == 1,
                                "original_gpu_branch": selection["delta"]["async_token"] == expected_async,
                                "dead_gather_selection": selection["delta"]["cpu_gather_skips"] == int(should_skip),
                                "fallback_selection": selection["delta"]["cpu_gather_fallbacks"] == int(not should_skip)}
            checks["cpu_scratch_dead_only_when_proven"] = (
                bool((changed.input_ids.cpu == -905).all()) if should_skip
                else torch.equal(baseline.input_ids.cpu, changed.input_ids.cpu))
            expected_ids = []
            batch = changed.input_batch
            previous_ids = (None if batch.prev_sampled_token_ids is None
                            else batch.prev_sampled_token_ids.cpu().numpy())
            for row, rid in enumerate(batch.req_ids):
                old = (batch.prev_req_id_to_index or {}).get(rid)
                if old is not None and lengths[row] == 1 and previous_ids is not None:
                    expected_ids.append(int(previous_ids[old, 0]))
                else:
                    start = int(batch.num_computed_tokens_cpu[row])
                    expected_ids.extend(batch.token_ids_cpu[row, start:start + lengths[row]].tolist())
                    if old is not None and previous_ids is not None:
                        expected_ids[-1] = int(previous_ids[old, 0])
            checks["all_valid_gpu_ids_cpu_or_previous_oracle"] = torch.equal(
                changed.input_ids.gpu[:sum(lengths)].cpu(), torch.tensor(expected_ids, dtype=torch.int32))
            assert all(checks.values()), (name, checks)
            assert all(selection_checks.values()), (name, selection)
            result["cases"].append({"name": name, "tokens": sum(lengths), "requests": len(lengths),
                                    "checks": checks, "selection": selection, "selection_checks": selection_checks})
        # Consecutive changed host values with no per-step device synchronize.
        # Copies are consumed by graph replay at the original fixed addresses.
        captures, destinations = [], []
        for runner in (baseline, changed):
            destination = tuple(torch.empty_like(tensor) for tensor in (runner.positions, runner.seq_lens,
                                runner.input_batch.block_table[0].slot_mapping.gpu, runner.input_ids.gpu))
            torch.cuda.synchronize()
            graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph):
                for target, source in zip(destination, (runner.positions, runner.seq_lens,
                                         runner.input_batch.block_table[0].slot_mapping.gpu, runner.input_ids.gpu)):
                    target.copy_(source)
            captures.append(graph)
            destinations.append(destination)
        consumed = []
        result["graph_steps"] = []
        for ordinal in range(4):
            snapshots = []
            for runner, graph, destination in zip((baseline, changed), captures, destinations):
                with runner.synchronize_input_prep():
                    output, scheduled = configure(runner, np, torch, [1] * 62, ordinal + 10)
                    runner.input_ids.cpu.fill_(-905)
                    before = selection_counts(changed, runtime, asynchronous, gather)
                    runner._prepare_inputs(output, scheduled)
                    if runner is changed:
                        after = selection_counts(changed, runtime, asynchronous, gather)
                        delta = {key: after[key] - value for key, value in before.items()}
                        assert delta == {"metadata": 1, "async_token": 1, "cpu_gather_skips": 1, "cpu_gather_fallbacks": 0}, (ordinal, delta)
                        assert bool((runner.input_ids.cpu == -905).all()), "graph step executed dead CPU gather"
                        result["graph_steps"].append({"ordinal": ordinal, "before": before,
                                                       "after": after, "delta": delta})
                graph.replay()
                snapshots.append(tuple(value.clone() for value in destination))
            consumed.append(snapshots)
        torch.cuda.synchronize()
        assert all(torch.equal(a, b) for pair in consumed for a, b in zip(*pair))
        assert not torch.equal(consumed[0][1][0], consumed[-1][1][0]), "graph observed stale positions"
        assert not torch.equal(consumed[0][1][3], consumed[-1][1][3]), "graph observed stale input_ids"
        assert fixed_pointers == [pointers(r) for r in (baseline, changed)], "graph source pointers changed"
        result["consecutive_event_and_fixed_graph_consumer"] = True
        result["graph_consumers"] = ["positions", "seq_lens", "slot_mapping", "input_ids"]
        result["graph_input_ids_changed_across_steps"] = True
        # Scope fallback must submit no candidate copy and preserve all storage.
        state = getattr(changed, runtime._STATE)
        selected = state["selected"]
        changed.use_async_spec_decode = True
        assert runtime.try_cpu_metadata(changed, np.array([1], dtype=np.int64),
                                        np.array([0], dtype=np.int64), np.array([1], dtype=np.int32)) is False
        assert state["selected"] == selected
        changed.use_async_spec_decode = False
        cpu_after, gpu_after = torch.get_rng_state(), torch.cuda.get_rng_state()
        result["rng_unchanged"] = {"CPU": bool(torch.equal(cpu_rng, cpu_after)),
                                   "GPU": bool(torch.equal(gpu_rng, gpu_after))}
        assert all(result["rng_unchanged"].values())
        result["rng_sha256"] = {"CPU_before": hashlib.sha256(cpu_rng.numpy().tobytes()).hexdigest(),
                                "CPU_after": hashlib.sha256(cpu_after.numpy().tobytes()).hexdigest(),
                                "GPU_before": hashlib.sha256(gpu_rng.numpy().tobytes()).hexdigest(),
                                "GPU_after": hashlib.sha256(gpu_after.numpy().tobytes()).hexdigest()}
        result["selected"] = selection_counts(changed, runtime, asynchronous, gather)
        result["timing"] = "not measured: correctness-only dead CPU gather gate"
        result["status"] = "pass"
    except BaseException:
        result["status"], result["error"] = "reject", traceback.format_exc()
        traceback.print_exc()
    write(run / "results.json", result)
    return 0 if result["status"] == "pass" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--runtime-path", type=Path)
    parser.add_argument("--async-runtime-path", type=Path)
    parser.add_argument("--gather-runtime-path", type=Path)
    parser.add_argument("--runner-path", type=Path)
    parser.add_argument("--installed-root", type=Path, default=Path("/usr/local/lib/python3.12/site-packages"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir)
    if any(value is None for value in (args.runtime_path, args.async_runtime_path, args.runner_path, args.gather_runtime_path)):
        parser.error("controller requires exact combined runner, gather candidate and both unchanged helpers")
    import fcntl
    import validate_block_table_candidate as owner

    root, run = owner.ROOT.resolve(), args.run_dir.resolve()
    if run == root or not run.is_relative_to(root):
        raise RuntimeError("new run directory must be below experiment root")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {"started_utc": utc(), "pid": os.getpid(), "command": [sys.executable, *sys.argv],
                "command_shell": shlex.join([sys.executable, *sys.argv]), "kind": "exact-method-no-weights-dead-cpu-gather-correctness-only"}
    lock = child = monitor = monitor_log = None
    status = 1
    def interrupted(signum, frame):
        raise SystemExit("controller interrupted: " + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    try:
        lock = (root / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest["preflight"] = owner.preflight(args.ixsmi)
        pre = subprocess.check_output([args.ixsmi], text=True, timeout=10)
        (run / "preflight-ixsmi.txt").write_text(pre, encoding="utf-8")
        if "No running processes found" not in pre:
            raise RuntimeError("device process remains")
        source = run / "source"
        source.mkdir()
        assets = {"gate.py": Path(__file__), "runtime.py": args.runtime_path,
                  "async-runtime.py": args.async_runtime_path, "runner.py": args.runner_path,
                  "gather-runtime.py": args.gather_runtime_path,
                  "validate_block_table_candidate.py": Path(owner.__file__),
                  "monitor_gpu.sh": root / "scripts/monitor_gpu.sh"}
        assets.update({Path(name).name: args.installed_root / name for name in (
            "vllm/v1/worker/gpu_input_batch.py", "vllm/v1/utils.py", "vllm/v1/worker/block_table.py")})
        for label, path in assets.items():
            (source / label).write_bytes(path.read_bytes())
        for label, expected in EXPECTED.items():
            if digest(source / label) != expected:
                raise RuntimeError("unaudited source: " + label)
        transformer = load("decode_gather_controller", source / "gather-runtime.py")
        candidate = transformer.transform((source / "runner.py").read_bytes())
        (source / "runner-combined.py").write_bytes(candidate)
        manifest["candidate_runner_sha256"] = digest(source / "runner-combined.py")
        assert transformer.reverse(candidate) == (source / "runner.py").read_bytes()
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["packages"] = {}
        for package in ("torch", "vllm", "FlagGems", "numpy", "SQLAlchemy", "flagtree"):
            try:
                manifest["packages"][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][package] = "unavailable"
        command = [sys.executable, str(source / "gate.py"), "--worker", "--run-dir", str(run)]
        manifest["worker_command"] = command
        with (run / "worker.log").open("x") as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
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
                post = subprocess.check_output([args.ixsmi], text=True, timeout=10)
                (run / "postflight-ixsmi.txt").write_text(post, encoding="utf-8")
                if "No running processes found" not in post:
                    raise RuntimeError("device process remains after child exit")
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
