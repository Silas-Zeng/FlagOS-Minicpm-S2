#!/usr/bin/env python3
"""仅本地stdlib验收一个已封存的FULL诊断；未齐原件不输出通过文件。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE_REVIEW = ROOT / "analysis/source/mm-cta-service-pair/recompute.py"
BASE_REVIEW_SHA = "81f227fb4c4eca992024fc0d7cebb6416f3ffda054d8e9a536d35040011122bd"
BUILDER_SHA = "b4e04e504e0ffda195913a267ca39b87562c73f30bb71e8dbf304392de0ebbd3"
LAUNCHER_SHA = "63947c7fc1c7bc423ceb41d99fb50bcd5b5560442609d76e597ccd5c5fd52bfe"
ASSETS = {
    "biv150_kv_protocol.py": "1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8",
    "biv150_kv_transaction.py": "84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883",
    "biv150_kv_worker.py": "5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477",
    "biv150_kv_page_copy.py": "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c",
    "biv150_kv_completion_probe.py": "a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6",
}
INPUTS = {name: name.replace("biv150_kv_", "biv150_kv_full_restore_")
          for name in ("biv150_kv_protocol.py", "biv150_kv_transaction.py", "biv150_kv_worker.py")}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, minimum=0):
    require(type(value) is int and value >= minimum, "整数范围/类型不符")
    return value


def inspect_raw(name):
    """复用已审原函数；仅更换长负载路径/输出数，允许真实DB变化并报告。"""
    require(not sys.flags.optimize, "审计不允许python -O跳过原validator断言")
    require(sha(BASE_REVIEW) == BASE_REVIEW_SHA, "原stdlib审计入口SHA变化")
    prefix, separator, _ = BASE_REVIEW.read_text(encoding="utf-8").partition("\ncandidate = inspect_run(")
    require(bool(separator), "原审计函数提取边界变化")
    replacements = [
        ('manifest["context_screen"] and', 'manifest["context_long_screen"] and'),
        ('"context_long_screen", "decode_screen"', '"context_screen", "decode_screen"'),
        ('context-16k', 'context-16k-long'), ('"128", "64"', '"1024", "64"'),
        ('524288, 4096', '524288, 32768'), ('528384 /', '557056 /'),
        ('"output_tokens": 4096', '"output_tokens": 32768'),
        ('    assert databases["before"] == databases["after"]\n', ''),
    ]
    for before, after in replacements:
        require(before in prefix, "原validator更换点缺失：" + before)
        prefix = prefix.replace(before, after)
    namespace = {"__file__": str(BASE_REVIEW), "__name__": "readonly_full_restore_raw"}
    exec(compile(prefix, str(BASE_REVIEW) + ":long_adapter", "exec"), namespace)
    return namespace["inspect_run"](name,
        "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1", 416)


def inspect(name):
    require(re.fullmatch(r"\d{8}T\d{6}Z-kv-full-restore-context16k-long", name) is not None,
            "需要独立FULL UTC run ID，不能把旧ZERO链作为输入")
    evidence, manifest, sources, _ = inspect_raw(name)
    run = ROOT / "experiments/framework" / name
    control = Path(str(run) + "-control")
    require(sha(control / "launch.sh") == LAUNCHER_SHA, "封存launcher不是63947")
    require(sha(control / "prepare_kv_full_restore_source.py") == BUILDER_SHA, "封存builder不是b4e")
    require(sources["vllm_fl/__init__.py"] == "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8", "init不符")
    for name_, value in ASSETS.items():
        require(sources["vllm_fl/patches/" + name_] == value, "canonical素材SHA不符：" + name_)
    prepared = read(control / "plugin-source/innovation-source.json")
    require(prepared["asset_sha256"] == ASSETS, "source manifest资产身份不符")
    require(all(prepared["asset_input_files"][n] == v for n, v in INPUTS.items()), "三input映射不符")
    require(prepared["preparer_sha256"] == BUILDER_SHA and prepared["base_source"].endswith("/code/sql-mixed-20261021T080656Z"), "非原080656包装")
    purpose = read(control / "purpose.json")
    require(purpose["variant"] == "single-victim-kv-full-restore" and purpose["restore_byte_readback_enabled"] is True, "非FULL VERIFY1诊断")
    require("BIV150_KV_VERIFY_RESTORE=1 " in (control / "command.txt").read_text(), "未显式VERIFY1")
    require(manifest["seed"] == 721201, "seed不符")
    driver_ast = ast.parse((run / "screen-driver.py").read_bytes())
    server, = [ast.literal_eval(n.value) for n in driver_ast.body
               if isinstance(n, ast.Assign) and len(n.targets) == 1
               and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "SERVER"]
    require(manifest["server_command"] == server, "实际serve参数偏离已固定bc51原SERVER")
    events = []
    for line in (run / "server.log").read_text(encoding="utf-8", errors="replace").splitlines():
        if "BIV150_KV_PROTOCOL " in line:
            events.append(json.loads(line.split("BIV150_KV_PROTOCOL ", 1)[1]))
    require(bool(events), "无实际协议事件")

    def one(event):
        selected = [e for e in events if e["event"] == event]
        require(len(selected) == 1, "事件须恰一条：" + event)
        return selected[0]

    checked = one("FIRST_CHECKED")
    require(checked["eligible"] is True, "scope未实际命中")
    acks = [e for e in events if e["event"] == "RPC_ACK"]
    require([a["command"]["kind"] for a in acks] == ["SAVE", "RESTORE_FULL", "DROP"],
            "须真实SAVE→FULL→DROP三命令；ZERO/旧RESTORE fallback不算FULL通过")
    require([a["command"]["operation_serial"] for a in acks] == [1, 2, 3], "serial不符")
    save, full, drop = (a["command"] for a in acks)
    saved, restored, dropped = (a["worker_response"] for a in acks)
    key = save["key"]
    require(len(key) == 4 and all(a["command"]["key"] == key for a in acks), "事务key/epoch不同")
    r = integer(save["prefix_tokens"], 16)
    require(r % 16 == 0, "R非整页")
    pages, nbytes = r // 16, r * 43008
    require(nbytes <= 1 << 30, "payload越首版cap")
    for command, reply, event in zip((save, full, drop), (saved, restored, dropped), acks):
        require(command["prefix_tokens"] == r, "跨command的R变化")
        require(all(reply.get(k) == command[k] for k in ("key", "operation_serial", "kind", "pages", "prefix_tokens", "nbytes")), "ACK映射回显不符")
        require(reply["successful"] is True and reply["completed"] is True and reply["error"] is None, "无真实成功settled ACK")
        require(reply["worker_pid"] == event["pid"] == checked["pid"], "非同PID actual worker ACK")
        require(reply["transferred_bytes"] == command["nbytes"], "真实完成字节数不符")
    for command in (save, full):
        ids = command["pages"]
        require(command["nbytes"] == nbytes and len(ids) == pages and len(set(ids)) == pages
                and all(type(x) is int and x > 0 for x in ids), "非完整唯一的实际R页")
    runs = lambda ids: 1 + sum(b != a + 1 for a, b in zip(ids, ids[1:]))
    source_runs, destination_runs = runs(save["pages"]), runs(full["pages"])
    require(saved["full_restore_supported"] is True and saved["saved_layers"] == 42
            and saved["saved_page_bytes"] == 16384 and saved["saved_prefix_pages"] == pages
            and saved["saved_bytes"] == nbytes, "SAVE真ACK缺完整normal42能力")
    require(saved["submitted_bytes"] == nbytes and saved["copy_calls"] == 42 * source_runs, "SAVE实际copy几何不符")
    require(restored["zero_stage_executed"] is False and restored["zero_calls"] == 0
            and restored["full_coverage"] is True and restored["destination_bound"] is True
            and restored["full_coverage_bytes"] == nbytes, "FULL完整覆盖/无ZERO证明缺失")
    require(restored["submitted_bytes"] == nbytes and restored["copy_calls"] == 42 * destination_runs, "FULL实际copy几何不符")
    require(restored["diagnostic_verify_requested"] is True and restored["verification_performed"] is True
            and restored["verification_passed"] is True and restored["verification_readback_bytes"] == nbytes
            and restored["verification_copy_calls"] == 42 * destination_runs, "42层全byte回读未通过")
    require(all(x["host_held"] is True and x["host_payload_bytes"] == nbytes for x in (saved, restored)), "copy期间host引用未持有")
    require(drop["pages"] == [] and drop["nbytes"] == 0 and dropped["dropped"] is True
            and dropped["host_held"] is False and dropped["host_payload_bytes"] == 0, "host未真实释放")
    freed, ordered = one("SAVE_ACK_FREE"), one("PRIVATE_PAGES_ORDERED")
    restore_ack, published = one("RESTORE_ACK"), one("RESUME_PUBLISHED")
    runner, consumer = one("RUNNER_RESUME_STATE_CHECKED"), one("RESUME_OUTPUT_PROCESSED")
    sequence = [acks[0], freed, ordered, acks[1], restore_ack, published, acks[2], runner, consumer]
    require([events.index(e) for e in sequence] == sorted(events.index(e) for e in sequence), "真实save/free/恢复/发布/消费次序不符")
    require(all(e["prefix_tokens"] == r for e in (freed, ordered, restore_ack, published)), "阶段R不符")
    require(ordered["page_count"] == pages and ordered["increasing_runs_after"] == destination_runs
            and full["pages"] == sorted(full["pages"]), "实际私有页排序/几何不符")
    require(all(ordered[k] is True for k in ("same_page_ids", "same_block_objects", "owned_list_identity", "future_free_order_may_change"))
            and ordered["host_logical_order_changed"] is False, "私有页映射proof缺失")
    expected_checks = {"cached_state_same", "computed_prefix", "cpu_computed_prefix", "full_block_replacement", "generator_same", "output_token_ids"}
    require(set(runner["checks"]) == expected_checks and all(v is True for v in runner["checks"].values())
            and runner["key"] == consumer["key"] == key and runner["before_attention"] is True
            and runner["gpu_completion_claimed"] is False and consumer["after_original_update"] is True, "原runner/实际消费未确认")
    consumed = integer(consumer["scheduled_tokens"], 1)
    for count in ("fast_rejects", "restore_skips", "saved", "restored", "published", "rollbacks"):
        values = [integer(e[count]) for e in events]
        require(values == sorted(values), "稀疏累计计数倒退：" + count)
    require(all(consumer[k] == 1 for k in ("saved", "restored", "published")) and consumer["rollbacks"] == 0
            and consumer["fast_rejects"] <= consumer["restore_skips"], "最终计数不符")
    return {"status": "passed_full_restore_verify1_diagnostic", "evidence": evidence,
        "protocol_events": events, "geometry": {"prefix_tokens": r, "pages": pages, "nbytes": nbytes,
            "source_runs": source_runs, "destination_runs": destination_runs,
            "save_copy_calls": saved["copy_calls"], "full_copy_calls": restored["copy_calls"],
            "zero_calls": 0, "verification_copy_calls": restored["verification_copy_calls"],
            "consumed_scheduled_tokens": consumed, "fast_rejects": consumer["fast_rejects"]},
        "database_before_after_equal": evidence["database"]["before"] == evidence["database"]["after"],
        "source_manifest_sha256": sha(control / "source-sha256.json"),
        "validator_sha256": sha(Path(__file__)), "reused_validator_sha256": BASE_REVIEW_SHA,
        "limits": ["VERIFY1诊断，不计算收益/总分；DB变化据实保留。", "42byte回读/runner六项/原消费不等于完整accuracy或取消/多victim证明。",
                   "copy调用几何和稀疏fast累计来自该run；不推算DMA带宽/CPU耗时或完整负载路径覆盖。"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.run_id)
    except FileNotFoundError as error:
        print(json.dumps({"status": "pending_missing_evidence", "missing": str(error), "gain_calculated": False}, ensure_ascii=False))
        return 2
    except (AssertionError, ValueError, KeyError, TypeError, RuntimeError) as error:
        print(json.dumps({"status": "not_passed", "error": repr(error), "gain_calculated": False}, ensure_ascii=False))
        return 1
    if args.output:
        with args.output.open("x", encoding="utf-8", newline="\n") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
            file.write("\n")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
