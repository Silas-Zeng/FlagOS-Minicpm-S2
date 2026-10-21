#!/usr/bin/env python3
"""只读本地已封存的独立413快照诊断；缺真实完整事件不写通过结果。"""
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
RUNTIME = "c6b3baa96db494e7c22d8c7a3f02980d06d3469c491bf850e9ebac77675204f6"
BUILDER = "ce4e9773900316c1c19c70acc2dfba5822da08bbdc9e32fa5945b76ab3a666ac"
LAUNCHER = "6ec5d60bf606b8f6c9cee19a1dbce52517b086c65a4d89ad58bf55b37da10812"
SCOPE = "a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6"
INIT = "01c42c6938efb61476669b9bdb76207e79d20d7e19ac4d0165e617649d2a85dd"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def literal(source, name):
    node, = [n.value for n in ast.parse(source).body if isinstance(n, ast.Assign)
             and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
    return ast.literal_eval(node)


def raw_inspect(name):
    require(not sys.flags.optimize and sha(RAW_REVIEW) == RAW_SHA, "原2071身份变化/禁止-O")
    raw = RAW_REVIEW.read_text(encoding="utf-8")
    namespace = {"__file__": str(RAW_REVIEW), "__name__": "readonly_preemption_raw"}
    exec(compile(raw, str(RAW_REVIEW), "exec"), namespace)
    node, = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == "inspect_raw"]
    function = ast.get_source_segment(raw, node)
    require(function.count(', 416)') == 1, "原通用source数量挂点不符")
    exec(compile(function.replace(', 416)', ', 413)'), "<raw413-only>", "exec"), namespace)
    # 不调用2071的KV/VERIFY1门，仅原通用长负载/DB实体/源/live/后态验证。
    return namespace["inspect_raw"](name)


