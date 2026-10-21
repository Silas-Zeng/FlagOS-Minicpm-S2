#!/usr/bin/env python3
"""本地stdlib验收共同6a、VERIFY0的capacity/FULL原件；不执行框架或设备。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
RAW_REVIEW = ROOT / "scripts/review_kv_full_restore_run.py"
RAW_SHA = "2071bff34cdcd469294b406966ad86a0941d556b1d1e9ddd62dc87f927caf55b"
BUILDER_SHA = "fc937baf735e5694ce9d75c99c200e43b26524b9c24db09ed6939fc408ca2467"
LAUNCHER_SHA = "d768860b8f9d9491b6ea473ab1e0219cfb9a04351806e0cd67685b95fcdf981e"
OBSERVER_SHA = "6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c"
INIT_SHA = "39fb96f474c4bacc79ba4cdc1ae27ce877f9dd654825c792dc8446ac620b08e0"
DB_KEYS = ("snapshot_sha256", "schema_sha256", "logical_content_sha256")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def literal(source, name):
    values = [ast.literal_eval(n.value) for n in ast.parse(source).body
              if isinstance(n, ast.Assign) and len(n.targets) == 1
              and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
    require(len(values) == 1, "顶层常量必须唯一：" + name)
    return values[0]


def raw_inspect(name):
    """只将已审2071通用long原件函数的完整源数量416改418；不调用其VERIFY1门。"""
    require(not sys.flags.optimize and sha(RAW_REVIEW) == RAW_SHA, "必须使用原2071且不可-O")
    raw = RAW_REVIEW.read_text(encoding="utf-8")
    namespace = {"__file__": str(RAW_REVIEW), "__name__": "readonly_observed_pair_raw"}
    exec(compile(raw, str(RAW_REVIEW), "exec"), namespace)
    node, = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == "inspect_raw"]
    function = ast.get_source_segment(raw, node)
    require(function.count(', 416)') == 1, "原通用完整source计数挂点变化")
    exec(compile(function.replace(', 416)', ', 418)'), str(RAW_REVIEW) + ":418", "exec"), namespace)
    return namespace["inspect_raw"](name)


def inspect_observer(log):
    events = [json.loads(x.split("BIV150_KV_MEMORY_OBSERVER ", 1)[1]) for x in log.splitlines()
              if "BIV150_KV_MEMORY_OBSERVER " in x]
    require(set(e["event"] for e in events) == {"ARMED", "DETERMINE_RETURN", "PARENT_RETURN"},
            "observer拒绝/不完整/异常或无实际观察")
    determine, = [e for e in events if e["event"] == "DETERMINE_RETURN"]
    parent, = [e for e in events if e["event"] == "PARENT_RETURN"]
    require(determine["pid"] == parent["pid"] and determine["profile_context_calls"] == 1,
            "实际同PID profile1未证")
    require(determine["error_type"] is parent["error_type"] is None
            and type(determine["returned"]) is int and determine["returned"] > 0
            and parent["returned_type"] == "list" and parent["returned"] == [determine["returned"]],
            "原worker整数/父list实际值不符")
    require(parent["restored"] == {"worker_method": True, "profiling_context": True, "parent_method": True},
            "三个hook没有恢复")
    require(all(e["observational_only"] is True and e["new_gpu_samples"] is False for e in events)
            and any(e["event"] == "ARMED" and e["pid"] == determine["pid"] for e in events)
            and events.index(determine) < events.index(parent), "观察生命周期不符")
    require(determine["logger_before"] == determine["logger_after"], "观察期logger配置变化")
    require(all(type(v) in (int, float) and v >= 0 for part in ("worker_fields", "profile")
                for v in determine[part].values()), "原CPU scalar缺失")
    comparable = {k: determine[k] for k in ("worker_fields", "derived_only_not_new_samples")}
    comparable["profile"] = {k: v for k, v in determine["profile"].items() if k != "profile_time"}
    for key in ("init_snapshot", "before_create", "before_profile", "after_profile"):
        require(len(determine[key]) == 8 and all(type(v) in (int, float, bool) for v in determine[key].values()),
                "原snapshot scalar缺失")
        comparable[key] = {k: v for k, v in determine[key].items() if k != "timestamp"}
    return {"events": events, "pid": determine["pid"], "capacity_components": comparable}


def inspect_protocol(log, variant, expected_pid):
    events = [json.loads(x.split("BIV150_KV_PROTOCOL ", 1)[1]) for x in log.splitlines()
              if "BIV150_KV_PROTOCOL {" in x]

    def one(event):
        rows = [e for e in events if e["event"] == event]
        require(len(rows) == 1, "真实事件必须恰一条：" + event)
        return rows[0]

    checked = one("FIRST_CHECKED")
    require(checked["eligible"] is True and checked["pid"] == expected_pid, "actual Engine协议scope不符")
    acks = [e for e in events if e["event"] == "RPC_ACK"]
    kinds = ["SAVE", "ZERO", "RESTORE", "DROP"] if variant == "capacity" else ["SAVE", "RESTORE_FULL", "DROP"]
    require([e["command"]["kind"] for e in acks] == kinds, "实际协议链未命中预定variant")
    save, restore, drop = acks[0], acks[-2], acks[-1]
    key, r = save["command"]["key"], save["command"]["prefix_tokens"]
    require(type(r) is int and r >= 16 and r % 16 == 0, "动态R须完整页")
    pages, nbytes = r // 16, r * 43008
    require(nbytes <= 1 << 30, "超单slot payload cap")
    for serial, event in enumerate(acks, 1):
        command, reply = event["command"], event["worker_response"]
        require(command["key"] == key and command["operation_serial"] == serial and command["prefix_tokens"] == r,
                "command epoch/serial/R不符")
        require(all(reply.get(k) == command[k] for k in ("key", "operation_serial", "kind", "pages", "prefix_tokens", "nbytes"))
                and reply["worker_pid"] == event["pid"] == expected_pid, "ACK echo/PID不符")
        require(reply["completed"] is True and reply["successful"] is True and reply["error"] is None
                and reply["transferred_bytes"] == command["nbytes"], "无真实成功settled ACK")
        if command["kind"] != "DROP":
            ids = command["pages"]
            require(command["nbytes"] == nbytes and len(ids) == len(set(ids)) == pages
                    and all(type(i) is int and i > 0 for i in ids), "真实整R页映射不符")
            require(reply["host_held"] is True and reply["host_payload_bytes"] == nbytes
                    and reply["submitted_bytes"] == nbytes, "传输期host/实际字节不符")
            require(reply["diagnostic_verify_requested"] is False and reply["diagnostic_extra_pinned_bytes"] == 0
                    and reply.get("verification_performed", False) is False
                    and reply.get("verification_readback_bytes", 0) == 0, "VERIFY0不可执行额外诊断回读")
    runs = lambda ids: 1 + sum(b != a + 1 for a, b in zip(ids, ids[1:]))
    source_runs = runs(save["command"]["pages"])
    destination = restore["command"]["pages"]
    destination_runs = runs(destination)
    require(save["worker_response"]["copy_calls"] == 42 * source_runs
            and restore["worker_response"]["copy_calls"] == 42 * destination_runs, "实际copy几何不符")
    if variant == "capacity":
        zero = acks[1]
        require(zero["command"]["pages"] == destination
                and zero["worker_response"]["zero_calls"] == 42 * destination_runs, "ZERO与RESTORE目的映射不一致")
    else:
        saved, restored = save["worker_response"], restore["worker_response"]
        require(saved["full_restore_supported"] is True
                and [saved[k] for k in ("saved_layers", "saved_page_bytes", "saved_prefix_pages", "saved_bytes")]
                == [42, 16384, pages, nbytes], "SAVE完整normal42能力缺失")
        require(restored["zero_stage_executed"] is False and restored["zero_calls"] == 0
                and restored["destination_bound"] is True and restored["full_coverage"] is True
                and restored["full_coverage_bytes"] == nbytes, "FULL无ZERO完整覆盖proof缺失")
    require(drop["command"]["pages"] == [] and drop["command"]["nbytes"] == 0
            and drop["worker_response"]["dropped"] is True and drop["worker_response"]["host_held"] is False
            and drop["worker_response"]["host_payload_bytes"] == 0, "host未释放")
    freed, ordered = one("SAVE_ACK_FREE"), one("PRIVATE_PAGES_ORDERED")
    restored, published = one("RESTORE_ACK"), one("RESUME_PUBLISHED")
    runner, consumer = one("RUNNER_RESUME_STATE_CHECKED"), one("RESUME_OUTPUT_PROCESSED")
    order = [save, freed, ordered, *acks[1:-1], restored, published, drop, runner, consumer]
    require([events.index(e) for e in order] == sorted(events.index(e) for e in order), "实际生命周期次序不符")
    require(all(e["prefix_tokens"] == r for e in (freed, ordered, restored, published))
            and ordered["page_count"] == pages and ordered["increasing_runs_after"] == destination_runs
            and destination == sorted(destination), "实际private页序/R不符")
    require(all(ordered[k] is True for k in ("same_page_ids", "same_block_objects", "owned_list_identity", "future_free_order_may_change"))
            and ordered["host_logical_order_changed"] is False, "私有页逻辑映射proof缺失")
    expected_checks = {"cached_state_same", "computed_prefix", "cpu_computed_prefix", "full_block_replacement", "generator_same", "output_token_ids"}
    require(set(runner["checks"]) == expected_checks and all(v is True for v in runner["checks"].values())
            and runner["key"] == consumer["key"] == key and runner["before_attention"] is True
            and runner["gpu_completion_claimed"] is False and consumer["after_original_update"] is True
            and type(consumer["scheduled_tokens"]) is int and consumer["scheduled_tokens"] > 0, "原runner/原consumer未证")
    for count in ("fast_rejects", "restore_skips", "saved", "restored", "published", "rollbacks"):
        values = [e[count] for e in events]
        require(all(type(v) is int and v >= 0 for v in values) and values == sorted(values), "累计计数不符：" + count)
    require(all(consumer[k] == 1 for k in ("saved", "restored", "published")) and consumer["rollbacks"] == 0
            and consumer["fast_rejects"] <= consumer["restore_skips"], "最终事务计数不符")
    deferred = [e for e in events if e["event"] == "RESTORE_DEFERRED"]
    require(len(deferred) <= 1, "首defer日志重复")
    if deferred and deferred[0]["reason"] == "capacity_lower_bound":
        require(deferred[0]["free_blocks"] < deferred[0]["saved_prefix_pages"], "容量下界快拒证据不符")
    return {"key": key, "command_kinds": kinds, "prefix_tokens": r, "pages": pages, "nbytes": nbytes,
            "source_runs": source_runs, "destination_runs": destination_runs,
            "save_copy_calls": save["worker_response"]["copy_calls"], "restore_copy_calls": restore["worker_response"]["copy_calls"],
            "zero_calls": acks[1]["worker_response"]["zero_calls"] if variant == "capacity" else 0,
            "fast_rejects": consumer["fast_rejects"], "restore_skips": consumer["restore_skips"],
            "first_deferred": deferred[0] if deferred else None, "runner_checks": runner["checks"],
            "consumer_scheduled_tokens": consumer["scheduled_tokens"], "verification_performed": False,
            "host_released": True, "ordered": ordered}


def inspect(name, variant):
    require(re.fullmatch(r"\d{8}T\d{6}Z-kv-observed-pair-" + variant + r"-context16k-long", name), "run ID或variant不符")
    require(re.fullmatch(r"[0-9a-f]{64}", BUILDER_SHA) and re.fullmatch(r"[0-9a-f]{64}", LAUNCHER_SHA), "等待最终包装pins，不能运行")
    evidence, manifest, sources, installed = raw_inspect(name)
    run = ROOT / "experiments/framework" / name
    control = Path(str(run) + "-control")
    builder = control / "prepare_kv_observed_pair_source.py"
    require(sha(builder) == BUILDER_SHA and sha(control / "launch_kv_observed_pair_screen.py") == LAUNCHER_SHA, "封存包装身份不符")
    spec = literal(builder.read_bytes(), "REFERENCES")[variant]
    reference = ROOT / "experiments/framework" / spec["control"]
    require(sha(reference / "source-sha256.json") == spec["source_manifest"]
            and sha(reference / "plugin-source/innovation-source.json") == spec["innovation_manifest"], "原完整416reference不符")
    original = read(reference / "source-sha256.json")
    package_path = control / "plugin-source/memory-observer-source.json"
    package = read(package_path)
    require(package["variant"] == variant and package["input_sha256"] == original
            and package["preparer_sha256"] == BUILDER_SHA and package["observer_sha256"] == OBSERVER_SHA
            and package["reference_source_manifest_sha256"] == spec["source_manifest"]
            and package["reference_innovation_manifest_sha256"] == spec["innovation_manifest"], "新source包装链不符")
    expected = {**original, "vllm_fl/__init__.py": INIT_SHA, "vllm_fl/patches/biv150_kv_memory_observer.py": OBSERVER_SHA}
    require(len(original) == 416 and package["output_sha256_excluding_this_manifest"] == expected
            and sources == {**expected, "memory-observer-source.json": sha(package_path)}, "除共同observer/init末尾外有变化")
    actual_files = {p.relative_to(control / "plugin-source").as_posix() for p in (control / "plugin-source").rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")}
    require(actual_files == sources.keys(), "完整418树有未登记文件")
    footer = literal((control / "plugin-source/vllm_fl/patches/biv150_kv_memory_observer.py").read_bytes(), "INIT_FOOTER")
    init = (control / "plugin-source/vllm_fl/__init__.py").read_bytes()
    require(init.endswith(footer) and hashlib.sha256(init[:-len(footer)]).hexdigest() == original["vllm_fl/__init__.py"], "原footer被改或observer不在最后")
    purpose, command = read(control / "purpose.json"), read(control / "command.json")
    require(purpose["variant"] == variant and purpose["restore_byte_readback_enabled"] is False
            and purpose["wrapper_sha256"] == LAUNCHER_SHA and purpose["source_count"] == 418
            and purpose["builder_sha256"] == BUILDER_SHA and purpose["observer_sha256"] == OBSERVER_SHA
            and purpose["source"] == manifest["source_dir"]
            and purpose["db_before"] == evidence["database"]["before"]
            and command["env"] == {"BIV150_KV_VERIFY_RESTORE": "0"}
            and command["argv"] == purpose["command"], "本轮VERIFY0/包装purpose/DB不符")
    require(command["argv"][1] == "/workspace/experiments/minicpm-s2/scripts/run_framework_screen.py", "不是原driver入口")
    require(command["argv"][2:] == ["/workspace/experiments/minicpm-s2/framework/" + name,
            "--source-dir", manifest["source_dir"], "--context-long-screen", "--seed", "721201",
            "--require-log-marker", '"event": "DETERMINE_RETURN"'], "原driver参数变化")
    require(manifest["seed"] == 721201 and manifest["require_log_marker"] == '"event": "DETERMINE_RETURN"'
            and manifest["server_command"] == literal((run / "screen-driver.py").read_bytes(), "SERVER"), "原SERVER/seed/marker不符")
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    observer = inspect_observer(log)
    determine, = [e for e in observer["events"] if e["event"] == "DETERMINE_RETURN"]
    expected_loaded = literal((control / "plugin-source/vllm_fl/patches/biv150_kv_memory_observer.py").read_bytes(), "EXPECTED_LOADED")
    require(determine["original_identity"]["loaded_source_sha256"] == expected_loaded
            and determine["original_identity"]["executor_class"] == "vllm.v1.executor.uniproc_executor.UniProcExecutor",
            "actual自然加载对象/源码身份不符")
    protocol = inspect_protocol(log, variant, observer["pid"])
    return {"status": "verified_observed_verify0_" + variant + "_run", "variant": variant,
            "evidence": evidence, "observer": observer, "protocol": protocol,
            "source_manifest_sha256": sha(control / "source-sha256.json"), "source_map": sources,
            "installed_fingerprint": installed, "packages": manifest["packages"],
            "server_command": manifest["server_command"], "purpose": purpose,
            "database_before_after_equal": evidence["database"]["before"] == evidence["database"]["after"],
            "validator_sha256": sha(Path(__file__)), "raw_validator_sha256": RAW_SHA,
            "builder_sha256": BUILDER_SHA, "launcher_sha256": LAUNCHER_SHA,
            "limits": ["VERIFY0本轮无回读，既有各自VERIFY1只作先前正确性证据；不伪造verification_passed。",
                       "共同observer含CPU/日志观察扰动；单轮不证稳定收益/新accuracy/官方成绩。",
                       "不同R/等待/源目的几何/consumer会据实保留，不能把总时间差强归因ZERO。"]}


def compare(report, baseline_path):
    baseline = read(baseline_path)
    require(baseline["status"] == "verified_observed_verify0_capacity_run"
            and baseline["validator_sha256"] == sha(Path(__file__))
            and baseline["builder_sha256"] == BUILDER_SHA and baseline["launcher_sha256"] == LAUNCHER_SHA,
            "需要本入口已完成capacity报告")
    prior = ROOT / "experiments/framework" / (baseline["evidence"]["run_id"] + "-control")
    require(sha(prior / "source-sha256.json") == baseline["source_manifest_sha256"], "先前capacity原件身份不符")
    b, c = baseline["evidence"], report["evidence"]
    match = report["purpose"]["matching_capacity_after"]
    require(match is not None and match["control"] == "/workspace/experiments/minicpm-s2/framework/" + prior.name
            and match["same_three_hashes"] is True
            and match["before"] == b["database"]["before"] and match["after"] == b["database"]["after"],
            "FULL启动前实际匹配的capacity不等于本报告")
    db_chain = all(b["database"]["before"][k] == b["database"]["after"][k]
                   == c["database"]["before"][k] == c["database"]["after"][k] for k in DB_KEYS)
    conditions = {
        "database_before_after_all_three_hashes_equal": db_chain,
        "actual_kv_capacity_equal": b["kv_tokens"] == c["kv_tokens"],
        "observed_startup_capacity_components_equal": baseline["observer"]["capacity_components"] == report["observer"]["capacity_components"],
        "server_command_equal": baseline["server_command"] == report["server_command"],
        "packages_and_installed_sources_equal": baseline["packages"] == report["packages"]
            and baseline["installed_fingerprint"] == report["installed_fingerprint"],
        "cpu_quota_physical_memory_equal": b["cpu_quota_cores"] == c["cpu_quota_cores"]
            and b["physical_memory_mib"] == c["physical_memory_mib"],
    }
    geometry_keys = ("prefix_tokens", "pages", "nbytes", "source_runs", "destination_runs",
                     "save_copy_calls", "restore_copy_calls", "fast_rejects", "restore_skips", "consumer_scheduled_tokens")
    geometry_equal = all(baseline["protocol"][k] == report["protocol"][k] for k in geometry_keys)
    matched = all(conditions.values())
    return {"capacity_review_sha256": sha(baseline_path), "capacity_run": b["run_id"],
            "recorded_starting_conditions_match": matched, "conditions": conditions,
            "protocol_geometry_and_observed_wait_counts_equal": geometry_equal,
            "protocol_differences": {k: {"capacity": baseline["protocol"][k], "full": report["protocol"][k]}
                                     for k in geometry_keys if baseline["protocol"][k] != report["protocol"][k]},
            "descriptive_total_tps_change_percent": (c["total_tokens_per_s"] / b["total_tokens_per_s"] - 1) * 100 if matched else None,
            "descriptive_duration_saved_percent": (1 - c["duration_s"] / b["duration_s"]) * 100 if matched else None,
            "descriptive_ttft_change_percent": (c["mean_ttft_ms"] / b["mean_ttft_ms"] - 1) * 100 if matched else None,
            "limits": ["记录条件匹配不证明所有主机干扰/编译cache相同，也不是单次稳定因果证明。",
                       "恢复R/几何/等待不同则更不能将总时间差归为独立ZERO阶段收益；不对独立ZERO计时。",
                       "任一容量/DB/环境项失配保留完成结果与mismatch，不补算收益。"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=("capacity", "full"))
    parser.add_argument("run_id")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--capacity-review", type=Path, help="FULL必须给本入口已完成的capacity报告")
    args = parser.parse_args()
    try:
        require((args.variant == "full") == bool(args.capacity_review), "FULL须给capacity报告，capacity本身不可配对")
        report = inspect(args.run_id, args.variant)
        if args.capacity_review:
            report["paired_conditions"] = compare(report, args.capacity_review)
    except FileNotFoundError as error:
        print(json.dumps({"status": "pending_missing_evidence", "error": str(error)}))
        return 2
    except (ValueError, AssertionError, KeyError, TypeError, RuntimeError) as error:
        print(json.dumps({"status": "not_passed", "error": repr(error)}))
        return 1
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "run_id": args.run_id,
                      "kv_tokens": report["evidence"]["kv_tokens"],
                      "database_before_after_equal": report["database_before_after_equal"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
