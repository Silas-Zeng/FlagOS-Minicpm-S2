#!/usr/bin/env python3
"""只读验收原FULL/进展victim共同6a VERIFY0对照；动态策略行为不要求相同。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
COMMON_REVIEW = ROOT / "scripts/review_kv_observed_pair_run.py"
COMMON_SHA = "c0c80dcf81b2fc0727f06b43d166a61ad042916ee300511243c2aae42cb14c00"
BUILDER_SHA = "6ffb9da39f0901bc83d4c1e3a283df668f73e9c58a90b7fa565020103c36ce4b"
LAUNCHER_SHA = "1aaf35e13d52e97742414bda4c9aaa18452f396555c373fc64b3a4ed2b4c3510"
OBSERVER_SHA = "6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c"
INIT_SHA = "39fb96f474c4bacc79ba4cdc1ae27ce877f9dd654825c792dc8446ac620b08e0"
INPUT_INIT = "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8"
REFERENCE_MAP = "a67c717f5e1f7ab5e2240dc9cd8623c02a91aa2b2958b9ee0bf206c791183829"
REFERENCE_INNOVATION = "93375c426c9fb0b4d5abdb869ba94a8fab0a01ce1863ab0e1bd9785f586827fe"
PROTOCOLS = {
    "full": "1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8",
    "progress": "72942f1f0c284069492b8ee7e1ca1348743e3b9ee49e7da05b8cf9024ac610ef",
}
MANIFEST = "progress-pair-source.json"
TARGET = "vllm_fl/patches/biv150_kv_protocol.py"
DB_KEYS = ("snapshot_sha256", "schema_sha256", "logical_content_sha256")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def common_functions():
    """复用已验c0的raw418、原6a及FULL VERIFY0合同；不调用其旧pair入口。"""
    require(not sys.flags.optimize and sha(COMMON_REVIEW) == COMMON_SHA, "原c0变化或使用-O")
    namespace = {"__file__": str(COMMON_REVIEW), "__name__": "readonly_progress_pair_common"}
    exec(compile(COMMON_REVIEW.read_bytes(), str(COMMON_REVIEW), "exec"), namespace)
    return namespace


def inspect_selection(log, variant, protocol, pid):
    events = [json.loads(line.split("BIV150_KV_PROTOCOL ", 1)[1]) for line in log.splitlines()
              if "BIV150_KV_PROTOCOL {" in line]
    decisions = [e for e in events if e["event"] == "PROGRESS_VICTIM_DECISION"]
    rejected = [e for e in events if e["event"] == "PROGRESS_VICTIM_REJECTED"]
    if variant == "full":
        require(not decisions and not rejected, "原FULL基线不得伪造选择事件")
        return {"active": False, "decision": None, "baseline_uses_original_tail": True}
    require(len(decisions) == 1 and not rejected, "progress须恰一实际选择，不以安装/拒绝代替")
    decision = decisions[0]
    require(decision["pid"] == pid and decision["actual_none_path"] is True
            and decision["selected"] is True and decision["original_tail_fallback"] is False
            and decision["selected_not_current_scheduled"] is True
            and decision["attempt_limit_per_engine"] == 1 and decision["progress_victim_attempts"] == 1
            and decision["reason"] == "maximum_confirmed_tie_later_once"
            and decision["save_success_predicted"] is False and decision["policy_fairness_preserved"] is False,
            "progress真实None/单次/未scheduled/模式证据不符")
    require(decision["selected_request_id"] not in (decision["failed_request_id"], decision["original_tail_request_id"])
            and decision["failed_running_index"] < decision["selected_running_index"] < decision["original_tail_index"]
            and decision["original_tail_confirmed_output"] < decision["selected_confirmed_output"] < decision["maximum_confirmed_output"]
            and decision["selected_remaining_upper_bound"] > decision["minimum_remaining_upper_bound"]
            and decision["candidate_count"] >= 1,
            "不同tail/后方/进展和保护集合不符")
    require(decision["required_new_blocks_derived"] - decision["free_blocks"] == decision["deficit_blocks"]
            and 0 < decision["deficit_blocks"] <= decision["selected_private_pages"], "缺页/可释放页关系不符")
    require(protocol["key"][1] == decision["selected_request_id"]
            and protocol["prefix_tokens"] == decision["selected_prefix_tokens"]
            and protocol["nbytes"] == decision["selected_payload_bytes"], "同一选中对象未完成FULL链")
    first_ack = next(e for e in events if e["event"] == "RPC_ACK")
    consumer, = [e for e in events if e["event"] == "RESUME_OUTPUT_PROCESSED"]
    require(events.index(decision) < events.index(first_ack)
            and consumer["progress_victim_attempts"] == consumer["progress_victim_selected"] == 1,
            "选择/SAVE顺序或单次累计计数不符")
    return {"active": True, "decision": decision, "counter_in_decision_precedes_increment": True}


def inspect(name, variant):
    require(variant in PROTOCOLS and re.fullmatch(r"\d{8}T\d{6}Z-kv-progress-pair-" + variant + r"-context16k-long", name),
            "只接受本次新A/B run ID")
    common = common_functions()
    evidence, manifest, sources, installed = common["raw_inspect"](name)
    run = ROOT / "experiments/framework" / name
    control = Path(str(run) + "-control")
    builder = control / "prepare_kv_progress_pair_source.py"
    require(sha(builder) == BUILDER_SHA and sha(control / "launch_kv_progress_pair_screen.py") == LAUNCHER_SHA,
            "封存包装不是已审版本")
    literal = common["literal"]
    reference = ROOT / "experiments/framework/20261021T214400Z-kv-full-restore-context16k-long-control"
    require(sha(reference / "source-sha256.json") == REFERENCE_MAP
            and sha(reference / "plugin-source/innovation-source.json") == REFERENCE_INNOVATION, "固定FULL416基点不符")
    original = read(reference / "source-sha256.json")
    package_path = control / "plugin-source" / MANIFEST
    package = read(package_path)
    expected = {**original, "vllm_fl/__init__.py": INIT_SHA,
                "vllm_fl/patches/biv150_kv_memory_observer.py": OBSERVER_SHA, TARGET: PROTOCOLS[variant]}
    require(len(original) == 416 and original["vllm_fl/__init__.py"] == INPUT_INIT
            and package["input_sha256"] == original and package["variant"] == variant
            and package["preparer_sha256"] == BUILDER_SHA and package["observer_sha256"] == OBSERVER_SHA
            and package["protocol_sha256"] == PROTOCOLS[variant]
            and package["progress_asset_sha256"] == PROTOCOLS["progress"]
            and package["source_count_including_this_manifest"] == 418
            and package["reference_source_manifest_sha256"] == REFERENCE_MAP
            and package["reference_innovation_manifest_sha256"] == REFERENCE_INNOVATION
            and package["original_innovation_manifest_preserved_sha256"] == REFERENCE_INNOVATION,
            "新418包装身份/当前protocol与基点混淆")
    require(package["output_sha256_excluding_this_manifest"] == expected
            and sources == {**expected, MANIFEST: sha(package_path)}
            and package["changes"] == {n: {"before": original.get(n), "after": h}
                                      for n, h in expected.items() if original.get(n) != h}, "当前完整源出现额外变化")
    actual_files = {p.relative_to(control / "plugin-source").as_posix() for p in (control / "plugin-source").rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")}
    require(actual_files == sources.keys(), "新418树有未登记文件")
    footer = literal((control / "plugin-source/vllm_fl/patches/biv150_kv_memory_observer.py").read_bytes(), "INIT_FOOTER")
    init = (control / "plugin-source/vllm_fl/__init__.py").read_bytes()
    require(init.endswith(footer) and hashlib.sha256(init[:-len(footer)]).hexdigest() == INPUT_INIT, "6a不在完整原init末尾")
    purpose, command = read(control / "purpose.json"), read(control / "command.json")
    require(purpose["variant"] == variant and purpose["pair_order"] == "full-before-progress"
            and purpose["automatic_repeat"] is False and purpose["wrapper_sha256"] == LAUNCHER_SHA
            and purpose["builder_sha256"] == BUILDER_SHA and purpose["observer_sha256"] == OBSERVER_SHA
            and purpose["protocol_sha256"] == PROTOCOLS[variant] and purpose["source_count"] == 418
            and purpose["restore_byte_readback_enabled"] is False and purpose["source"] == manifest["source_dir"]
            and purpose["db_before"] == evidence["database"]["before"], "新pair purpose/实际DB不符")
    require(command["env"] == {"BIV150_KV_VERIFY_RESTORE": "0"} and command["argv"] == purpose["command"]
            and command["argv"][1:] == ["/workspace/experiments/minicpm-s2/scripts/run_framework_screen.py",
                "/workspace/experiments/minicpm-s2/framework/" + name, "--source-dir", manifest["source_dir"],
                "--context-long-screen", "--seed", "721201", "--require-log-marker", '"event": "DETERMINE_RETURN"']
            and manifest["seed"] == 721201 and manifest["require_log_marker"] == '"event": "DETERMINE_RETURN"'
            and manifest["server_command"] == literal((run / "screen-driver.py").read_bytes(), "SERVER"),
            "VERIFY0/原bc51-SERVER-long-seed命令不符")
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    observer = common["inspect_observer"](log)
    determine, = [e for e in observer["events"] if e["event"] == "DETERMINE_RETURN"]
    expected_loaded = common["loaded_sources"]((control / "plugin-source/vllm_fl/patches/biv150_kv_memory_observer.py").read_bytes())
    require(determine["original_identity"]["loaded_source_sha256"] == expected_loaded
            and determine["original_identity"]["executor_class"] == "vllm.v1.executor.uniproc_executor.UniProcExecutor",
            "实际加载对象/源身份不符")
    protocol = common["inspect_protocol"](log, "full", observer["pid"])
    selection = inspect_selection(log, variant, protocol, observer["pid"])
    return {"status": "verified_progress_pair_" + variant + "_VERIFY0_run", "variant": variant,
            "evidence": evidence, "observer": observer, "protocol": protocol, "selection": selection,
            "source_manifest_sha256": sha(control / "source-sha256.json"), "source_map": sources,
            "installed_fingerprint": installed, "packages": manifest["packages"], "server_command": manifest["server_command"],
            "purpose": purpose, "database_before_after_equal": evidence["database"]["before"] == evidence["database"]["after"],
            "validator_sha256": sha(Path(__file__)), "common_validator_sha256": COMMON_SHA,
            "builder_sha256": BUILDER_SHA, "launcher_sha256": LAUNCHER_SHA,
            "limits": ["VERIFY0本轮无回读，不继承旧VERIFY1标记；原6a含CPU/日志共同扰动。",
                       "R/页/段/copy/fast/消费者是策略行为，逐轮记录而非匹配前置条件。",
                       "即使环境匹配，单次顺序对照不证稳定因果/准确率/公平或官方成绩。"]}


def compare(report, baseline_path):
    baseline = read(baseline_path)
    require(baseline["variant"] == "full" and baseline["status"] == "verified_progress_pair_full_VERIFY0_run"
            and baseline["validator_sha256"] == report["validator_sha256"] == sha(Path(__file__))
            and baseline["builder_sha256"] == report["builder_sha256"] == BUILDER_SHA
            and baseline["launcher_sha256"] == report["launcher_sha256"] == LAUNCHER_SHA, "不是本入口已完成原FULL基线")
    b, c = baseline["evidence"], report["evidence"]
    match = report["purpose"]["matching_full_after"]
    require(match["control"] == "/workspace/experiments/minicpm-s2/framework/" + b["run_id"] + "-control"
            and match["same_three_hashes"] is True and match["before"] == b["database"]["before"]
            and match["after"] == b["database"]["after"], "实际启动前件与基线报告不符")
    differences = {n: {"full": baseline["source_map"].get(n), "progress": report["source_map"].get(n)}
                   for n in baseline["source_map"].keys() | report["source_map"].keys()
                   if baseline["source_map"].get(n) != report["source_map"].get(n)}
    conditions = {
        "database_before_after_all_three_hashes_equal": all(b["database"]["before"][k] == b["database"]["after"][k]
            == c["database"]["before"][k] == c["database"]["after"][k] for k in DB_KEYS),
        "actual_KV_capacity_equal": b["kv_tokens"] == c["kv_tokens"],
        "observed_startup_capacity_components_equal": baseline["observer"]["capacity_components"] == report["observer"]["capacity_components"],
        "original_server_command_equal": baseline["server_command"] == report["server_command"],
        "packages_and_installed_sources_equal": baseline["packages"] == report["packages"]
            and baseline["installed_fingerprint"] == report["installed_fingerprint"],
        "CPU_quota_and_physical_memory_equal": b["cpu_quota_cores"] == c["cpu_quota_cores"]
            and b["physical_memory_mib"] == c["physical_memory_mib"],
        "source_only_expected_protocol_and_pair_manifest_differ": set(differences) == {TARGET, MANIFEST},
    }
    matched = all(conditions.values())
    behavior_keys = ("prefix_tokens", "pages", "nbytes", "source_runs", "destination_runs", "save_copy_calls",
                     "restore_copy_calls", "fast_rejects", "restore_skips", "consumer_scheduled_tokens")
    behavior = {label: {**{k: value["protocol"][k] for k in behavior_keys},
                        "native_preemptions": value["evidence"]["preemptions"], "selection": value["selection"]}
                for label, value in (("full", baseline), ("progress", report))}
    return {"full_review_sha256": sha(baseline_path), "full_run": b["run_id"],
            "recorded_environment_match": matched, "environment_conditions": conditions,
            "source_differences": differences, "strategy_behavior": behavior,
            "strategy_R_pages_runs_wait_consumer_equality_required": False,
            "descriptive_total_TPS_change_percent": 100 * (c["total_tokens_per_s"] / b["total_tokens_per_s"] - 1) if matched else None,
            "descriptive_duration_saved_percent": 100 * (1 - c["duration_s"] / b["duration_s"]) if matched else None,
            "descriptive_TTFT_change_percent": 100 * (c["mean_ttft_ms"] / b["mean_ttft_ms"] - 1) if matched else None,
            "limits": ["环境失配只保原值，不补算gain、不调参数或追容量。",
                       "整体差含策略遍历/日志/传输/调度变化，不当纯pop/更少重算的独立收益。",
                       "策略动态行为差异允许且全部列出，不以几何相等作为环境门。",
                       "同DB/KV/分项不证明其它编译cache/主机干扰完全同，单次小差不证稳定。"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=PROTOCOLS)
    parser.add_argument("run_id")
    parser.add_argument("--full-review", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        require((args.variant == "progress") == bool(args.full_review), "progress须给本入口FULL报告，基线不可配对")
        report = inspect(args.run_id, args.variant)
        if args.full_review:
            report["paired_conditions"] = compare(report, args.full_review)
    except FileNotFoundError as error:
        print(json.dumps({"status": "pending_missing_evidence", "error": str(error), "gain_calculated": False}, ensure_ascii=False))
        return 2
    except (ValueError, AssertionError, KeyError, TypeError, RuntimeError) as error:
        print(json.dumps({"status": "not_passed", "error": repr(error), "gain_calculated": False}, ensure_ascii=False))
        return 1
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "run_id": args.run_id, "kv_tokens": report["evidence"]["kv_tokens"],
                      "database_before_after_equal": report["database_before_after_equal"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
