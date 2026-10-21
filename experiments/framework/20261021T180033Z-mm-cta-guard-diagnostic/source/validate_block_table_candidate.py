#!/usr/bin/env python3
"""Small, device-owned BlockTable metadata gate; no model and no E2E claim.

Example (run only after the service exits):
  python validate_block_table_candidate.py --run-dir <new UTC run directory> \
      --candidate-path <audited biv150_block_table.py> [--graph] [--microtiming]

The default gate is 32 deterministic H2D/state-machine steps. Optional timing
is a stable-table best case, with no row mutation inside the measured loop.
It is not serving throughput; H2D can overlap real CPU input preparation.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import socket
import statistics
import subprocess
import sys
import time
import traceback


ROOT = Path("/workspace/experiments/minicpm-s2")
IXSMI = "/usr/local/corex-4.5.0/bin/ixsmi"


def utc():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight(ixsmi):
    # This function uses no torch/vLLM imports and initializes no CUDA context.
    for family, address in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        try:
            with socket.socket(family) as sock:
                sock.settimeout(1)
                if sock.connect_ex((address, 9031)) == 0:
                    raise RuntimeError("port 9031 occupied")
        except OSError as exc:
            if family == socket.AF_INET:
                raise RuntimeError("could not verify port 9031") from exc
    output = subprocess.check_output(
        [ixsmi, "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        text=True, timeout=10,
    )
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1 or not lines[0].isdigit():
        raise RuntimeError(f"expected one accelerator and numeric free MiB: {lines!r}")
    free_mib = int(lines[0])
    if free_mib < 30000:
        raise RuntimeError(f"accelerator occupied: free MiB={free_mib}, required>=30000")
    return {"checked_utc": utc(), "port_9031": "free", "free_mib": free_mib}


def load_candidate(path):
    spec = importlib.util.spec_from_file_location("block_table_candidate_validation", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load candidate at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_table(cls, torch, batch):
    return cls(
        block_size=16,
        max_num_reqs=batch,
        max_num_blocks_per_req=8192,
        max_num_batched_tokens=64,
        pin_memory=True,
        device=torch.device("cuda:0"),
        kernel_block_size=16,
        cp_kv_cache_interleave_size=1,
    )


class ReferenceRunner:
    def __init__(self, table):
        self.table = table

    def _prepare_inputs(self, num_reqs):
        self.table.commit_block_table(num_reqs)


class CandidateRunner(ReferenceRunner):
    pass


def checked_state(torch, reference, table, active, position, pad_slot_id, pointers):
    for obj, pointer in zip((reference, table), pointers):
        assert (obj.block_table.gpu.data_ptr(), obj.block_table.gpu.stride(),
                obj.slot_mapping.gpu.data_ptr()) == pointer, "device storage changed"
        assert torch.equal(obj.block_table.gpu[:active].cpu(), obj.block_table.cpu[:active]), \
            "active block table differs from host"
    assert torch.equal(reference.block_table.cpu, table.block_table.cpu), "host table mismatch"
    assert (reference.num_blocks_per_row == table.num_blocks_per_row).all(), "block counts mismatch"
    expected = [
        int(reference.block_table.np[row, position // 16]) * 16 + position % 16
        for row in range(active)
    ] + [pad_slot_id] * (64 - active)
    actual_reference = reference.slot_mapping.gpu.cpu().tolist()
    actual_candidate = table.slot_mapping.gpu.cpu().tolist()
    assert actual_reference == expected, "original slot mapping differs from CPU oracle"
    assert actual_candidate == expected, "candidate slot mapping differs from CPU oracle"


def state_machine(torch, original_cls, candidate_cls, module, candidate, args, result):
    reference = make_table(original_cls, torch, 8)
    table = make_table(candidate_cls, torch, 8)
    reference_runner, runner = ReferenceRunner(reference), CandidateRunner(table)
    q_cpu = torch.empty(9, dtype=torch.int32, pin_memory=True)
    p_cpu = torch.empty(8, dtype=torch.int64, pin_memory=True)
    q_gpu = torch.empty(9, dtype=torch.int32, device="cuda")
    p_gpu = torch.empty(8, dtype=torch.int64, device="cuda")
    pointers = [
        (obj.block_table.gpu.data_ptr(), obj.block_table.gpu.stride(), obj.slot_mapping.gpu.data_ptr())
        for obj in (reference, table)
    ]
    ready = torch.cuda.Event()
    ready.record()
    next_block = 100

    def ids(count):
        nonlocal next_block
        values = list(range(next_block, next_block + count))
        next_block += count
        return values

    checks = result["state_machine"] = []
    for step in range(32):
        # Every host-source mutation waits for the previous DMA/kernel users.
        ready.synchronize()
        active = 6 if 16 <= step < 24 else 4
        position = 14 + step
        needed = position // 16 + 1
        operations = []

        def both(name, *values):
            for obj in (reference, table):
                getattr(obj, name)(*values)
            operations.append(name)

        if step == 0:
            for row in range(8):
                both("add_row", ids(1), row)
        if step == 6:
            both("move_row", 0, 3)
        if step == 10:
            both("swap_row", 1, 2)
        if step == 12:
            both("clear_row", 2)
            both("add_row", ids(needed), 2)
        if step == 14:
            both("add_row", ids(needed), 6)  # dirty inactive row survives commit(4).
        if step == 16:
            for row in (4, 5):
                both("add_row", ids(needed), row)
        if step == 20:
            counts_before_clear = reference.num_blocks_per_row.copy()
            both("clear")
            assert (reference.num_blocks_per_row == counts_before_clear).all()
            assert (table.num_blocks_per_row == counts_before_clear).all()
            for row in range(8):
                both("add_row", ids(needed), row)
        if step == 24:
            for obj in (reference, table):
                obj.block_table.gpu[4:8].fill_(0)  # external graph-padding write.
            operations.append("external_device_padding")
        if step == 25:
            # No scope: recover even non-dirty inactive rows after padding.
            both("commit_block_table", 8)
        if step == 26:
            both("add_row", ids(needed), 3)
        if step == 28:
            both("move_row", 6, 3)  # reactivate an inactive/prefix-reused row.
        if step == 30:
            both("swap_row", 0, 3)
        for row in range(active):
            missing = needed - int(reference.num_blocks_per_row[row])
            if missing > 0:
                both("append_row", ids(missing), row)
        q_cpu[:active + 1].copy_(torch.arange(active + 1, dtype=torch.int32))
        p_cpu[:active].fill_(position)
        reference_runner._prepare_inputs(active)
        runner._prepare_inputs(active)
        q_gpu[:active + 1].copy_(q_cpu[:active + 1], non_blocking=True)
        p_gpu[:active].copy_(p_cpu[:active], non_blocking=True)
        for obj in (reference, table):
            obj.compute_slot_mapping(active, q_gpu[:active + 1], p_gpu[:active])
        ready.record()
        ready.synchronize()
        checked_state(torch, reference, table, active, position, module.PAD_SLOT_ID, pointers)
        if step == 14:
            assert table._biv150_dirty_rows[6], "inactive dirty state was lost"
        if step == 25:
            assert torch.equal(reference.block_table.gpu.cpu(), reference.block_table.cpu)
            assert torch.equal(table.block_table.gpu.cpu(), table.block_table.cpu)
        checks.append({"step": step, "active": active, "position": position,
                       "operations": operations, "status": "pass"})
        result["state_machine_stats"] = candidate.snapshot_stats(table)

    if args.graph:
        # Warm the exact kernels on a side stream before capturing only the
        # slot-mapping consumers. CPU->GPU copies remain outside the graph.
        ready.synchronize()
        warm_stream = torch.cuda.Stream()
        warm_stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(warm_stream):
            for _ in range(2):
                for obj in (reference, table):
                    obj.compute_slot_mapping(4, q_gpu[:5], p_gpu[:4])
        torch.cuda.current_stream().wait_stream(warm_stream)
        torch.cuda.synchronize()
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            for obj in (reference, table):
                obj.compute_slot_mapping(4, q_gpu[:5], p_gpu[:4])
        graph_checks = result["graph"] = []
        for replay in range(3):
            ready.synchronize()
            replacement = ids(3)
            for obj in (reference, table):
                obj.add_row(replacement, 0)
            reference_runner._prepare_inputs(4)
            runner._prepare_inputs(4)
            graph.replay()
            ready.record()
            ready.synchronize()
            checked_state(torch, reference, table, 4, 45, module.PAD_SLOT_ID, pointers)
            graph_checks.append({"replay": replay, "status": "pass"})
    else:
        result["graph"] = "not requested"
    result["state_machine_stats"] = candidate.snapshot_stats(table)


def microtiming(torch, original_cls, candidate_cls, candidate, result):
    records = result["microtiming"] = []
    for batch in (8, 16, 64):
        reference = make_table(original_cls, torch, batch)
        table = make_table(candidate_cls, torch, batch)
        runners = {"original": ReferenceRunner(reference), "candidate": CandidateRunner(table)}
        ready = torch.cuda.Event()
        ready.record()
        ready.synchronize()
        for row in range(batch):
            for obj in (reference, table):
                obj.add_row([100 + row], row)
        for _ in range(4):
            for runner in runners.values():
                runner._prepare_inputs(batch)
        ready.record()
        ready.synchronize()
        # The host tables are immutable throughout every measured loop.
        for repeat in range(3):
            order = ("original", "candidate") if repeat % 2 == 0 else ("candidate", "original")
            for name in order:
                ready.synchronize()
                start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                stats_before = candidate.snapshot_stats(table)
                wall_start = time.perf_counter()
                start.record()
                for _ in range(64):
                    runners[name]._prepare_inputs(batch)
                end.record()
                end.synchronize()
                records.append({
                    "batch": batch, "repeat": repeat, "order": list(order), "implementation": name,
                    "steps": 64, "wall_us_per_commit": (time.perf_counter() - wall_start) * 1e6 / 64,
                    "stream_interval_us_per_commit": start.elapsed_time(end) * 1000 / 64,
                    "candidate_stats_before": stats_before,
                    "candidate_stats_after": candidate.snapshot_stats(table),
                })
        result.setdefault("microtiming_medians", []).append({
            "batch": batch,
            "wall_us_per_commit": {
                name: statistics.median(r["wall_us_per_commit"] for r in records
                                        if r["batch"] == batch and r["implementation"] == name)
                for name in runners
            },
        })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--candidate-path", required=True, type=Path)
    parser.add_argument("--ixsmi", default=IXSMI)
    parser.add_argument("--graph", action="store_true")
    parser.add_argument("--microtiming", action="store_true")
    args = parser.parse_args()
    run, candidate_path = args.run_dir.resolve(), args.candidate_path.resolve()
    if not run.is_relative_to(ROOT.resolve()) or run == ROOT.resolve():
        raise ValueError("--run-dir must be a new directory inside the experiment workspace")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {
        "run_id_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
        "kind": "isolated metadata correctness and optional microtiming; not E2E or official score",
        "started_utc": utc(), "pid": os.getpid(), "command": shlex.join(sys.argv),
        "run_dir": str(run), "candidate_path": str(candidate_path),
        "host": platform.platform(), "python": sys.version,
        "graph_requested": args.graph, "microtiming_requested": args.microtiming,
        "lock_path": str(ROOT / "framework-device.lock"),
    }
    result = {
        "status": "started",
        "limitations": [
            "No model, scheduler, logits, accuracy benchmark, or official benchmark is loaded.",
            "Stable-table timings are a best case and omit row-mutation work.",
            "CUDA event intervals can include host submission gaps; they are not pure DMA latency.",
            "Real H2D can overlap CPU preparation; these timings do not establish E2E throughput gains.",
            "Small stable improvements remain useful; this gate imposes no percentage rejection threshold.",
        ],
    }
    write_json(run / "manifest.json", manifest)
    write_json(run / "result.json", result)
    lock, torch = None, None
    status = 1
    try:
        if not __debug__:
            raise RuntimeError("validation requires Python assertions; do not use -O")
        lock = (ROOT / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest["lock_acquired_utc"] = utc()
        manifest["preflight"] = preflight(args.ixsmi)
        # Imports that could initialize the runtime occur only under the lock,
        # after the service/memory gate. No service or GPU job is launched here.
        torch = importlib.import_module("torch")
        module = importlib.import_module("vllm.v1.worker.block_table")
        candidate = load_candidate(candidate_path)
        source_dir = run / "source"
        source_dir.mkdir()
        for label, path in (("validator.py", Path(__file__).resolve()),
                            ("candidate.py", candidate_path),
                            ("block_table.py", Path(module.__file__))):
            data = path.read_bytes()
            (source_dir / label).write_bytes(data)
            manifest.setdefault("source_sha256", {})[str(path)] = hashlib.sha256(data).hexdigest()
        manifest["packages"] = {
            name: importlib.metadata.version(name) for name in ("torch", "vllm", "vllm-plugin-fl")
        }
        write_json(run / "manifest.json", manifest)
        original_cls = module.BlockTable
        if getattr(original_cls, "_biv150_dirty_commit_patch", False):
            raise RuntimeError("original BlockTable already patched; cannot build an independent control")
        candidate_cls = candidate.install(CandidateRunner, module=module)
        torch.cuda.set_device(0)
        torch.cuda.init()
        manifest["device"] = {"name": torch.cuda.get_device_name(0),
                              "visible_count": torch.cuda.device_count(),
                              "total_memory": torch.cuda.get_device_properties(0).total_memory}
        if manifest["device"]["visible_count"] != 1:
            raise RuntimeError("expected exactly one visible accelerator")
        write_json(run / "manifest.json", manifest)
        state_machine(torch, original_cls, candidate_cls, module, candidate, args, result)
        write_json(run / "result.json", result)
        if args.microtiming:
            microtiming(torch, original_cls, candidate_cls, candidate, result)
        else:
            result["microtiming"] = "not requested"
        torch.cuda.synchronize()
        result["status"] = "pass"
        status = 0
    except BaseException as exc:
        result.update(status="failed", error_type=type(exc).__name__, error=str(exc),
                      traceback=traceback.format_exc())
    finally:
        # Keep ownership until all submitted work finishes, also on exceptions.
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
            except BaseException as exc:
                result["shutdown_error"] = repr(exc)
                result["status"] = "failed"
                status = 1
        manifest["finished_utc"] = utc()
        result["finished_utc"] = utc()
        write_json(run / "manifest.json", manifest)
        write_json(run / "result.json", result)
        if lock is not None:
            lock.close()
    print(json.dumps({"status": result["status"], "run_dir": str(run),
                      "state_machine_stats": result.get("state_machine_stats"),
                      "microtiming_medians": result.get("microtiming_medians"),
                      "error": result.get("error")}, ensure_ascii=False))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
