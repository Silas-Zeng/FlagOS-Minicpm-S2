#!/usr/bin/env python3
"""原参数KV页序成对短测启动器；只复用冻结源，VERIFY=0，非官方成绩。"""
import argparse
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

ROOT = Path("/workspace/experiments/minicpm-s2")
REFERENCE = "20261021T204159Z-kv-page-order-context16k-long"
BASE_NAME = "sql-mixed-20261021T080656Z"
CANDIDATE_NAME = "kv-page-order-20261021T204159Z"
# 204159完整原件封存后的唯一source-sha256.json身份。
EXPECTED_REFERENCE_SOURCE_MANIFEST = "98a72844e77eee9e07d6c70050003bd121bb61404c507189dd663a320651f240"
ASSETS = {
    "run_framework_screen.py": "bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9",
    "snapshot_tuning_db.py": "0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2",
    "prepare_innovation_source.py": "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca",
}
PROTOCOL_SHA = "0e2115d0fbdedea64d1b911c0d6ae3b359f178004d844a8dd8088dfa4388fb86"
DB = Path("/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db")
DB_KEYS = ("snapshot_sha256", "schema_sha256", "logical_content_sha256")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def idle():
    query = subprocess.check_output(["ixsmi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"], text=True)
    table = subprocess.check_output(["ixsmi"], text=True)
    if query.strip() != "68, 0" or "No running processes found" not in table or "32768MiB" not in table:
        raise RuntimeError("设备忙或非已审32GiB设备")
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
        raise RuntimeError("DB快照身份或重算不符")
    return {k: actual[k] for k in (*DB_KEYS, "table_count", "row_count")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("stable", "page-order"), required=True)
    parser.add_argument("--match-baseline-control", type=Path, help="可选：先前本启动器stable control；新DBbefore必须同其after三hash")
    args = parser.parse_args()
    if len(EXPECTED_REFERENCE_SOURCE_MANIFEST) != 64:
        raise RuntimeError("204159完整源码清单尚未固定，禁止启动")
    for name, expected in ASSETS.items():
        if sha(ROOT / "scripts" / name) != expected:
            raise RuntimeError("辅助素材身份变化：" + name)
    # 只导入已pin纯stdlib的文件/SQLite辅助；不import候选、torch或vllm。
    owner = module("kv_pair_source_files", ROOT / "scripts/prepare_innovation_source.py")
    helper = module("kv_pair_db", ROOT / "scripts/snapshot_tuning_db.py")
    ref = ROOT / "framework" / (REFERENCE + "-control")
    if sha(ref / "source-sha256.json") != EXPECTED_REFERENCE_SOURCE_MANIFEST:
        raise RuntimeError("204159固定源码清单不符")
    candidate_manifest = read(ref / "source-sha256.json")
    package_file = ref / "plugin-source/innovation-source.json"
    if sha(package_file) != candidate_manifest["innovation-source.json"]:
        raise RuntimeError("204159包装清单身份不符")
    package = read(package_file)
    stable_manifest = package["input_sha256"]
    if (len(stable_manifest) != 410 or len(candidate_manifest) != 416
            or package["base_source"] != str(ROOT / "code" / BASE_NAME)
            or package["output"] != str(ROOT / "code" / CANDIDATE_NAME)
            or package["preparer_sha256"] != "4c8ae1d50a113fa35f2642dafa4f60f9a2790187e327a369e063cdb587b3790b"
            or candidate_manifest["vllm_fl/patches/biv150_kv_protocol.py"] != PROTOCOL_SHA
            or {k: v for k, v in candidate_manifest.items() if k != "innovation-source.json"} != package["output_sha256_excluding_this_manifest"]):
        raise RuntimeError("仅接受已审080656/204159两份完整固定source")
    source = ROOT / "code" / (BASE_NAME if args.variant == "stable" else CANDIDATE_NAME)
    if source.is_symlink() or source.resolve() != source:
        raise RuntimeError("source须为固定直接目录")
    expected_source = stable_manifest if args.variant == "stable" else candidate_manifest
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = ROOT / "framework" / (stamp + "-kv-pair-" + args.variant + "-context16k-long")
    control = run.with_name(run.name + "-control")
    control.mkdir(exist_ok=False)
    shutil.copyfile(__file__, control / "launch_kv_pair_screen.py")
    write(control / "wrapper-command.json", [sys.executable, *sys.argv])
    for name in ASSETS:
        shutil.copyfile(ROOT / "scripts" / name, control / name)
    import fcntl
    # 只持准备锁；释放后原bc51自行重新取同锁，不能嵌套持锁启动。
    with (ROOT / "framework-device.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        observed_idle = idle()
        if owner.source_files(source) != expected_source:
            raise RuntimeError("source全文件SHA不符，不能测量")
        shutil.copytree(source, control / "plugin-source", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        if owner.source_files(control / "plugin-source") != expected_source:
            raise RuntimeError("control source复制不一致")
        write(control / "source-sha256.json", expected_source)
        with (control / "db-before.log").open("w") as output:
            subprocess.run([sys.executable, str(control / "snapshot_tuning_db.py"), "--database", str(DB), "--output", str(control / "db-before")], check=True, stdout=output)
        before = db_fingerprint(control / "db-before", helper)
        matched = None
        if args.match_baseline_control is not None:
            previous = args.match_baseline_control.resolve(strict=True)
            if previous.parent != ROOT / "framework" or not previous.name.endswith("-control"):
                raise RuntimeError("仅接受ROOT/framework既有baseline control")
            previous_purpose = read(previous / "purpose.json")
            previous_run = previous.with_name(previous.name[:-8])
            if (previous_purpose.get("variant") != "stable" or previous_purpose.get("wrapper_sha256") != sha(Path(__file__))
                    or (previous_run / "exit-code").read_text().strip() != "0"
                    or read(previous / "source-sha256.json") != stable_manifest):
                raise RuntimeError("对照不是本启动器正常完成的冻结stable")
            post = read(previous_run / "postflight-full.json")
            if (post["source_count"] != len(stable_manifest) or post["source_failures"]
                    or post["query"].strip() != "68, 0" or not all(post["ports_closed"].values())
                    or "No running processes found" not in post["ixsmi"]):
                raise RuntimeError("上一baseline未完成source/live/空闲封存")
            baseline_before = db_fingerprint(previous / "db-before", helper)
            after = db_fingerprint(previous / "db-after", helper)
            if any(baseline_before[k] != after[k] for k in DB_KEYS):
                raise RuntimeError("baseline运行中DB发生变化，拒绝把其after当共同起点")
            if any(before[k] != after[k] for k in DB_KEYS):
                raise RuntimeError("DB起点不同，拒绝启动候选")
            matched = {"control": str(previous), "before": baseline_before, "after": after,
                       "baseline_before_after_three_hashes_equal": True, "three_hashes_equal": True}
        command = [sys.executable, str(ROOT / "scripts/run_framework_screen.py"), str(run), "--source-dir", str(source), "--context-long-screen", "--seed", "721201", "--require-log-marker", "BIV150_SQL_REFLECTION_INSTALLED" if args.variant == "stable" else "BIV150_KV_PROTOCOL_INSTALLED"]
        purpose = {"kind": "成对短测准备；非官方成绩，仅候选源码差异允许，不能据安装marker判真实命中", "variant": args.variant,
                   "wrapper_sha256": sha(Path(__file__)), "source": str(source), "reference_control": str(ref),
                   "reference_source_manifest_sha256": EXPECTED_REFERENCE_SOURCE_MANIFEST, "source_count": len(expected_source),
                   "preflight": observed_idle, "db_before": before, "matching_baseline_after": matched,
                   "restore_byte_readback_enabled": False, "command": command,
                   "limits": ["VERIFY=0；不包含诊断回读，但原protocol稀疏日志保留。", "DB相同不等于所有编译cache全热；KV容量/CPU/参数仍须run后独立核对。", "准备锁释放后原bc51重新取锁；root仍须唯一设备owner，未改原driver。", "运行后DBafter/live/fullpost由root既有封存步骤收取，不在本包装新增流程。"]}
        write(control / "purpose.json", purpose)
        write(control / "command.json", {"env": {"BIV150_KV_VERIFY_RESTORE": "0"}, "argv": command})
        if owner.source_files(source) != expected_source:
            raise RuntimeError("准备期间source变化")
        idle()
    env = os.environ.copy()
    if any(name in env for name in ("MINICPM_NATIVE_PROFILE_EVENTS", "MINICPM_DECODE_GAP_RUN_DIR")):
        raise RuntimeError("禁止继承profiler环境")
    env["BIV150_KV_VERIFY_RESTORE"] = "0"
    with (control / "runner.log").open("wb") as output:
        process = subprocess.Popen(command, env=env, stdout=output, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, start_new_session=True)
    (control / "runner.pid").write_text(str(process.pid) + "\n")
    print(json.dumps({"run": str(run), "control": str(control), "source": str(source), "runner_pid": process.pid}, ensure_ascii=False))


if __name__ == "__main__":
    main()
