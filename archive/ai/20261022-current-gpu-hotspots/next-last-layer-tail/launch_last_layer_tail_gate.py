#!/usr/bin/env python3
"""末层局部尾段门外层；不导入Torch，不编译或启动模型服务。"""
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
# 完整干净6f基点固定；不接C3views/gather/其它候选。
BASE = ROOT / "code/cpu-combination-combined-20261022T100830Z"
MODEL = Path("/workspace/MiniCPM5-2B")
REFERENCE = ROOT / "scripts/cpu-combination-base-sha256.json"
REFERENCE_SHA = "cd506fa2ed386df5961a188702a512351829cca59b684f2d47897e57e298c676"
SOURCES = {
    "gate.py": ("validate_last_layer_tail.py", "25d3e9cb194b9a6504db7f678f05d0f2113495e5bdd4d3829b82d813f153b650"),
    "last_layer_tail.py": ("last_layer_tail.py", "99d5a8c86dac67b7a2c0029842576fbd1439060525d4c6789b0ddd32703fc9ec"),
}
INSTALLED = {
    "llama.py": (Path("/usr/local/lib/python3.12/site-packages/vllm/model_executor/models/llama.py"), "1e1003454985bf86d3868a7755bcf5324676881548b3895809edf0b76698d384"),
    "linear.py": (Path("/usr/local/lib/python3.12/site-packages/vllm/model_executor/layers/linear.py"), "0bd60103d85d7183791077c46e0770d0a2adc8e8811b162b9084c3cbe92ba662"),
    "layernorm.py": (Path("/usr/local/lib/python3.12/site-packages/vllm/model_executor/layers/layernorm.py"), "696615d858292fea7a2942480803cd4c7d2d1e88d818bfe5cd9d695ac464f37c"),
    "activation.py": (Path("/usr/local/lib/python3.12/site-packages/vllm/model_executor/layers/activation.py"), "757209cef4b5cc091d29d95b4a6b29f2511984110c9b66810c760d4499cb156c"),
    "model-config.json": (MODEL / "config.json", "59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180"),
}
BASE_OVERLAY = {
    "vllm_fl/worker/model_runner.py": "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141",
    "vllm_fl/patches/biv150_cpu_metadata.py": "0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f",
    "vllm_fl/patches/biv150_async_token_update.py": "1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc",
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
    for name, (path, expected) in INSTALLED.items():
        if sha(regular(path)) != expected:
            raise RuntimeError("actual尾段源码或模型配置变化：" + name)
    if sha(regular(REFERENCE)) != REFERENCE_SHA:
        raise RuntimeError("完整基点410参考变化")


def plugin_map(folder):
    resolved = folder.resolve(strict=True)
    if folder.is_symlink() or not folder.is_dir():
        raise RuntimeError("基点必须真实目录")
    result = {}
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder)
        if any(part in (".git", "__pycache__") for part in rel.parts) or path.suffix in (".pyc", ".pyo"):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(resolved):
                raise RuntimeError("拒绝外部或目录别名：" + str(rel))
        if path.is_file():
            result[rel.as_posix()] = sha(path)
    return result


def checked_base():
    expected = read(REFERENCE)
    if len(expected) != 410:
        raise RuntimeError("原SQL+C3参考必须410项")
    expected.update(BASE_OVERLAY)
    if len(expected) != 412 or plugin_map(BASE) != expected:
        raise RuntimeError("完整干净6f 412基点不符")
    return expected


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
    for name in ("torch", "vllm", "vllm-plugin-fl", "flag-gems", "triton", "sqlalchemy", "transformers"):
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
            "env": {k: os.environ.get(k) for k in ("PATH", "PYTHONPATH", "VLLM_PLUGINS", "LD_LIBRARY_PATH", "CUDA_VISIBLE_DEVICES", "PYTHONDONTWRITEBYTECODE", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
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
            or not run.name.endswith("-last-layer-tail-gate") or not run.is_dir() or not control.is_dir()
            or run.is_symlink() or control.is_symlink()):
        raise ValueError("只接受本launcher新建的ROOT/framework直系run/control")
    manifest = {"kind": "actual末层局部eager尾段门，非生产AOT/模型服务性能", "started_utc": utc(),
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
        expected_base = checked_base()
        manifest["base_source"] = str(BASE)
        manifest["base_aliases_dereferenced"] = {
            path.relative_to(BASE).as_posix(): {"target": str(path.readlink()),
                "resolved": str(path.resolve(strict=True)), "sha256": sha(path)}
            for path in BASE.rglob("*") if path.is_symlink()
            and not any(part in (".git", "__pycache__") for part in path.relative_to(BASE).parts)}
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
        for name, (path, expected) in INSTALLED.items():
            shutil.copyfile(path, source / name)
            if sha(source / name) != expected:
                raise RuntimeError("actual源码归档不符：" + name)
        for name in HELPERS:
            shutil.copyfile(ROOT / "scripts" / name, control / name)
        shutil.copyfile(REFERENCE, control / "base-reference-410.json")
        write(control / "base-source-sha256.json", expected_base)
        shutil.copytree(BASE, control / "plugin-source",
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
        if plugin_map(control / "plugin-source") != expected_base or checked_base() != expected_base:
            raise RuntimeError("完整412基点复制或准备后身份变化")
        manifest["environment"] = environment()
        write(control / "environment-before.json", manifest["environment"])
        expected_source = source_map(source)
        write(control / "source-sha256.json", expected_source)
        manifest["db_before"] = snapshot(control, "db-before")
        checked_assets()
        if source_map(source) != expected_source:
            raise RuntimeError("准备期间归档source变化")
        manifest["preflight_before_worker"] = idle(control, "preflight-before-worker")
        worker_argv = [sys.executable, str(source / "gate.py"), "--device-worker", "--output-dir", str(run),
                       "--source-dir", str(source), "--model", str(MODEL)]
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = str(BASE)
        env["VLLM_PLUGINS"] = "fl"
        write(control / "worker-command.json", {"argv": worker_argv, "shell": shlex.join(worker_argv), "env": {key: env[key] for key in ("PYTHONDONTWRITEBYTECODE", "PYTHONPATH", "VLLM_PLUGINS")}})
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
        if status == 0 and read(run / "results.json").get("status") != "local_tolerance_passed_not_model_accuracy_or_production_speed":
            raise RuntimeError("worker结果没有通过局部声明的数值门")
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
                manifest["base_unchanged"] = checked_base() == expected_base
                if not manifest["base_unchanged"]:
                    raise RuntimeError("运行期间完整412基点变化")
                checked_assets()
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
        write(control / "seal.json", {"kind": "本轮局部尾段门完整字节索引，不代表模型正确性通过", "recorded_utc": utc(),
                                     "run": str(run), "control": str(control), "exit_code": status, "files": files,
                                     "collect": [str(run), str(control)], "limits": ["worker结果/失败原件另审；exit0不冒充服务或准确率。", "随机权重actual类eager局部门，不是生产Inductor尾图或模型服务性能。"]})
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
    run = ROOT / "framework" / (stamp + "-last-layer-tail-gate")
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
