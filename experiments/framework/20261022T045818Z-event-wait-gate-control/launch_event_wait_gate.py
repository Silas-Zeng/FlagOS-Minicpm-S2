#!/usr/bin/env python3
"""独立Event等待API门外层；不导入Torch/加载库，不编译或启动模型服务。"""
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import traceback

ROOT = Path("/workspace/experiments/minicpm-s2")
DB = Path("/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db")
# archived name: (ROOT/scripts input name, reviewed SHA256)
SOURCES = {
    "gate.py": ("validate_event_wait_gate.py", "67090baad306b95679717a0f4b3e97d7a16abc9815317d3c885102ccac1d32ae"),
    "event-wait-contract.json": ("event-wait-contract.json", "41ba9a3bcc40ef826ac9fa350be134aa66a86a4e3cab4aa5c9234624c3bfe5eb"),
}
HELPERS = {
    "monitor_gpu.sh": "af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a",
    "snapshot_tuning_db.py": "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2",
}


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.write("\n")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def regular(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("要求真实regular file：" + str(path))
    return path


def checked_assets():
    for name, expected in [(item[0], item[1]) for item in SOURCES.values()] + list(HELPERS.items()):
        path = regular(ROOT / "scripts" / name)
        if len(expected) != 64 or sha(path) != expected:
            raise RuntimeError("素材未审或变化：" + name)


def command(control, label, argv, timeout=30):
    """保留stdout/stderr/exit，包括编译失败；不执行shell字符串。"""
    write(control / (label + "-command.json"), {"argv": argv, "shell": shlex.join(argv), "started_utc": utc()})
    with (control / (label + ".stdout")).open("xb") as out, (control / (label + ".stderr")).open("xb") as err:
        try:
            result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err, timeout=timeout)
        except BaseException:
            write(control / (label + "-result.json"), {"finished_utc": utc(), "exception": traceback.format_exc()})
            raise
    write(control / (label + "-result.json"), {"finished_utc": utc(), "returncode": result.returncode})
    if result.returncode:
        raise RuntimeError(label + "失败，exit=" + str(result.returncode))
    return (control / (label + ".stdout")).read_text(encoding="utf-8", errors="replace")


def idle(control, label):
    query = command(control, label + "-query", ["ixsmi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"])
    table = command(control, label + "-table", ["ixsmi"])
    sockets = []
    for family, host in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            code = sock.connect_ex((host, 9031))
            sockets.append({"host": host, "port": 9031, "connect_ex": code})
            if code == 0:
                raise RuntimeError("9031仍开放：" + host)
    result = {"recorded_utc": utc(), "query": query, "ixsmi": table, "sockets": sockets}
    write(control / (label + ".json"), result)
    if (query.strip() != "68, 0" or "No running processes found" not in table
            or "BI-V150" not in table or "32768MiB" not in table):
        raise RuntimeError("设备非已审单BI-V150/32GiB或忙")
    return result


def source_map(source):
    if any(not p.is_file() or p.is_symlink() for p in source.iterdir()):
        raise RuntimeError("source含目录/链接/非regular file")
    return {p.name: sha(p) for p in sorted(source.iterdir())}


def snapshot(control, label):
    command(control, label, [sys.executable, str(control / "snapshot_tuning_db.py"),
                            "--database", str(DB), "--output", str(control / label)])
    manifest = read(control / label / "manifest.json")
    if manifest.get("status") != "complete" or sha(control / label / "snapshot.sqlite") != manifest.get("snapshot_sha256"):
        raise RuntimeError(label + "快照未完整或物理SHA不符")
    return {k: manifest[k] for k in ("snapshot_sha256", "schema_sha256", "logical_content_sha256", "table_count", "row_count")}


