#!/usr/bin/env python3
"""共同6a下原FULL先、进展victim后；首个原参数VERIFY0 A/B，不自动重复。"""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys

ROOT = Path("/workspace/experiments/minicpm-s2")
ASSETS = {
    "prepare_kv_progress_pair_source.py": "6ffb9da39f0901bc83d4c1e3a283df668f73e9c58a90b7fa565020103c36ce4b",
    "biv150_kv_progress_victim_protocol.py": "72942f1f0c284069492b8ee7e1ca1348743e3b9ee49e7da05b8cf9024ac610ef",
    "biv150_kv_memory_observer.py": "6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c",
    "run_framework_screen.py": "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9",
    "snapshot_tuning_db.py": "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2",
    "prepare_innovation_source.py": "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca",
}
DB = Path("/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db")
DB_KEYS = ("snapshot_sha256", "schema_sha256", "logical_content_sha256")
INIT = "39fb96f474c4bacc79ba4cdc1ae27ce877f9dd654825c792dc8446ac620b08e0"


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


def db_fingerprint(directory, helper):
    saved = read(directory / "manifest.json")
    actual = {"snapshot_sha256": sha(directory / "snapshot.sqlite"), **helper.fingerprint(directory / "snapshot.sqlite")}
    if saved.get("status") != "complete" or any(saved[k] != actual[k] for k in (*DB_KEYS, "table_count", "row_count")):
        raise RuntimeError("DB快照身份或实体复算不符")
    return {k: actual[k] for k in (*DB_KEYS, "table_count", "row_count")}


