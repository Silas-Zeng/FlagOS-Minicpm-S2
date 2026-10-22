#!/usr/bin/env python3
"""仅SAVE的42层真实VERIFY1门；原FULL协议/服务参数，不叠观察器或进展选择。"""
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
    "prepare_kv_pitched_save_source.py": "cd3d5c2874f487f8115329d573cb5202f893ab46c89cf31764e9757decaf0209",
    "biv150_kv_pitched_save_worker.py": "a662e478d20884c5b1d65e0ee3d270a62453d88166b28e092dcaf3b35a3df854",
    "biv150_kv_pitched_copy.py": "818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd",
    "biv150_kv_pitched_bridge.cpp": "0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44",
    "biv150_kv_pitched_bridge.so": "9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0",
    "run_framework_screen.py": "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9",
    "snapshot_tuning_db.py": "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2",
    "prepare_innovation_source.py": "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca",
}
DB = Path("/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db")
MANIFEST = "pitched-save-source.json"


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
    owner = module("pitched_save_source_files", ROOT / "scripts/prepare_innovation_source.py")
    helper = module("pitched_save_db", ROOT / "scripts/snapshot_tuning_db.py")
    builder = ROOT / "scripts/prepare_kv_pitched_save_source.py"
    reference, = [ast.literal_eval(node.value) for node in ast.parse(builder.read_bytes()).body
                  if isinstance(node, ast.Assign) and len(node.targets) == 1
                  and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "REFERENCE"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = ROOT / "framework" / (stamp + "-kv-pitched-save-context16k-long")
    control = run.with_name(run.name + "-control")
    source = ROOT / "code" / ("kv-pitched-save-" + stamp)
    control.mkdir(exist_ok=False)
    shutil.copyfile(__file__, control / "launch_kv_pitched_save_screen.py")
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
            if (prepared["asset_sha256"]["vllm_fl/patches/biv150_kv_worker.py"] != ASSETS["biv150_kv_pitched_save_worker.py"]
                    or prepared["preparer_sha256"] != ASSETS["prepare_kv_pitched_save_source.py"]
                    or len(expected_source) != 420 or owner.source_files(source) != expected_source):
                raise RuntimeError("新420树/准备器/SAVE worker身份不符")
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
                "kind": "仅SAVE的C-batch加2D及原FULL VERIFY1真实机制诊断，非性能或新accuracy",
                "variant": "full-R-pitched-save-on-frozen-full-restore", "wrapper_sha256": sha(Path(__file__)),
                "source": str(source), "base": prepared["base_source"], "source_count": 420,
                "reference": reference, "builder_sha256": ASSETS["prepare_kv_pitched_save_source.py"],
                "candidate_worker_sha256": ASSETS["biv150_kv_pitched_save_worker.py"],
                "save_byte_readback_enabled": True,
                "original_innovation_manifest_is_base_only": True, "restore_byte_readback_enabled": True,
                "preflight": {"before_preparation": first_idle, "before_driver": second_idle},
                "db_before": {k: actual[k] for k in db_keys}, "command": command,
                "required_evidence": ["真实SAVE implementation与runtime/bridge/库身份、完整R/42层及动态调用几何",
                                      "SAVE提交非ACK，真实event完成后源free前42层原c95f对照全bytes通过",
                                      "同一事务SAVE→RESTORE_FULL→DROP真ACK、原caps、0ZERO",
                                      "原RESTORE_FULL独立42层整页回读通过，runner六checks/原消费者/host释放",
                                      "32成功0失败/原tokens、DBbeforeafter变化、420源归档-live一致及完整后态"],
                "limits": ["INSTALLED只load前预检，不等于SAVE/FULL/两组回读/消费完成。",
                           "原protocol1aff/txn84be/init791c/e155不变；只替worker SAVE，不叠72942/6a。",
                           "CPP只归档，SO固定已验9e33，不在worker编译；真实服务stream允许0，必须记录实际值。",
                           "旧innovation-source.json仅基点；新420身份以当前manifest及本control映射为准。",
                           "VERIFY1含SAVE源free前原c95f对照及原FULL回读，不计吞吐或accuracy。",
                           "准备锁先释放再由bc51重取；root既有seal收DB-after/source/live/post。",
                           "不自动追加smoke/性能pair/大官方测试；最短必要正确性证据后由root决定。"],
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