def environment():
    packages = {}
    for name in ("torch",):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    cgroup = {}
    for name in ("cpu/cpu.cfs_quota_us", "cpu/cpu.cfs_period_us", "cpu/cpu.stat",
                 "memory/memory.limit_in_bytes", "memory/memory.usage_in_bytes", "memory/memory.stat",
                 "cpu.max", "cpu.stat", "memory.max", "memory.current"):
        path = Path("/sys/fs/cgroup") / name
        if path.is_file():
            cgroup[str(path)] = path.read_text()
    return {"recorded_utc": utc(), "python": sys.version, "platform": platform.platform(), "packages": packages,
            "env": {k: os.environ.get(k) for k in ("PATH", "LD_LIBRARY_PATH", "CUDA_VISIBLE_DEVICES", "PYTHONDONTWRITEBYTECODE")},
            "cgroup_observation_not_peak": cgroup}


def stop(process):
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


def controller(run, control):
    import fcntl
    if (run.parent != ROOT / "framework" or control != run.with_name(run.name + "-control")
            or not run.name.endswith("-event-wait-gate") or not run.is_dir() or not control.is_dir()
            or run.is_symlink() or control.is_symlink()):
        raise ValueError("只接受本launcher新建的ROOT/framework直系run/control")
    manifest = {"kind": "独立Event默认/typed/blocking等待API门，非模型服务性能", "started_utc": utc(),
                "controller_pid": os.getpid(), "run": str(run), "control": str(control),
                "controller_sha256": sha(Path(__file__)), "command": [sys.executable, *sys.argv]}
    write(control / "started.json", manifest)
    child = monitor = lock = None
    logs = []
    status = 1
    expected_source = None
    locked = False

    def interrupted(signum, frame):
        raise SystemExit("controller signal " + str(signum))

    signal.signal(signal.SIGTERM, interrupted)
    try:
        checked_assets()
        if any(k in os.environ for k in ("MINICPM_NATIVE_PROFILE_EVENTS", "MINICPM_DECODE_GAP_RUN_DIR")):
            raise RuntimeError("禁止继承profiler环境")
        lock = (ROOT / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
        manifest["preflight_before_preparation"] = idle(control, "preflight-before-preparation")
        source = run / "source"
        source.mkdir()
        for target, (name, _) in SOURCES.items():
            shutil.copyfile(ROOT / "scripts" / name, source / target)
        if any(sha(source / name) != expected for name, (_, expected) in SOURCES.items()):
            raise RuntimeError("归档素材SHA不符")
        for name in HELPERS:
            shutil.copyfile(ROOT / "scripts" / name, control / name)
        manifest["environment"] = environment()
        write(control / "environment-before.json", manifest["environment"])
        contract = read(source / "event-wait-contract.json")
        identities = []
        for item in contract["files"]:
            if item["status"] != "read_only":
                continue  # wheel缺失cpp按原取证记录，不补上游或假定绑定语义。
            path = regular(Path(item["path"]))
            if sha(path) != item["sha256"] or str(path.resolve()) != item["resolved"]:
                raise RuntimeError("事件契约实际源变化：" + str(path))
            identities.append({"path": str(path), "resolved": str(path.resolve()), "sha256": item["sha256"]})
        write(control / "event-source-identity.json", {"files": identities,
              "missing_in_original_collection": contract["missing_paths"],
              "semantic_pass_claimed": False})
        expected_source = source_map(source)
        write(control / "source-sha256.json", expected_source)
        manifest["db_before"] = snapshot(control, "db-before")
        checked_assets()
        if source_map(source) != expected_source:
            raise RuntimeError("准备期间归档source变化")
        manifest["preflight_before_worker"] = idle(control, "preflight-before-worker")
        worker_argv = [sys.executable, str(source / "gate.py"), "--device-worker", "--output-dir", str(run),
                       "--source-dir", str(source)]
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        write(control / "worker-command.json", {"argv": worker_argv, "shell": shlex.join(worker_argv), "env": {"PYTHONDONTWRITEBYTECODE": "1"}})
        manifest["worker_command"] = worker_argv
        out = (run / "worker.log").open("xb")
        logs.append(out)
        child = subprocess.Popen(worker_argv, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        manifest["worker_pid"] = child.pid
        (run / "worker.pid").write_text(str(child.pid) + "\n")
        out = (run / "monitor.log").open("xb")
        logs.append(out)
        monitor = subprocess.Popen(["bash", str(control / "monitor_gpu.sh"), str(child.pid), str(run / "gpu.csv")],
                                   stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
        manifest["monitor_pid"] = monitor.pid
        manifest["worker_exit_code"] = child.wait(timeout=300)
        status = manifest["worker_exit_code"]
        if status == 0 and not (run / "results.json").is_file():
            raise RuntimeError("worker exit0但无results原件")
    except BaseException:
        status = 1
        manifest["controller_error"] = traceback.format_exc()
        traceback.print_exc()
    finally:
        for process in (child, monitor):
            try:
                stop(process)
            except BaseException:
                manifest.setdefault("cleanup_errors", []).append(traceback.format_exc())
                status = 1
        for out in logs:
            out.close()
        if locked:
            for label, action in (("db_after", lambda: snapshot(control, "db-after")),
                                  ("postflight", lambda: idle(control, "postflight")),
                                  ("environment_after", environment)):
                try:
                    manifest[label] = action()
                except BaseException:
                    manifest[label + "_error"] = traceback.format_exc()
                    status = 1
            try:
                if (run / "source").is_dir():
                    actual = source_map(run / "source")
                    write(control / "source-post-sha256.json", actual)
                    manifest["source_unchanged"] = expected_source is not None and actual == expected_source
                    if expected_source is not None and not manifest["source_unchanged"]:
                        raise RuntimeError("运行后source变化")
            except BaseException:
                manifest["source_post_error"] = traceback.format_exc()
                status = 1
        manifest.update(finished_utc=utc(), exit_code=status)
        write(run / "manifest.json", manifest)
        (run / "exit-code").write_text(str(status) + "\n")
        (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n")
        # 原件自身不修改；seal仅列本轮run/control完整regular-file字节，不自引用。
        sys.stdout.flush()
        sys.stderr.flush()
        files = {}
        for directory in (run, control):
            for path in sorted(directory.rglob("*")):
                if path.is_symlink():
                    raise RuntimeError("本门封存禁止symlink：" + str(path))
                if path.is_file():
                    files[str(path.relative_to(run.parent))] = {"sha256": sha(path), "bytes": path.stat().st_size}
        write(control / "seal.json", {"kind": "本轮API门完整字节索引，不代表设备正确性通过", "recorded_utc": utc(),
                                     "run": str(run), "control": str(control), "exit_code": status, "files": files,
                                     "collect": [str(run), str(control)], "limits": ["worker结果/失败原件另审；exit0不冒充服务或准确率。", "事件API微门，不是模型服务性能；源声明不能证明驱动真实睡眠。"]})
        if lock is not None:
            lock.close()
    return status


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--controller":
        return controller(Path(sys.argv[2]), Path(sys.argv[3]))
    if len(sys.argv) != 1:
        raise ValueError("无参启动唯一UTC门；不接受源/参数覆盖")
    checked_assets()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = ROOT / "framework" / (stamp + "-event-wait-gate")
    control = run.with_name(run.name + "-control")
    run.mkdir(exist_ok=False)
    control.mkdir(exist_ok=False)
    archived = control / Path(__file__).name
    shutil.copyfile(__file__, archived)
    argv = [sys.executable, str(archived), "--controller", str(run), str(control)]
    write(control / "launch-command.json", {"argv": [sys.executable, *sys.argv], "controller_argv": argv, "wrapper_sha256": sha(archived)})
    with (control / "runner.log").open("xb") as out:
        process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    (control / "runner.pid").write_text(str(process.pid) + "\n")
    print(json.dumps({"run": str(run), "control": str(control), "runner_pid": process.pid, "collect": [str(run), str(control)]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
