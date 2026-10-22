#!/usr/bin/env python3
"""只读验收已封存的单次进展victim/FULL417诊断；无原件不写通过。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
import textwrap

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
RAW_REVIEW = ROOT / "scripts/review_kv_full_restore_run.py"
RAW_SHA = "2071bff34cdcd469294b406966ad86a0941d556b1d1e9ddd62dc87f927caf55b"
BUILDER_SHA = "bbb49a069698d45dc0d4cd39c22d1e7254667ab5264da25b6cf98993b961f1e5"
LAUNCHER_SHA = "1f8a2f144ec43d21349398a31f268c174ca6de12996024539ec622679fafb996"
PROTOCOL_SHA = "72942f1f0c284069492b8ee7e1ca1348743e3b9ee49e7da05b8cf9024ac610ef"
INIT_SHA = "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8"
REFERENCE_MAP = "a67c717f5e1f7ab5e2240dc9cd8623c02a91aa2b2958b9ee0bf206c791183829"
REFERENCE_INNOVATION = "93375c426c9fb0b4d5abdb869ba94a8fab0a01ce1863ab0e1bd9785f586827fe"
TARGET = "vllm_fl/patches/biv150_kv_protocol.py"
MANIFEST = "progress-victim-source.json"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def original_namespace():
    require(not sys.flags.optimize and sha(RAW_REVIEW) == RAW_SHA, "只接受原2071且不允许-O")
    raw = RAW_REVIEW.read_text(encoding="utf-8")
    namespace = {"__file__": str(RAW_REVIEW), "__name__": "readonly_progress_victim_raw"}
    exec(compile(raw, str(RAW_REVIEW), "exec"), namespace)
    return raw, namespace


def inspect_raw(name, raw, namespace):
    """只更换原2071通用raw函数完整source数416→417，不运行旧FULL入口。"""
    node, = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == "inspect_raw"]
    source = ast.get_source_segment(raw, node)
    require(source.count(', 416)') == 1, "原raw source数挂点变化")
    exec(compile(source.replace(', 416)', ', 417)'), str(RAW_REVIEW) + ":417", "exec"), namespace)
    return namespace["inspect_raw"](name)


def inspect_full_chain(log, raw, namespace):
    """完整复用原2071的ACK/42byte/发布/原消费合同，仅抽离旧包装身份前缀。"""
    node, = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == "inspect"]
    first, = [n for n in node.body if isinstance(n, ast.Assign)
              and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
              and n.targets[0].id == "events"]
    last, = [n for n in node.body if isinstance(n, ast.Return)]
    body = textwrap.dedent("\n".join(raw.splitlines()[first.lineno - 1:last.lineno - 1]))
    before = '(run / "server.log").read_text(encoding="utf-8", errors="replace").splitlines()'
    require(body.count(before) == 1, "原协议log读取挂点变化")
    body = body.replace(before, 'log.splitlines()')
    tail = ('return {"events": events, "pid": checked["pid"], "key": key, '
            '"geometry": {"prefix_tokens": r, "pages": pages, "nbytes": nbytes, '
            '"source_runs": source_runs, "destination_runs": destination_runs, '
            '"save_copy_calls": saved["copy_calls"], "full_copy_calls": restored["copy_calls"], '
            '"zero_calls": 0, "verification_copy_calls": restored["verification_copy_calls"], '
            '"consumed_scheduled_tokens": consumed, "fast_rejects": consumer["fast_rejects"]}}')
    function = "def inspect_full_chain_from_log(log):\n" + textwrap.indent(body + "\n" + tail, "    ")
    exec(compile(function, str(RAW_REVIEW) + ":full_chain_only", "exec"), namespace)
    return namespace["inspect_full_chain_from_log"](log)


def inspect(name):
    require(all(len(p) == 64 for p in (BUILDER_SHA, LAUNCHER_SHA, PROTOCOL_SHA)), "新资产尚未固定，禁止验收")
    require(re.fullmatch(r"\d{8}T\d{6}Z-kv-progress-victim-context16k-long", name) is not None,
            "只接受全新进展victim诊断run ID")
    raw, namespace = original_namespace()
    evidence, manifest, sources, installed = inspect_raw(name, raw, namespace)
    run = ROOT / "experiments/framework" / name
    control = Path(str(run) + "-control")
    require(sha(control / "prepare_kv_progress_victim_source.py") == BUILDER_SHA
            and sha(control / "launch_kv_progress_victim_screen.py") == LAUNCHER_SHA,
            "封存包装不是冻结版本")
    require(sources["vllm_fl/__init__.py"] == INIT_SHA and sources[TARGET] == PROTOCOL_SHA, "新init/协议身份不符")
    expected = {
        "vllm_fl/patches/biv150_kv_worker.py": "5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477",
        "vllm_fl/patches/biv150_kv_transaction.py": "84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883",
        "vllm_fl/patches/biv150_kv_page_copy.py": "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c",
        "vllm_fl/patches/biv150_kv_completion_probe.py": "a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6",
    }
    require(all(sources[k] == v for k, v in expected.items()), "原worker/事务/copy/scope被改")
    ref = ROOT / "experiments/framework/20261021T214400Z-kv-full-restore-context16k-long-control"
    require(sha(ref / "source-sha256.json") == REFERENCE_MAP, "原完整416映射不符")
    inputs = read(ref / "source-sha256.json")
    prepared = read(control / "plugin-source" / MANIFEST)
    current = {**inputs, TARGET: PROTOCOL_SHA, MANIFEST: sources[MANIFEST]}
    require(sources == current and len(inputs) == 416 and len(sources) == 417, "不是唯一协议加manifest变化")
    require(sources["innovation-source.json"] == REFERENCE_INNOVATION
            and prepared["original_innovation_manifest_preserved_sha256"] == REFERENCE_INNOVATION,
            "原innovation仅基点的字节保护不符")
    require(prepared["input_sha256"] == inputs
            and prepared["output_sha256_excluding_this_manifest"] == {n: h for n, h in sources.items() if n != MANIFEST}
            and prepared["changes"] == {TARGET: {"before": inputs[TARGET], "after": PROTOCOL_SHA}}
            and prepared["asset_sha256"] == PROTOCOL_SHA and prepared["canonical_target"] == TARGET
            and prepared["asset_input_file"] == "biv150_kv_progress_victim_protocol.py"
            and prepared["preparer_sha256"] == BUILDER_SHA,
            "新manifest当前完整身份或canonical映射不符")
    purpose, command = read(control / "purpose.json"), read(control / "command.json")
    require(purpose["variant"] == "single-progress-victim-on-full-restore"
            and purpose["source_count"] == 417 and purpose["original_innovation_manifest_is_base_only"] is True
            and purpose["restore_byte_readback_enabled"] is True
            and purpose["candidate_protocol_sha256"] == PROTOCOL_SHA,
            "purpose不是新417机制门")
    require(command["env"] == {"BIV150_KV_VERIFY_RESTORE": "1"}
            and command["argv"] == purpose["command"] and command["argv"][2] == str(Path(manifest["source_dir"]).parents[1] / "framework" / name)
            and command["argv"][3:] == ["--source-dir", manifest["source_dir"], "--context-long-screen", "--seed", "721201", "--require-log-marker", "BIV150_KV_PROTOCOL_INSTALLED"],
            "原bc51/VERIFY1/参数命令不符")
    driver = ast.parse((run / "screen-driver.py").read_bytes())
    server, = [ast.literal_eval(n.value) for n in driver.body if isinstance(n, ast.Assign)
               and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "SERVER"]
    require(manifest["server_command"] == server and manifest["seed"] == 721201, "原SERVER/seed不符")
    log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
    require("BIV150_KV_MEMORY_OBSERVER " not in log and "BIV150_PREEMPTION_SNAPSHOT " not in log,
            "不得叠加6a/c6诊断")
    chain = inspect_full_chain(log, raw, namespace)
    events = chain["events"]
    decisions = [e for e in events if e["event"] == "PROGRESS_VICTIM_DECISION"]
    require(len(decisions) == 1 and not any(e["event"] == "PROGRESS_VICTIM_REJECTED" for e in events), "必须恰一真实选择，不能以拒绝/安装当通过")
    decision = decisions[0]
    require(decision["selected"] is True and decision["actual_none_path"] is True
            and decision["selected_not_current_scheduled"] is True and decision["original_tail_fallback"] is False
            and decision["attempt_limit_per_engine"] == 1 and decision["progress_victim_attempts"] == 1
            and decision["reason"] == "maximum_confirmed_tie_later_once"
            and decision["policy_fairness_preserved"] is False and decision["save_success_predicted"] is False,
            "不是已审单次真实None选择")
    require(decision["pid"] == chain["pid"]
            and decision["selected_request_id"] != decision["original_tail_request_id"]
            and decision["selected_request_id"] != decision["failed_request_id"]
            and decision["failed_running_index"] < decision["selected_running_index"] < decision["original_tail_index"]
            and decision["selected_confirmed_output"] > decision["original_tail_confirmed_output"]
            and decision["selected_confirmed_output"] < decision["maximum_confirmed_output"]
            and decision["selected_remaining_upper_bound"] > decision["minimum_remaining_upper_bound"]
            and decision["candidate_count"] >= 1,
            "不同tail/后方未scheduled/保护集合或进展关系不符")
    require(decision["required_new_blocks_derived"] - decision["free_blocks"] == decision["deficit_blocks"]
            and decision["deficit_blocks"] > 0 and decision["selected_private_pages"] >= decision["deficit_blocks"],
            "原缺页/私有释放必要关系不符")
    require(chain["key"][1] == decision["selected_request_id"]
            and chain["geometry"]["prefix_tokens"] == decision["selected_prefix_tokens"]
            and chain["geometry"]["nbytes"] == decision["selected_payload_bytes"],
            "所选真实对象没有完成原FULL链或R不一致")
    first_ack = next(e for e in events if e["event"] == "RPC_ACK")
    consumer, = [e for e in events if e["event"] == "RESUME_OUTPUT_PROCESSED"]
    require(events.index(decision) < events.index(first_ack)
            and consumer["progress_victim_attempts"] == consumer["progress_victim_selected"] == 1,
            "选择/实际SAVE次序或单次计数不符")
    preemptions = evidence["preemptions"]
    delta = preemptions["after"] - preemptions["before"]
    require(delta >= 1, "原metrics未记录真实preempt")
    return {"status": "verified_progress_victim_full_verify1_diagnostic", "evidence": evidence,
            "selection": decision, "protocol_events": events, "geometry": chain["geometry"],
            "native_preemptions": {**preemptions, "delta": delta, "exactly_one_not_required": True},
            "database_before_after_equal": evidence["database"]["before"] == evidence["database"]["after"],
            "source_manifest_sha256": sha(control / "source-sha256.json"), "installed_fingerprint": installed,
            "validator_sha256": sha(Path(__file__)), "raw_validator_sha256": RAW_SHA,
            "builder_sha256": BUILDER_SHA, "launcher_sha256": LAUNCHER_SHA, "protocol_sha256": PROTOCOL_SHA,
            "performance_gain_calculated": False,
            "limits": ["只有一次主动替换，原路后续抢占可发生；不把原metrics强行固定为1。",
                       "VERIFY1为机制诊断，DB变化据实报告，耗时不计收益/accuracy。",
                       "全42byte及原消费者通过不证明公平、全局随机数逐token等价或更短makespan。"]}


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
