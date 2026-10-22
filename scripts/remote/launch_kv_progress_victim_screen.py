#!/usr/bin/env python3
"""单次进展victim/FULL VERIFY1机制门；原服务参数，不叠观察器或性能配对。"""
from datetime import datetime, timezone
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys

ROOT = Path("/workspace/experiments/minicpm-s2")
ASSETS = {
    "prepare_kv_progress_victim_source.py": "bbb49a069698d45dc0d4cd39c22d1e7254667ab5264da25b6cf98993b961f1e5",
    "biv150_kv_progress_victim_protocol.py": "72942f1f0c284069492b8ee7e1ca1348743e3b9ee49e7da05b8cf9024ac610ef",
    "run_framework_screen.py": "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9",
    "snapshot_tuning_db.py": "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2",
    "prepare_innovation_source.py": "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca",
}
DB = Path("/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db")
MANIFEST = "progress-victim-source.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    with path.open("x", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.write("\n")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def idle():
    query = subprocess.check_output(["ixsmi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"], text=True)
    table = subprocess.check_output(["ixsmi"], text=True)
    if query.strip() != "68, 0" or "No running processes found" not in table or "32768MiB" not in table or "BI-V150" not in table:
        raise RuntimeError("设备忙或非已审单BI-V150/32GiB")
    for family, host in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            if sock.connect_ex((host, 9031)) == 0:
                raise RuntimeError("9031端口被占用")
    return {"query": query, "ixsmi": table}


def main():
    if len(sys.argv) != 1:
        raise ValueError("仅执行冻结单轮，不接受算法/负载参数覆盖")
    for name, expected in ASSETS.items():
        if len(expected) != 64 or sha(ROOT / "scripts" / name) != expected:
            raise RuntimeError("辅助素材未审或变化：" + name)
    env = os.environ.copy()
    if any(name in env for name in ("MINICPM_NATIVE_PROFILE_EVENTS", "MINICPM_DECODE_GAP_RUN_DIR")):
        raise RuntimeError("禁止继承profiler环境")
    env["BIV150_KV_VERIFY_RESTORE"] = "1"
    # 只加载已pin的stdlib辅助；绝不import候选协议/worker/torch/vllm。
    owner = module("progress_victim_source_files", ROOT / "scripts/prepare_innovation_source.py")
    helper = module("progress_victim_db", ROOT / "scripts/snapshot_tuning_db.py")
    builder = ROOT / "scripts/prepare_kv_progress_victim_source.py"
    reference, = [ast.literal_eval(node.value) for node in ast.parse(builder.read_bytes()).body
                  if isinstance(node, ast.Assign) and len(node.targets) == 1
                  and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "REFERENCE"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = ROOT / "framework" / (stamp + "-kv-progress-victim-context16k-long")
    control = run.with_name(run.name + "-control")
    source = ROOT / "code" / ("kv-progress-victim-" + stamp)
    control.mkdir(exist_ok=False)
    shutil.copyfile(__file__, control / "launch_kv_progress_victim_screen.py")
    write(control / "wrapper-command.json", [sys.executable, *sys.argv])
    for name in ASSETS:
        shutil.copyfile(ROOT / "scripts" / name, control / name)
    import fcntl
    try:
        # 同原driver准备锁；先释放后由bc51重取，不能持锁再启动driver。
        with (ROOT / "framework-device.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            first_idle = idle()
            subprocess.run([sys.executable, str(builder), "--output", str(source)], check=True)
            prepared = read(source / MANIFEST)
            expected_source = {**prepared["output_sha256_excluding_this_manifest"], MANIFEST: sha(source / MANIFEST)}
            if (prepared["asset_sha256"] != ASSETS["biv150_kv_progress_victim_protocol.py"]
                    or prepared["preparer_sha256"] != ASSETS["prepare_kv_progress_victim_source.py"]
                    or len(expected_source) != 417 or owner.source_files(source) != expected_source):
                raise RuntimeError("新417树/准备器/唯一协议身份不符")
            shutil.copytree(source, control / "plugin-source", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
            if owner.source_files(control / "plugin-source") != expected_source:
                raise RuntimeError("control源码复制不一致")
            write(control / "source-sha256.json", expected_source)
            with (control / "db-before.log").open("w") as output:
                subprocess.run([sys.executable, str(control / "snapshot_tuning_db.py"), "--database", str(DB), "--output", str(control / "db-before")], check=True, stdout=output)
            saved = read(control / "db-before/manifest.json")
            actual = {"snapshot_sha256": sha(control / "db-before/snapshot.sqlite"), **helper.fingerprint(control / "db-before/snapshot.sqlite")}
            db_keys = ("snapshot_sha256", "schema_sha256", "logical_content_sha256", "table_count", "row_count")
            if saved.get("status") != "complete" or any(saved[k] != actual[k] for k in db_keys):
                raise RuntimeError("DB-before快照实体复算不符")
            command = [sys.executable, str(ROOT / "scripts/run_framework_screen.py"), str(run), "--source-dir", str(source),
                       "--context-long-screen", "--seed", "721201", "--require-log-marker", "BIV150_KV_PROTOCOL_INSTALLED"]
            write(control / "command.json", {"env": {"BIV150_KV_VERIFY_RESTORE": "1"}, "argv": command})
            if owner.source_files(source) != expected_source:
                raise RuntimeError("准备期间source变化")
            second_idle = idle()
            write(control / "purpose.json", {
                "kind": "单次进展victim选择与FULL VERIFY1真实机制诊断，非性能或新accuracy",
                "variant": "single-progress-victim-on-full-restore", "wrapper_sha256": sha(Path(__file__)),
                "source": str(source), "base": prepared["base_source"], "source_count": 417,
                "reference": reference, "builder_sha256": ASSETS["prepare_kv_progress_victim_source.py"],
                "candidate_protocol_sha256": ASSETS["biv150_kv_progress_victim_protocol.py"],
                "original_innovation_manifest_is_base_only": True, "restore_byte_readback_enabled": True,
                "preflight": {"before_preparation": first_idle, "before_driver": second_idle},
                "db_before": {k: actual[k] for k in db_keys}, "command": command,
                "required_evidence": ["真实选择非原tail的对象及动态进展/原索引/未scheduled/保护集合证明",
                                      "每Engine最多一次主动替换尝试，原后续preempt计数据实保留",
                                      "同一事务真实SAVE→RESTORE_FULL→DROP，0ZERO，dynamic R/pages/runs/bytes",
                                      "全部42层整页字节回读通过，runner六checks/原消费者/host释放",
                                      "32成功0失败/原tokens、DBbeforeafter变化、417源归档-live一致及完整后态"],
                "limits": ["INSTALLED仅load前预检，不等于选择/SAVE/FULL/回读/消费已执行。",
                           "不叠c6快照/6a观察器，不运行smoke或第二pair，不改原bc51/SERVER/seed。",
                           "旧innovation-source.json仅基点；新417身份以本control映射为准。",
                           "VERIFY1包含回读与选择日志开销，不能作为吞吐收益或准确率。",
                           "准备锁已释放再由原bc51重取；root既有seal收DB-after/source/live/post。"],
            })
    except BaseException as error:
        write(control / "preparation-failed.json", {"error": repr(error), "device_driver_started": False})
        raise
    with (control / "runner.log").open("wb") as output:
        process = subprocess.Popen(command, env=env, stdout=output, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, start_new_session=True)
    (control / "runner.pid").write_text(str(process.pid) + "\n")
    print(json.dumps({"run": str(run), "control": str(control), "source": str(source), "runner_pid": process.pid}, ensure_ascii=False))


if __name__ == "__main__":
    main()