def analyze_snapshot(snapshot):
    rows, queued, current = snapshot["running"], snapshot["queued_frames"], snapshot["current_scheduled_tokens"]
    require(rows and len(rows) == snapshot["running_count"], "缺全running行")
    ids = [r["request_id"] for r in rows]
    require(len(set(ids)) == len(rows) and [r["running_index"] for r in rows] == list(range(len(rows)))
            and all(type(rid) is str for rid in ids), "running顺序/身份不符")
    require(len({r["request_object_id"] for r in rows}) == len(rows)
            and all(type(r["request_object_id"]) is int and r["request_object_id"] > 0 for r in rows), "对象身份缺失")
    require(type(current) is dict and current.keys() <= set(ids)
            and all(type(v) is int and v >= 0 for v in current.values()), "当前未issued映射不符")
    spans = {}
    require([q["deque_index"] for q in queued] == list(range(len(queued)))
            and len({q["output_object_id"] for q in queued}) == len(queued), "旧frame描述不符")
    for entry in queued:
        counts = entry["scheduled_tokens"]
        require(type(counts) is dict and all(type(k) is str and type(v) is int and v >= 0 for k, v in counts.items()), "旧frame token映射不符")
        for rid, count in counts.items():
            spans[rid] = spans.get(rid, 0) + count
    integers = ("prompt_tokens", "legal_max_output_tokens", "confirmed_output_tokens", "remaining_output_upper_bound",
                "known_tokens", "issued_computed_tokens", "output_placeholders", "queued_scheduled_span",
                "stable_prefix_floor_tokens", "current_schedule_tokens_not_yet_issued", "num_preemptions", "next_decode_eligible_step",
                "owned_logical_pages", "owned_nonnull_unique_pages", "private_single_ref_unique_pages", "shared_unique_pages",
                "hashed_unique_pages", "null_page_references", "snapshot_prefix_tokens", "snapshot_payload_bytes")
    for row in rows:
        require(all(type(row[k]) is int and row[k] >= 0 for k in integers), "CPU整数描述符不符")
        require(all(type(row[k]) is bool for k in ("is_prefill_chunk", "nonstreaming", "snapshot_logical_page_coverage", "snapshot_payload_within_1gib")), "CPU布尔描述符不符")
        rid = row["request_id"]
        require(row["queued_scheduled_span"] == spans.get(rid, 0)
                and row["current_schedule_tokens_not_yet_issued"] == current.get(rid, 0), "queued/current span不符")
        stable = max(0, min(row["issued_computed_tokens"] - spans.get(rid, 0), row["known_tokens"] - 1))
        prefix = stable // 16 * 16
        require(row["stable_prefix_floor_tokens"] == stable and row["snapshot_prefix_tokens"] == prefix
                and row["snapshot_payload_bytes"] == prefix * 43008
                and row["snapshot_payload_within_1gib"] == (prefix >= 16 and prefix * 43008 <= 1 << 30), "安全R/cap计算不符")
        require(row["remaining_output_upper_bound"] == max(0, row["legal_max_output_tokens"] - row["confirmed_output_tokens"]), "合法剩余上界不符")
        if row["nonstreaming"]:
            require(row["known_tokens"] == row["prompt_tokens"] + row["confirmed_output_tokens"], "nonstreaming known计数不符")
        require(row["private_single_ref_unique_pages"] + row["shared_unique_pages"] <= row["owned_nonnull_unique_pages"]
                and row["hashed_unique_pages"] <= row["owned_nonnull_unique_pages"]
                and row["owned_nonnull_unique_pages"] + row["null_page_references"] <= row["owned_logical_pages"], "owned/私有/共享计数不符")
        if row["snapshot_logical_page_coverage"]:
            require(prefix >= 16 and prefix // 16 <= row["owned_nonnull_unique_pages"], "逻辑prefix覆盖声明不符")
        else:
            require(prefix >= 0, "负prefix")
    failed_index = snapshot["failed_running_index"]
    require(type(failed_index) is int and 0 <= failed_index < len(rows), "失败index不符")
    failed, tail = rows[failed_index], rows[-1]
    require(snapshot["failed_request_id"] == failed["request_id"]
            and snapshot["original_tail_victim_request_id"] == tail["request_id"], "原FCFS尾对象不符")
    new, free = snapshot["failed_num_new_tokens"], snapshot["free_blocks"]
    require(type(new) is int and new > 0 and type(free) is int and free >= 0, "失败需求/free非整数")
    # 固定原bc51 --max-model-len 131072；此处不查询任何allocator。
    slots = min(min(failed["issued_computed_tokens"], 131072) + new, 131072)
    required = max((slots + 15) // 16 - failed["owned_logical_pages"], 0)
    require(snapshot["required_new_blocks_derived_from_exact_fast_path"] == required
            and snapshot["required_blocks_direct_allocator_sample"] is False
            and snapshot["failure_matches_derived_deficit"] is True and required > free, "derived fast-path失败需求不符")
    require(snapshot["host_headroom_observed"] is False and snapshot["save_success_predicted"] is False, "不能把cap称成功SAVE")
    deficit = required - free
    minimum = min(r["remaining_output_upper_bound"] for r in rows)
    protected = [r["request_id"] for r in rows if r["remaining_output_upper_bound"] == minimum]
    structurally_possible = [r for r in rows if r["nonstreaming"] and not r["is_prefill_chunk"]
        and r["snapshot_logical_page_coverage"] and r["snapshot_payload_within_1gib"]
        and r["private_single_ref_unique_pages"] >= deficit]
    alternatives = [r for r in structurally_possible if r["request_id"] != failed["request_id"]
                    and r["request_id"] not in protected
                    and r["confirmed_output_tokens"] > tail["confirmed_output_tokens"]]
    return {"running_at_failure_count": len(rows), "failed": failed, "original_tail": tail,
        "free_blocks": free, "required_derived_blocks": required, "deficit_blocks": deficit,
        "initial_token_budget_reconstructed": snapshot["token_budget_at_failure"] + sum(current.values()),
        "running_prompt_lengths": sorted({r["prompt_tokens"] for r in rows}),
        "running_legal_max_outputs": sorted({r["legal_max_output_tokens"] for r in rows}),
        "confirmed_output_range": [min(r["confirmed_output_tokens"] for r in rows), max(r["confirmed_output_tokens"] for r in rows)],
        "minimum_remaining_upper_bound_ids_not_actual_finish_prediction": protected,
        "tail_remaining_upper_bound_excess_over_minimum": tail["remaining_output_upper_bound"] - minimum,
        "structurally_possible_payload_rows": [r["running_index"] for r in structurally_possible],
        "more_progressed_nonprotected_rows_to_examine": [r["running_index"] for r in alternatives],
        "policy_selected": None, "policy_implemented": False,
        "conditional_direction": ("存在进展差异和结构候选，后续应权衡最早释放延迟与恢复长尾；本快照不足以选victim或预测收益。"
                                  if alternatives else "这次快照没有给出所需可区分结构候选，不能据此提出更换victim的收益。"),
        "limits": ["分布只覆盖失败瞬间全running，不是全部32请求的到达/长度轨迹。",
                   "合法剩余上界不是实际EOS/完成时刻；不可把protected集合当已确定最早完成者。",
                   "原tail来自已pin FCFS源码和快照，不是额外preempt事件采样；完整后续时序未观测。",
                   "私有页/R/cap只是结构条件，不含pinned余量、传输成本或成功SAVE资格。",
                   "替代行排除失败请求自身；容量条件仅讨论保留失败请求继续的结构可能性，未模拟新victim后的调度。"]}


def inspect(name):
    require(re.fullmatch(r"\d{8}T\d{6}Z-preemption-snapshot-context16k-long", name), "需要独立快照UTC run ID")
    evidence, manifest, sources, installed = raw_inspect(name)
    run = ROOT / "experiments/framework" / name
    control = Path(str(run) + "-control")
    require(sha(control / "launch_preemption_snapshot.py") == LAUNCHER
            and sha(control / "prepare_preemption_snapshot_source.py") == BUILDER, "包装版本不符")
    ref = ROOT / "experiments/framework/20261021T212106Z-kv-capacity-context16k-long-control"
    require(sha(ref / "source-sha256.json") == "73e5d880f5a92f528618ffda71677c2b56c4b49ae582258dc0946ff20809a436"
            and sha(ref / "plugin-source/innovation-source.json") == "5bef5daf33f8d4ed31f4d146106ff2eb23f5a05f317c256f544a07332a6f872d", "410参考链不符")
    base = read(ref / "plugin-source/innovation-source.json")["input_sha256"]
    package_path = control / "plugin-source/preemption-snapshot-source.json"
    package = read(package_path)
    assets = {"biv150_preemption_snapshot.py": RUNTIME, "biv150_kv_completion_probe.py": SCOPE}
    expected = {**base, "vllm_fl/__init__.py": INIT, **{"vllm_fl/patches/" + k: v for k, v in assets.items()}}
    require(len(base) == 410 and package["input_sha256"] == base and package["asset_sha256"] == assets
            and package["preparer_sha256"] == BUILDER and package["output_sha256_excluding_this_manifest"] == expected
            and sources == {**expected, "preemption-snapshot-source.json": sha(package_path)}, "非固定410→413新树")
    actual_files = {p.relative_to(control / "plugin-source").as_posix() for p in (control / "plugin-source").rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")}
    require(actual_files == sources.keys(), "完整413树有未登记文件")
    runtime_path = control / "plugin-source/vllm_fl/patches/biv150_preemption_snapshot.py"
    footer = literal(runtime_path.read_bytes(), "INIT_FOOTER")
    init = (control / "plugin-source/vllm_fl/__init__.py").read_bytes()
    require(init.endswith(footer) and hashlib.sha256(init[:-len(footer)]).hexdigest() == base["vllm_fl/__init__.py"], "完整原init末尾变换不符")
    purpose, command = read(control / "purpose.json"), read(control / "command.json")
    require(manifest["source_dir"] == "/workspace/experiments/minicpm-s2/code/preemption-snapshot-" + name.split("-preemption-snapshot-", 1)[0]
            and purpose["source"] == manifest["source_dir"]
            and package["output"] == manifest["source_dir"], "不是本独立UTC source目录")
    require(purpose["wrapper_sha256"] == LAUNCHER and purpose["builder_sha256"] == BUILDER
            and purpose["runtime_sha256"] == RUNTIME and purpose["source_count"] == 413
            and purpose["requires_post_load_event"] == "FIRST_RUNNING_FAILURE" and purpose["requires_complete"] is True
            and command["env"] == {"BIV150_KV_VERIFY_RESTORE": "0"} and command["argv"] == purpose["command"], "诊断purpose/环境不符")
    require(command["argv"][1:] == ["/workspace/experiments/minicpm-s2/scripts/run_framework_screen.py",
        "/workspace/experiments/minicpm-s2/framework/" + name, "--source-dir", manifest["source_dir"],
        "--context-long-screen", "--seed", "721201", "--require-log-marker", '"event": "CORE_HOOKED"'], "原bc51命令变化")
    require(manifest["seed"] == 721201 and manifest["server_command"] == literal((run / "screen-driver.py").read_bytes(), "SERVER"), "原SERVER/seed变化")
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    require(not any(marker in log for marker in ("BIV150_KV_PROTOCOL ", "BIV150_KV_PROTOCOL_INSTALLED",
        "BIV150_KV_MEMORY_OBSERVER ", "BIV150_KV_COMPLETION_PROBE_INSTALLED")), "不能混其它KV/观察器安装")
    events = [json.loads(line.split("BIV150_PREEMPTION_SNAPSHOT ", 1)[1]) for line in log.splitlines()
              if "BIV150_PREEMPTION_SNAPSHOT " in line]
    snapshot, = [e for e in events if e["event"] == "FIRST_RUNNING_FAILURE"]
    require(snapshot["complete"] is True, "没有实际完整首次失败快照")
    engine_events = [e for e in events if e["pid"] == snapshot["pid"]]
    armed, = [e for e in engine_events if e["event"] == "SCHEDULE_ARMED"]
    checked, = [e for e in engine_events if e["event"] == "FIRST_CHECKED"]
    require(checked["eligible"] is True and armed["source_reverse_exact"] is True
            and armed["schedule_source_sha256"] == "87a6016cdb08ae0d5bdb3fc2c14cb6974467a76b58d0ed41c35aadf1b697a8dd", "实际schedule安装/资格未证")
    require(not any(e["event"] in ("REJECTED", "SCOPE_INCOMPLETE", "SNAPSHOT_INCOMPLETE") for e in engine_events), "Engine观察未完成")
    hooked, = [e for e in engine_events if e["event"] == "CORE_HOOKED"]
    require(events.index(hooked) < events.index(armed) < events.index(checked) < events.index(snapshot), "同Engine原构造后延迟安装/快照次序不符")
    require(all(e["observational_only"] is True and e["gpu_values_read"] is False
                and e["future_readiness_evaluated"] is False and e["victim_policy_changed"] is False for e in events), "不是只观察事件")
    interpretation = analyze_snapshot(snapshot)
    return {"status": "verified_complete_preemption_cpu_snapshot_diagnostic", "evidence": evidence,
        "source_manifest_sha256": sha(control / "source-sha256.json"), "server_log_sha256": sha(run / "server.log"),
        "runtime_sha256": RUNTIME, "builder_sha256": BUILDER, "launcher_sha256": LAUNCHER,
        "validator_sha256": sha(Path(__file__)), "raw_validator_sha256": RAW_SHA,
        "snapshot": snapshot, "events": events, "interpretation": interpretation,
        "database_before_after_equal": evidence["database"]["before"] == evidence["database"]["after"],
        "performance_gain_calculated": False, "limits": ["只一次诊断快照；不执行新policy/accuracy或把页遍历开销计收益。",
            "无实际完整事件/原后续32-0/413源/live/后态就不生成通过报告。",
            "DB变化如实保留；非时间比较，缺少全程状态，不能由单快照重建makespan。"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = inspect(args.run_id)
    except FileNotFoundError as error:
        print(json.dumps({"status": "pending_missing_evidence", "error": str(error)}))
        return 2
    except (ValueError, AssertionError, KeyError, TypeError, RuntimeError) as error:
        print(json.dumps({"status": "not_passed", "error": repr(error)}))
        return 1
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "running_count": report["snapshot"]["running_count"],
                      "complete": True, "performance_gain_calculated": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