def observer_receipt(run):
    events = [json.loads(line.split("BIV150_KV_MEMORY_OBSERVER ", 1)[1])
              for line in (run / "server.log").read_text(errors="replace").splitlines()
              if "BIV150_KV_MEMORY_OBSERVER " in line]
    if set(e["event"] for e in events) != {"ARMED", "DETERMINE_RETURN", "PARENT_RETURN"}:
        raise RuntimeError("上一FULL启动观察不完整/未激活")
    determines = [e for e in events if e["event"] == "DETERMINE_RETURN"]
    parents = [e for e in events if e["event"] == "PARENT_RETURN"]
    if len(determines) != 1 or len(parents) != 1:
        raise RuntimeError("上一FULL不是单次真实启动观察")
    determine, parent = determines[0], parents[0]
    if (determine["pid"] != parent["pid"] or determine["profile_context_calls"] != 1
            or determine["error_type"] is not None or parent["error_type"] is not None
            or type(determine["returned"]) is not int or determine["returned"] <= 0
            or parent["returned_type"] != "list" or parent["returned"] != [determine["returned"]]
            or set(parent["restored"]) != {"worker_method", "profiling_context", "parent_method"}
            or not all(v is True for v in parent["restored"].values())
            or any(e["new_gpu_samples"] is not False or e["observational_only"] is not True for e in events)):
        raise RuntimeError("上一FULL原返回/profile1/同PID/三hook恢复不符")
    for part in ("worker_fields", "profile", "init_snapshot", "before_create", "before_profile", "after_profile"):
        if not determine[part] or any(type(v) not in (int, float, bool) for v in determine[part].values()):
            raise RuntimeError("上一FULL启动分项存在unobserved")
    return {"pid": determine["pid"], "original_int_return": determine["returned"],
            "profile_context_calls": 1, "restored": parent["restored"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("full", "progress"), required=True)
    parser.add_argument("--match-full-control", type=Path)
    args = parser.parse_args()
    if (args.variant == "progress") != (args.match_full_control is not None):
        parser.error("progress必须匹配本启动器已完成FULL；FULL不接受配对前件")
    for name, expected in ASSETS.items():
        if sha(ROOT / "scripts" / name) != expected:
            raise RuntimeError("辅助素材身份变化：" + name)
    env = os.environ.copy()
    if any(name in env for name in ("MINICPM_NATIVE_PROFILE_EVENTS", "MINICPM_DECODE_GAP_RUN_DIR")):
        raise RuntimeError("禁止继承profiler环境")
    env["BIV150_KV_VERIFY_RESTORE"] = "0"
    # 仅加载已pin的stdlib辅助，候选/torch/vllm一律不import。
    owner = module("observed_pair_source_files", ROOT / "scripts/prepare_innovation_source.py")
    helper = module("observed_pair_db", ROOT / "scripts/snapshot_tuning_db.py")
    builder = ROOT / "scripts/prepare_kv_progress_pair_source.py"
    references, = [ast.literal_eval(n.value) for n in ast.parse(builder.read_bytes()).body
                   if isinstance(n, ast.Assign) and len(n.targets) == 1
                   and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "REFERENCES"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = ROOT / "framework" / (stamp + "-kv-progress-pair-" + args.variant + "-context16k-long")
    control = run.with_name(run.name + "-control")
    source = ROOT / "code" / ("kv-progress-pair-" + args.variant + "-" + stamp)
    control.mkdir(exist_ok=False)
    shutil.copyfile(__file__, control / "launch_kv_progress_pair_screen.py")
    write(control / "wrapper-command.json", [sys.executable, *sys.argv])
    for name in ASSETS:
        shutil.copyfile(ROOT / "scripts" / name, control / name)
    import fcntl
    try:
        # 与原driver同一准备锁；退出with后原bc51自行重新取得，不能嵌套锁启动。
        with (ROOT / "framework-device.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            observed_idle = idle()
            subprocess.run([sys.executable, str(builder), "--variant", args.variant, "--output", str(source)], check=True)
            prepared = read(source / "progress-pair-source.json")
            expected_source = {**prepared["output_sha256_excluding_this_manifest"],
                               "progress-pair-source.json": sha(source / "progress-pair-source.json")}
            if len(expected_source) != 418 or owner.source_files(source) != expected_source:
                raise RuntimeError("新418树完整身份不符")
            shutil.copytree(source, control / "plugin-source", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
            if owner.source_files(control / "plugin-source") != expected_source:
                raise RuntimeError("control源码复制不一致")
            write(control / "source-sha256.json", expected_source)
            with (control / "db-before.log").open("w") as output:
                subprocess.run([sys.executable, str(control / "snapshot_tuning_db.py"), "--database", str(DB), "--output", str(control / "db-before")], check=True, stdout=output)
            before, matched = db_fingerprint(control / "db-before", helper), None
            if args.variant == "progress":
                previous = args.match_full_control.resolve(strict=True)
                if previous.parent != ROOT / "framework" or not re.fullmatch(r"\d{8}T\d{6}Z-kv-progress-pair-full-context16k-long-control", previous.name):
                    raise RuntimeError("只接受本启动器FULL control")
                prior_run = previous.with_name(previous.name[:-8])
                prior_purpose, prior_source = read(previous / "purpose.json"), read(previous / "source-sha256.json")
                cap = references["full"]
                cap_ref = ROOT / "framework" / cap["control"] / "source-sha256.json"
                if sha(cap_ref) != cap["source_manifest"]:
                    raise RuntimeError("FULL固定完整参考变化")
                prior_inputs = read(cap_ref)
                prior_expected = {**prior_inputs, "vllm_fl/__init__.py": INIT,
                                  "vllm_fl/patches/biv150_kv_memory_observer.py": ASSETS["biv150_kv_memory_observer.py"],
                                  "progress-pair-source.json": sha(previous / "plugin-source/progress-pair-source.json")}
                prior_prepared = read(previous / "plugin-source/progress-pair-source.json")
                if (prior_purpose["variant"] != "full" or prior_purpose["wrapper_sha256"] != sha(Path(__file__))
                        or sha(previous / "launch_kv_progress_pair_screen.py") != sha(Path(__file__))
                        or prior_source != prior_expected or prior_prepared["input_sha256"] != prior_inputs
                        or prior_prepared["preparer_sha256"] != ASSETS["prepare_kv_progress_pair_source.py"]
                        or owner.source_files(previous / "plugin-source") != prior_source
                        or (prior_run / "exit-code").read_text().strip() != "0"):
                    raise RuntimeError("前件不是本包装正常完成的固定FULL")
                post = read(prior_run / "postflight-full.json")
                if (post["source_count"] != 418 or post["source_failures"] or post["query"].strip() != "68, 0"
                        or not all(post["ports_closed"].values()) or "No running processes found" not in post["ixsmi"]
                        or not all(v is None or "\nState:\tZ " in v for v in post["owned_process_status"].values())):
                    raise RuntimeError("前件未完成source/live/空闲封存")
                baseline_before = db_fingerprint(previous / "db-before", helper)
                after = db_fingerprint(previous / "db-after", helper)
                if any(baseline_before[k] != after[k] or before[k] != after[k] for k in DB_KEYS):
                    raise RuntimeError("FULL DB前后变化或progress起点不同，拒绝启动")
                matched = {"control": str(previous), "before": baseline_before, "after": after,
                           "same_three_hashes": True, "startup_observer": observer_receipt(prior_run)}
            command = [sys.executable, str(ROOT / "scripts/run_framework_screen.py"), str(run), "--source-dir", str(source),
                       "--context-long-screen", "--seed", "721201", "--require-log-marker", '"event": "DETERMINE_RETURN"']
            write(control / "purpose.json", {"kind": "共同启动观察器原FULL/进展选择VERIFY0首个A/B，非官方计分",
                "pair_order": "full-before-progress", "automatic_repeat": False,
                "variant": args.variant, "wrapper_sha256": sha(Path(__file__)), "source": str(source),
                "base": prepared["base_source"], "source_count": 418, "reference": references[args.variant],
                "builder_sha256": ASSETS["prepare_kv_progress_pair_source.py"], "observer_sha256": ASSETS["biv150_kv_memory_observer.py"],
                "protocol_sha256": expected_source["vllm_fl/patches/biv150_kv_protocol.py"],
                "preflight": observed_idle, "db_before": before, "matching_full_after": matched,
                "restore_byte_readback_enabled": False, "command": command,
                "required_evidence": ["同PID实际profile1/原int与父list/三hook恢复及完整内存标量", "双方实际KV/CPU/物理显存/DB/host工作后验",
                                      "双方实际SAVE-FULL-DROP且0ZERO；progress须真实不同tail且一次主动选择", "动态R/页与run/copy几何/fast/host释放/runner/原consumer"],
                "limits": ["VERIFY0无回读，不继承旧VERIFY1标记。", "同observer仍有共同stdout/CPU扰动，不能称完全无扰动。",
                           "R/消费者/几何是策略行为可不同；DB/KV/启动分项失配不归因。", "准备锁释放后原bc51重取；root串行且既有seal收after/live/post，不自动启动第二job。"]})
            write(control / "command.json", {"env": {"BIV150_KV_VERIFY_RESTORE": "0"}, "argv": command})
            if owner.source_files(source) != expected_source:
                raise RuntimeError("准备期间source变化")
            idle()
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
