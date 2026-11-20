from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO.parent.parent
ARCHIVE = ROOT / "archive"
EXPECTED_HEAD = "35bfd52ba722bd2c6b2403184d0996f625634b66"
SPECS = [
    ("i32_dep", "batch-003247-component-dependency-failed", "11e24b6d4099fa73fab46653658dd2c2241a43697575218842c3761bd4c14a81", 61,
     "20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component", "prefill_i32_component_gqa_dependency_missing", "failed"),
    ("i32_scope", "batch-004624-scope-failed", "470c7d3fa878a90e96498c4f077cb9e79b5490b6421953c7f2a265764ed9ed01", 66,
     "20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component", "prefill_i32_component_scope_assertion_failed", "failed"),
    ("i32_record", "batch-010243-recording-failed", "58123f6cade37e360045c42c2b1224804ad9f99a2f1c355abfc49c3a51b0cb8d", 80,
     "20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component", "prefill_i32_component_result_recording_failed", "failed"),
    ("i32_negative", "batch-010950-component-negative", "f95bf0f1c62395f99cb66da02e6f07f16a35a1b07b197da24b44ff941b08773f", 84,
     "20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component", "prefill_i32_component_negative", "stopped_negative"),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    actual_head = __import__("subprocess").check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if actual_head != EXPECTED_HEAD:
        raise RuntimeError(f"checkout moved: {actual_head}")
    helper_path = REPO / "scripts/stage_pr105_232613_prefill_i32_20261029.py"
    spec = importlib.util.spec_from_file_location("stage_helpers", helper_path)
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    helper.EXPECTED_HEAD = EXPECTED_HEAD
    helper.SOURCES = {
        key: {"path": f"prefill-i32-offset-20261029/{folder}", "sha256": manifest_sha,
              "run": run_id, "count": count}
        for key, folder, manifest_sha, count, run_id, _, _ in SPECS
    }

    reg = REPO / "experiments/registry.csv"
    before = reg.read_bytes()
    rows = list(csv.DictReader(io.StringIO(before.decode("utf-8-sig"))))
    if len(rows) != 475:
        raise RuntimeError(f"expected 475 existing rows, got {len(rows)}")
    existing = {r["run_id"] for r in rows}
    staged = []
    for key, folder, manifest_sha, count, run_id, status, label in SPECS:
        if run_id in existing:
            raise RuntimeError(f"run already exists: {run_id}")
        packed = helper.pack_run(run_id, key)
        manifest = packed["source_manifest"]
        run_rel = f"framework/{run_id}/"
        archive_dir = ARCHIVE / "prefill-i32-offset-20261029" / folder
        result = json.loads((archive_dir / f"framework/{run_id}/results.json").read_text(encoding="utf-8"))
        run_meta = json.loads((archive_dir / f"framework/{run_id}/manifest.json").read_text(encoding="utf-8"))
        raw_status = result["status"]
        if raw_status != label:
            raise RuntimeError(f"source status mismatch {run_id}: {raw_status}")
        if len(manifest["files"]) != count or manifest["run"] != run_id:
            raise RuntimeError(f"manifest mismatch: {run_id}")
        conclusion = {
            SPECS[0][5]: "i32组件因入口未传固定GQA依赖而在EngineArgs初始化阶段退出；未进入A/B、数值或计时。保留为依赖接线失败，不是候选正确性或性能结果。",
            SPECS[1][5]: "i32组件在实际调用scope断言处停止；当时worker预设BM256/BQ32与selected配置不符，未进入A/B、数值或计时。保留为scope/harness失败，不判候选数值。",
            SPECS[2][5]: "i32组件A/B编译与Q-fragment proof后，在结果记录代码访问缺失属性而退出，未形成数值或计时。保留为记录器失败，不判候选正确性或性能。",
            SPECS[3][5]: "i32相对offset候选在单层M2048/KV16384组件通过既定数值门，但ABBA慢于baseline：Event每调用8.347575→9.235266ms（+10.63%），wall 8.441216→9.303357ms（+10.21%）。负向停止，不接入生产。",
        }[status]
        created = run_meta["started_utc"]
        utc_start = f"{created[:4]}-{created[4:6]}-{created[6:8]}T{created[9:11]}:{created[11:13]}:{created[13:15]}.{created[15:21]}+00:00"
        row = {
            "run_id": run_id, "local_date": "2026-10-29", "utc_start": utc_start,
            "profile_id": "prefill-i32-offset", "phase": "component_abba", "device": "Iluvatar BI-V150",
            "vllm_commit": run_meta.get("base_commit", ""), "flaggems_commit": "",
            "input_len": 16384, "output_len": "", "concurrency": "", "num_prompts": "", "profiler": "",
            "status": status, "conclusion": conclusion,
        }
        summary = {
            "run_id": run_id, "status": status, "device": "Iluvatar BI-V150", "scope": "私有单层attention组件，M=2048/KV=16384，BM128/BQ16/page16；非官方模型测试",
            "source_tree": run_meta.get("source_tree"), "source_count": run_meta.get("source_count"),
            "source_command": run_meta.get("command"), "source_exit_code": int((archive_dir / f"framework/{run_id}/exit-code").read_text().strip()),
            "conclusion": conclusion,
        }
        if key == "i32_negative":
            timings = result["timings"]
            baseline = [x for x in timings if x["arm"] == "baseline"]
            candidate = [x for x in timings if x["arm"] == "i32"]
            mean = lambda xs, field: sum(x[field] for x in xs) / len(xs)
            summary["correctness"] = "GO：原件终态独审确认初始/变化输入逐位、finite、采样FP64、Graph/side/input/KV/RNG/guard通过；仅单shape，FP64为采样。"
            event_a, event_b = mean(baseline, "event_per_call_ms"), mean(candidate, "event_per_call_ms")
            wall_a, wall_b = mean(baseline, "wall_per_call_ms"), mean(candidate, "wall_per_call_ms")
            summary["timing"] = {"event_baseline_ms": event_a, "event_candidate_ms": event_b,
                                 "wall_baseline_ms": wall_a, "wall_candidate_ms": wall_b,
                                 "event_change_percent": (event_b / event_a - 1) * 100,
                                 "wall_change_percent": (wall_b / wall_a - 1) * 100}
            summary["limitation"] = "资源静态差异没有转成性能收益；单shape私有组件，不是完整attention层链、完整模型吞吐、准确率或官方资格。"
        else:
            summary["limitation"] = "没有有效A/B数值或计时；本次harness/依赖问题不得记作候选数值失败或性能负结果。"
        result_doc = {"raw_source_manifest_sha256": manifest_sha, "source": run_meta,
                      "component_result": result, "limitation": summary["limitation"]}
        helper.write_bundle(packed, row, summary, result_doc)
        staged.append((row, summary, result_doc, packed))
        print(json.dumps({"run": run_id, "status": status, "raw_sha256": packed["raw_info"]["raw_tar_sha256"],
                          "raw_bytes": packed["raw_info"]["raw_tar_bytes"], "chunks": len(packed["raw_info"]["chunks"])}, ensure_ascii=False))

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=rows[0].keys(), lineterminator="\n")
    for row, _, _, _ in staged:
        writer.writerow({name: row.get(name, "") for name in writer.fieldnames})
    with reg.open("ab") as f:
        f.write(output.getvalue().encode("utf-8"))
    if not reg.read_bytes().startswith(before):
        raise RuntimeError("preexisting registry bytes changed")
    result = __import__("subprocess").run([sys.executable, "scripts/build_team_view.py"], cwd=REPO,
                                           check=True, capture_output=True, text=True, encoding="utf-8")
    view = json.loads(result.stdout)
    if view.get("registry_records") != 479 or view.get("unique_runs") != 476:
        raise RuntimeError(f"team view count mismatch: {view}")
    note = REPO / "analysis/stage-prefill-i32-component-batch-20261029.md"
    note.write_text("# Prefill i32 组件四次尝试 staging\n\n"
                    "本地登记四条BI-V150记录；原registry 475行字节保持不变，新增4行。前三次分别为GQA依赖漏接、scope断言和结果记录异常，均未形成候选数值/计时结论；第四次单shape组件通过既定正确性门但Event慢10.63%、wall慢10.21%，按负向停止。资源观察不作为吞吐收益；没有生产接入、完整模型或官方资格。\n\n"
                    "四份原始归档清单和成员完整按SHA校验并写入独立raw.tar.gz及1MiB分块。仅生成本地tree-plan/payload，不提交、不推送。\n", encoding="utf-8", newline="\n")
    print(json.dumps({"prior_rows": 475, "appended_rows": 4, "total_rows": 479, "unique_runs": 476,
                      "generated_view": view, "staging_note": str(note)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
