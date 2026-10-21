#!/usr/bin/env python3
"""独立首次RUNNING失败CPU快照诊断；原参数，不是性能成绩或victim策略。"""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path("/workspace/experiments/minicpm-s2")
ASSETS = {
    "prepare_preemption_snapshot_source.py": "42958bd16759243667340e9575968a1f44e9a8553ce96c500403ad45e1720504",
    "biv150_preemption_snapshot.py": "d38fd18e7a83aa03db43390746731c5caa0defd9b560da65f10e4454016a9124",
    "biv150_kv_completion_probe.py": "a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6",
    "prepare_innovation_source.py": "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca",
    "run_framework_screen.py": "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9",
    "snapshot_tuning_db.py": "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def idle():
    query = subprocess.check_output(["ixsmi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"], text=True)
    table = subprocess.check_output(["ixsmi"], text=True)
    if (query.strip() != "68, 0" or "No running processes found" not in table
            or "32768MiB" not in table or "BI-V150" not in table):
        raise RuntimeError("当前不是已审单BI-V150空闲态")
    for family, host in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            if sock.connect_ex((host, 9031)) == 0:
                raise RuntimeError("9031已占用")
    return {"query": query, "ixsmi": table}


def main():
    if len(sys.argv) != 1:
        raise RuntimeError("仅固定原context-long诊断，不接受额外服务/负载参数")
    for name, expected in ASSETS.items():
        if sha(ROOT / "scripts" / name) != expected:
            raise RuntimeError("素材身份变化：" + name)
    environment = os.environ.copy()
    if any(k in environment for k in ("MINICPM_NATIVE_PROFILE_EVENTS", "MINICPM_DECODE_GAP_RUN_DIR")):
        raise RuntimeError("不能继承profiler环境")
    environment["BIV150_KV_VERIFY_RESTORE"] = "0"
    spec = importlib.util.spec_from_file_location("preemption_source_files", ROOT / "scripts/prepare_innovation_source.py")
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)  # 已pin的stdlib文件helper；不import候选或框架。
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = ROOT / "framework" / (stamp + "-preemption-snapshot-context16k-long")
    control = run.with_name(run.name + "-control")
    source = ROOT / "code" / ("preemption-snapshot-" + stamp)
    control.mkdir(exist_ok=False)
    shutil.copyfile(__file__, control / "launch_preemption_snapshot.py")
    for name in ASSETS:
        shutil.copyfile(ROOT / "scripts" / name, control / name)
    import fcntl
    try:
        with (ROOT / "framework-device.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            before_idle = idle()
            subprocess.run([sys.executable, str(ROOT / "scripts/prepare_preemption_snapshot_source.py"),
                            "--output", str(source)], check=True)
            prepared = json.loads((source / "preemption-snapshot-source.json").read_text())
            expected = {**prepared["output_sha256_excluding_this_manifest"],
                        "preemption-snapshot-source.json": sha(source / "preemption-snapshot-source.json")}
            if len(expected) != 413 or owner.source_files(source) != expected:
                raise RuntimeError("独立413完整树不符")
            shutil.copytree(source, control / "plugin-source", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
            if owner.source_files(control / "plugin-source") != expected:
                raise RuntimeError("control复制字节变化")
            write(control / "source-sha256.json", expected)
            with (control / "db-before.log").open("w") as log:
                subprocess.run([sys.executable, str(control / "snapshot_tuning_db.py"), "--database",
                    "/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db",
                    "--output", str(control / "db-before")], check=True, stdout=log)
            # 原driver在load之前检查安装；真实失败只能在load之后后验，不冒充preload marker。
            command = [sys.executable, str(ROOT / "scripts/run_framework_screen.py"), str(run), "--source-dir", str(source),
                       "--context-long-screen", "--seed", "721201", "--require-log-marker", '"event": "INSTALLED"']
            write(control / "command.json", {"env": {"BIV150_KV_VERIFY_RESTORE": "0"}, "argv": command})
            write(control / "purpose.json", {"kind": "首次RUNNING实际None后CPU快照，只诊断不计性能",
                "wrapper_sha256": sha(Path(__file__)), "builder_sha256": ASSETS["prepare_preemption_snapshot_source.py"],
                "runtime_sha256": ASSETS["biv150_preemption_snapshot.py"], "source_count": 413,
                "base": prepared["base_source"], "source": str(source), "preflight": before_idle,
                "command": command, "requires_post_load_event": "FIRST_RUNNING_FAILURE", "requires_complete": True,
                "required_evidence": ["实际FIRST_CHECKED eligibleTrue/FIRST_RUNNING_FAILURE completeTrue且仅一次",
                    "原tail victim/全running CPU进展/queued spans/1GiB静态资格/真实free及标明derived需求",
                    "原serve/负载/32成功tokens、413source/live、DB前后实体与postidle原件"],
                "limits": ["INSTALLED不是快照完成；scope拒绝/INCOMPLETE/无实际失败均不算诊断通过。",
                    "真实失败在负载中产生，不能把FIRST_RUNNING_FAILURE放进原driver的load前marker。",
                    "不叠6a/两KV协议，不启用旧a4de probe，无future访问/新GPU操作或策略。",
                    "一次页遍历/CPU打印有扰动，不报告吞吐收益或继承accuracy；原seal收DBafter/live/fullpost。"]})
            if owner.source_files(source) != expected:
                raise RuntimeError("启动前source变化")
            idle()
    except BaseException as error:
        write(control / "preparation-failed.json", {"error": repr(error), "device_driver_started": False})
        raise
    # 准备锁释放后原bc51自行重取；只启动这个子任务，root串行持有设备归属。
    with (control / "runner.log").open("wb") as log:
        process = subprocess.Popen(command, env=environment, stdout=log, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, start_new_session=True)
    (control / "runner.pid").write_text(str(process.pid) + "\n")
    print(json.dumps({"run": str(run), "control": str(control), "source": str(source), "runner_pid": process.pid}))


if __name__ == "__main__":
    main()
