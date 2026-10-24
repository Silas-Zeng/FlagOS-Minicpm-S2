#!/usr/bin/env python3
"""原单卡 owner 的 baseline-only ixsys 诊断分支，不产生性能比较。"""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import traceback
from validate_hidden_row_gather import digest, utc, write
EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"
EXPECTED_C3 = "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42"
ASSET_PINS = {'worker.py': '900ee5702b177b86922b0d6be8bf6e85f900e5b6531bdf31b448f24246abfadb', 'fixture.py': '60d99d1d24cbbb91f0ad0a2eca13abfe1760ae551de01904801874561d3710a5'}


def completion_status(ixsys_status, result):
    """ixsys exit 0 不能替代 worker 完整完成；缺失或不完整都 fail closed。"""
    if not isinstance(result, dict):
        return 1, {"complete": False, "reason": "worker result is not an object"}
    profile, checks = result.get("profile"), result.get("checks")
    expected_checks = {"entire_kv_bits_unchanged", "rng_unchanged", "valid_output_finite",
                       "padding_untouched", "same_q_repeat_output_bits"}
    complete = (result.get("status") == "diagnostic_complete_no_performance_verdict"
        and isinstance(profile, dict)
        and profile.get("start_returned") is True and profile.get("stop_returned") is True
        and type(profile.get("completed_calls")) is int and profile["completed_calls"] == 128
        and isinstance(checks, dict) and expected_checks <= checks.keys()
        and all(value is True for value in checks.values())
        and result.get("device_settled") is True and result.get("entry_bindings_restored") is True)
    status = 0 if ixsys_status == 0 and complete else (ixsys_status if ixsys_status != 0 else 1)
    return status, {"complete": complete, "worker_status": result.get("status"),
                    "profile": profile, "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--runtime-path", type=Path)
    parser.add_argument("--mixed-path", type=Path)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    args = parser.parse_args()
    if any(path is None for path in (args.runtime_path, args.mixed_path)):
        parser.error("controller requires original C2 and C3 paths")
    import fcntl
    import validate_block_table_candidate as owner
    import validate_hidden_row_gather as utilities
    import bench_attention_dispatch as shared

    root, run = owner.ROOT.resolve(), args.run_dir.resolve()
    if not run.is_relative_to(root) or run == root:
        raise ValueError("run must be a new child of experiment root")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {"started_utc": utc(), "pid": os.getpid(), "command": [sys.executable, *sys.argv],
                "command_shell": shlex.join([sys.executable, *sys.argv]),
                "kind": "baseline-only D1/P2047 KV16K hardware-metrics diagnostic; no performance verdict",
                "profile_calls": 128,
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
        base_path = os.environ["PYTHONPATH"].split(os.pathsep)[0]
        if not base_path:
            raise RuntimeError("PYTHONPATH must begin with the clean base source directory")
        base_runner = Path(base_path) / "vllm_fl/worker/model_runner.py"
        manifest["base_runner_sha256"] = digest(base_runner)
        if manifest["base_runner_sha256"] != "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141":
            raise RuntimeError("gate requires the clean combined 6f runner")
        manifest["preflight"] = owner.preflight(args.ixsmi)
        gpu = subprocess.check_output([args.ixsmi], text=True, timeout=10)
        (run / "preflight-ixsmi.txt").write_text(gpu, encoding="utf-8")
        if "No running processes found" not in gpu:
            raise RuntimeError("accelerator process already active")
        source = run / "source"
        source.mkdir()
        for name, path in (("controller.py", Path(__file__)), ("runtime.py", args.runtime_path),
                           ("mixed.py", args.mixed_path),
                           ("worker.py", Path(__file__).with_name("worker.py")),
                           ("fixture.py", Path(__file__).with_name("fixture.py")),
                           ("asset-pins.json", Path(__file__).with_name("asset-pins.json")),
                           ("validate_hidden_row_gather.py", Path(utilities.__file__)),
                           ("bench_attention_dispatch.py", Path(shared.__file__)),
                           ("validate_block_table_candidate.py", Path(owner.__file__)),
                           ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh")):
            (source / name).write_bytes(path.read_bytes())
        for name, expected in (("runtime.py", EXPECTED_C2), ("mixed.py", EXPECTED_C3), *ASSET_PINS.items()):
            if expected is None or digest(source / name) != expected:
                raise RuntimeError("unaudited baseline diagnostic asset: " + name)
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["packages"] = {}
        for package in ("torch", "vllm", "FlagGems", "SQLAlchemy"):
            try:
                manifest["packages"][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][package] = "unavailable"
        if json.loads((source / "asset-pins.json").read_text()) != ASSET_PINS:
            raise RuntimeError("worker asset manifest drift")
        ixsys = "/usr/local/corex-4.5.0/bin/ixsys"
        manifest["ixsys"] = {"path": ixsys, "sha256": digest(Path(ixsys))}
        manifest["worker_command"] = [ixsys, "-t", "cuda", "--profile-from-start", "off",
            "--gpu-metrics-device", "0", "--gpu-metrics-set", "3", "--gpu-metrics-frequency", "500",
            "-o", str(run / "native-trace.json"), sys.executable, str(source / "worker.py"),
            "--worker", "--run-dir", str(run), "--model", str(args.model)]
        write(run / "manifest.json", manifest)
        with (run / "worker.log").open("x") as log:
            child = subprocess.Popen(manifest["worker_command"], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            manifest["worker_pid"] = child.pid
            monitor_log = (run / "monitor.log").open("x")
            monitor = subprocess.Popen(["bash", str(source / "monitor_gpu.sh"), str(child.pid), str(run / "gpu.csv")],
                                       stdout=monitor_log, stderr=subprocess.STDOUT, start_new_session=True)
            write(run / "manifest.json", manifest)
            ixsys_status = child.wait(timeout=300)
            manifest["ixsys_exit_code"] = ixsys_status
            status = ixsys_status if ixsys_status != 0 else 1
            worker_result = json.loads((run / "results.json").read_text(encoding="utf-8"))
            status, manifest["worker_completion"] = completion_status(ixsys_status, worker_result)
    except BaseException:
        status = 1
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
