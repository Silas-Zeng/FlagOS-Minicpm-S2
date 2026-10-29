from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO.parent.parent
ARCHIVE = ROOT / "archive"
EXP = REPO / "experiments"
REG = EXP / "registry.csv"
CHUNK = 1024 * 1024
EXPECTED_HEAD = "b3c869cdb4034b03499a8d5d4720a67eec10084a"

SOURCES = {
    "profile": {
        "path": "pr105-hotspot16k-20261029/batch-232613-single-cold-profile",
        "sha256": "9ead287f3abaa87463f0b7dce67b9f14d3f557a4bc628457fc4a1809246d3ffd",
        "run": "20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2",
        "count": 3056,
    },
    "analysis": {
        "path": "pr105-hotspot16k-20261029/batch-235339-readonly-analysis",
        "sha256": "d869df480279e52eb40582960e19c2dcfb2f0c8d28542f4cd3a8a42d2e97f354",
        "run": "pr105-analysis-232613-20261028T235339Z",
        "count": 18,
    },
    "i32_v2": {
        "path": "prefill-i32-offset-20261029/batch-235007-cpu-preparation-failed",
        "sha256": "b561b28b9a6b53adf46c4aa5414c2ff9547bd9dfc8670196c92a3211027750a3",
        "run": "prefill-i32-offset-v2-20261028T235007Z",
        "count": 22,
    },
    "i32_v3": {
        "path": "prefill-i32-offset-20261029/batch-235532-cpu-identity-failed",
        "sha256": "b1608500664fe9592397db6235f2e5dc9df2a3fb3e453dc7241bad5c1406a326",
        "run": "prefill-i32-offset-v3-20261028T235532Z",
        "count": 29,
    },
}


def long_path(path: Path) -> Path:
    value = str(path)
    if value.startswith("\\\\?\\"):
        return Path(value)
    p = Path(path).resolve()
    value = str(p)
    return Path("\\\\?\\" + value) if os.name == "nt" and len(value) >= 240 else p


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with long_path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def load_manifest(key: str):
    spec = SOURCES[key]
    directory = ARCHIVE / spec["path"]
    manifest_path = directory / "manifest.json"
    raw = manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise RuntimeError(f"{key}: archive manifest SHA mismatch")
    manifest = json.loads(raw)
    if manifest.get("run") != spec["run"] or len(manifest.get("files", [])) != spec["count"]:
        raise RuntimeError(f"{key}: archive run/count mismatch")
    return directory, manifest_path, manifest, hashlib.sha256(raw).hexdigest()


def verify_files(key: str, directory: Path, manifest: dict) -> int:
    total = 0
    files = manifest["files"]
    for index, item in enumerate(files, 1):
        rel = Path(item["path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise RuntimeError(f"unsafe archive path: {item['path']}")
        p = long_path(directory / rel)
        if not p.is_file() or p.stat().st_size != item["bytes"] or sha(p) != item["sha256"]:
            raise RuntimeError(f"archive evidence mismatch: {key}:{item['path']}")
        total += item["bytes"]
        if index % 500 == 0 or index == len(files):
            print(f"verified {key}: {index}/{len(files)}", flush=True)
    return total


def add_archive(tf: tarfile.TarFile, archive_key: str, archive_id: str, directory: Path, manifest_path: Path, manifest: dict):
    prefix = "framework" if archive_key == "profile" else "cpu-probes"
    for item in manifest["files"]:
        p = long_path(directory / item["path"])
        tf.add(p, arcname=f"{prefix}/{archive_id}/{item['path']}", recursive=False)
    tf.add(long_path(manifest_path), arcname=f"{prefix}/{archive_id}/archive-manifest.json", recursive=False)


def store_tar(run_id: str, tar_path: Path, primary: dict, supplemental: list[dict] | None = None) -> dict:
    digest = sha(tar_path)
    size = tar_path.stat().st_size
    blob_dir = EXP / "raw-blobs" / digest
    blob_dir.mkdir(parents=True, exist_ok=True)
    chunks = []
    with tar_path.open("rb") as f:
        index = 0
        while True:
            block = f.read(CHUNK)
            if not block:
                break
            chunk_hash = hashlib.sha256(block).hexdigest()
            part = blob_dir / f"{index:04d}.part"
            if part.exists():
                if part.stat().st_size != len(block) or sha(part) != chunk_hash:
                    raise RuntimeError(f"raw chunk collision: {part}")
            else:
                part.write_bytes(block)
            chunks.append({"path": part.relative_to(REPO).as_posix(), "bytes": len(block), "sha256": chunk_hash})
            index += 1
    storage = {"format": "sha256-chunks-v1", "original_path": f"experiments/bundles/{run_id}/raw.tar.gz",
               "original_bytes": size, "original_sha256": digest, "parts": chunks}
    return {"raw_tar_sha256": digest, "raw_tar_bytes": size, "chunks": chunks, "storage": storage}


def pack_run(run_id: str, primary_key: str, supplemental_keys: list[str] | None = None) -> tuple[dict, dict]:
    primary_dir, primary_manifest_path, primary_manifest, primary_manifest_sha = load_manifest(primary_key)
    primary_bytes = verify_files(primary_key, primary_dir, primary_manifest)
    supplemental = []
    for key in supplemental_keys or []:
        directory, manifest_path, manifest, manifest_sha = load_manifest(key)
        size = verify_files(key, directory, manifest)
        supplemental.append({"key": key, "directory": directory, "manifest_path": manifest_path,
                             "manifest": manifest, "manifest_sha256": manifest_sha, "source_bytes": size})

    fd, temp_name = tempfile.mkstemp(prefix=f"stage-{run_id}-", suffix=".tar.gz", dir=REPO)
    os.close(fd)
    temp_tar = Path(temp_name)
    try:
        with tarfile.open(temp_tar, "w:gz", compresslevel=6) as tf:
            add_archive(tf, primary_key, run_id, primary_dir, primary_manifest_path, primary_manifest)
            for extra in supplemental:
                source_id = SOURCES[extra["key"]]["run"]
                for item in extra["manifest"]["files"]:
                    p = long_path(extra["directory"] / item["path"])
                    tf.add(p, arcname=f"supplemental/{source_id}/{item['path']}", recursive=False)
                tf.add(long_path(extra["manifest_path"]), arcname=f"supplemental/{source_id}/archive-manifest.json", recursive=False)
        raw_info = store_tar(run_id, temp_tar, {"source_manifest_sha256": primary_manifest_sha})
        stage_dir = EXP / "bundles" / run_id
        if stage_dir.exists():
            if any(stage_dir.iterdir()):
                raise RuntimeError(f"bundle already exists and is non-empty: {stage_dir}")
            stage_dir.rmdir()
        stage_dir.mkdir(parents=True)
        result = {"primary": {"archive": f"archive/{SOURCES[primary_key]['path']}",
                               "run": primary_manifest["run"], "source_file_count": len(primary_manifest["files"]),
                               "source_bytes": primary_bytes, "source_manifest_sha256": primary_manifest_sha,
                               "files": primary_manifest["files"]},
                  "supplemental": [{"archive": f"archive/{SOURCES[x['key']]['path']}",
                                    "run": x["manifest"]["run"], "source_file_count": len(x["manifest"]["files"]),
                                    "source_bytes": x["source_bytes"], "source_manifest_sha256": x["manifest_sha256"],
                                    "files": x["manifest"]["files"]} for x in supplemental],
                  "raw_tar_sha256": raw_info["raw_tar_sha256"], "raw_tar_bytes": raw_info["raw_tar_bytes"]}
        bundle_manifest = {"run_id": run_id, "status": None, "source_archive": result["primary"]["archive"],
                           "source_file_count": result["primary"]["source_file_count"],
                           "source_manifest_sha256": primary_manifest_sha, "source_files": primary_manifest["files"],
                           "supplemental_archives": result["supplemental"],
                           "raw_tar_sha256": raw_info["raw_tar_sha256"], "raw_tar_bytes": raw_info["raw_tar_bytes"]}
        return {"stage_dir": stage_dir, "raw_info": raw_info, "manifest": bundle_manifest,
                "result": result, "source_manifest": primary_manifest}
    finally:
        try:
            temp_tar.unlink()
        except FileNotFoundError:
            pass


def profile_payload(run_id: str, packed: dict) -> tuple[dict, dict, dict]:
    profile_run = SOURCES["profile"]["run"]
    base = ARCHIVE / SOURCES["profile"]["path"]
    profile_dir = base / "profiles" / profile_run
    profile_manifest = json.loads((profile_dir / "manifest.json").read_text(encoding="utf-8"))
    state = json.loads((profile_dir / "state.json").read_text(encoding="utf-8"))
    launcher_final = json.loads((base / "scripts/pr105-hotspot16k-v2-700dabcb/launcher-final.json").read_text(encoding="utf-8"))
    diagnosis = json.loads((profile_dir / "diagnostic_results.json").read_text(encoding="utf-8"))
    native = json.loads((profile_dir / "native-gqa-prebenchmark.json").read_text(encoding="utf-8"))
    validation = json.loads((profile_dir / "diagnostic-16384-single-cold-window-profile-validation.json").read_text(encoding="utf-8"))
    if not (state.get("complete") and state.get("collector_returncode") == 0 and state.get("cleanup_error") is None):
        raise RuntimeError("profile owner/collector/cleanup gate is not complete")
    if not (launcher_final.get("driver_exit_code") == 0 and launcher_final.get("owner_exit_code") == 0
            and launcher_final.get("posthoc_exit_code") == 1 and launcher_final.get("shared_db_unchanged") is True):
        raise RuntimeError("profile launcher final contract mismatch")
    if not (profile_manifest.get("tree") == "f1658b690011d1a6568bd07210eed597af6ff516"
            and profile_manifest.get("source_count") == 814 and profile_manifest.get("official_score") is False):
        raise RuntimeError("profile source/official identity mismatch")
    if not (native.get("valid") and native.get("covered") and native.get("captured") and not native.get("abnormal")):
        raise RuntimeError("production GQA selected/captured evidence incomplete")
    if not (diagnosis.get("diagnostic_only") and diagnosis.get("official_score") is False
            and diagnosis["results"]["16384"]["completed"] == 128 and diagnosis["results"]["16384"]["failed"] == 0):
        raise RuntimeError("profile workload result mismatch")
    if not (validation.get("passed") and len(validation.get("windows", [])) == 1):
        raise RuntimeError("posthoc worker window validation failed")
    posthoc = json.loads((profile_dir / "actual/posthoc.json").read_text(encoding="utf-8"))
    analysis_root = ARCHIVE / SOURCES["analysis"]["path"] / "cpu-probes/pr105-analysis-232613-20261028T235339Z/output"
    analysis_identity = json.loads((analysis_root / "identity.json").read_text(encoding="utf-8"))
    analysis_summary = json.loads((analysis_root / "window-1/summary.json").read_text(encoding="utf-8"))
    trace_sha = next(x["sha256"] for x in packed["source_manifest"]["files"] if x["path"].endswith("/baseline.ixsys"))
    analysis_manifest = packed["result"]["supplemental"][0]
    if (analysis_summary.get("diagnostic_only") is not True or analysis_summary.get("official_score") is not False
            or analysis_identity.get("trace_sha256") != trace_sha or analysis_identity.get("trace_size") != 686108672):
        raise RuntimeError("supplemental analysis is not diagnostic-only")

    result = {
        "source": {"tree": profile_manifest["tree"], "file_count": profile_manifest["source_count"],
                   "base_commit": profile_manifest["base_commit"], "merged_main": profile_manifest["merged_main"],
                   "source_identity_kind": profile_manifest["source_identity_kind"]},
        "libraries": {"native_gqa_path": profile_manifest["gqa_library"], "native_gqa_sha256": profile_manifest["gqa_library_sha256"],
                      "native_gqa_build_receipt_sha256": profile_manifest["gqa_receipt_sha256"],
                      "native_w8a8_path": profile_manifest["library"], "native_w8a8_sha256": profile_manifest["library_sha256"]},
        "workload": diagnosis["results"]["16384"],
        "diagnostic_only": True, "official_score": False,
        "driver_exit_code": launcher_final["driver_exit_code"], "owner_exit_code": launcher_final["owner_exit_code"],
        "posthoc_exit_code": launcher_final["posthoc_exit_code"],
        "posthoc_status": posthoc.get("status"), "posthoc_valid": posthoc.get("valid"),
        "posthoc_native_graph_count": len(posthoc.get("native_graphs", [])),
        "fresh_fx_evidence_missing": not bool(posthoc.get("native_graphs")),
        "production_native_gqa_activation": {"valid": native["valid"], "covered": native["covered"],
            "captured": native["captured"], "selected_keys": native["selected_keys"],
            "captured_keys": native["captured_keys"], "library_sha256": native["library_sha256"]},
        "db_unchanged": launcher_final["shared_db_unchanged"],
        "db_before_snapshot_sha256": profile_manifest["tuning_snapshot"]["snapshot_sha256"],
        "collector": {"complete": state["complete"], "exit_code": state["collector_returncode"],
                      "cleanup_error": state.get("cleanup_error"), "service_sigterm_sent": state.get("service_sigterm_sent"),
                      "final_phase": state["phase"], "trace_sha256": trace_sha},
        "cleanup_completed_utc": next((x["time"] for x in state["steps"] if x.get("phase") == "cleanup_completed"), None),
        "supplemental_analysis": {"archive": analysis_manifest["archive"], "file_count": analysis_manifest["source_file_count"],
                                  "source_manifest_sha256": analysis_manifest["source_manifest_sha256"],
                                  "trace_sha256": analysis_identity["trace_sha256"],
                                  "summary_sha256": next(x["sha256"] for x in json.loads((ARCHIVE / SOURCES["analysis"]["path"] / "manifest.json").read_text(encoding="utf-8"))["files"] if x["path"].endswith("/window-1/summary.json"))},
        "raw_bundle": {"source_manifest_sha256": packed["manifest"]["source_manifest_sha256"],
                       "raw_tar_sha256": packed["raw_info"]["raw_tar_sha256"], "raw_tar_bytes": packed["raw_info"]["raw_tar_bytes"]},
        "limitation": "one cold instrumented diagnostic, not official throughput; posthoc lacks fresh FX graph evidence, and worker metadata does not prove GPU request-row order.",
    }
    summary = {
        "run_id": run_id, "scope": "PR105 16K single-cold profiled diagnostic; not official qualification or score",
        "status": "diagnostic_completed_posthoc_fresh_fx_missing", "completed": 128, "failed": 0,
        "input_len": 16384, "output_len": 1024, "num_prompts": 128,
        "driver_exit_code": 0, "owner_exit_code": 0, "posthoc_exit_code": 1,
        "conclusion": "PR105 16K单次冷态采集诊断完成128/128；driver/owner/collector exit 0，生产GQA selected/captured覆盖，source/SO/DB/清理门通过。posthoc exit 1且fresh FX图证缺项；保留诊断与trace，不作为官方成绩或稳态吞吐。",
    }
    row = {
        "run_id": run_id, "local_date": "2026-10-29", "utc_start": "2026-10-28T23:26:13.805348+00:00",
        "profile_id": "shape-gemm", "phase": "profile_diagnostic", "device": "Iluvatar BI-V150",
        "vllm_commit": profile_manifest["base_commit"], "flaggems_commit": "", "input_len": 16384,
        "output_len": 1024, "concurrency": 64, "num_prompts": 128, "profiler": "cuda",
        "status": "profile_diagnostic_completed_posthoc_fresh_fx_missing", "conclusion": summary["conclusion"],
    }
    return row, summary, result


def cpu_payload(run_id: str, key: str, status: str, conclusion: str, scope_note: str) -> tuple[dict, dict, dict]:
    directory = ARCHIVE / SOURCES[key]["path"]
    evidence_root = "cpu-probes/" + SOURCES[key]["run"]
    work_root = directory / evidence_root
    receipt_path = next(work_root.glob("runs/*/receipt.json"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    check = json.loads((work_root / "cpu-check-result.json").read_text(encoding="utf-8"))
    if receipt.get("exit_code") != 1 or receipt.get("cuda_api_used_by_owner") is not False or check.get("status") != "PASS":
        raise RuntimeError(f"{key}: CPU-only failure/guard contract mismatch")
    if key == "i32_v2":
        detail = "set_arg_attr() 收到错误的 attrs list 值，CPU Triton AST lowering 失败。"
        run_id = "20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed"
        utc_start = "2026-10-28T23:50:07.253864+00:00"
        phase = "cpu_compile"
        status = "prefill_i32_v2_compile_attrs_failed"
    else:
        detail = "A normal compile 未匹配 171100 的 selected normal hash，严格身份门停止，B 未编译。"
        run_id = "20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed"
        utc_start = "2026-10-28T23:55:32.240420+00:00"
        phase = "cpu_compile"
        status = "prefill_i32_v3_normal_identity_mismatch"
    summary = {"run_id": run_id, "scope": scope_note, "status": status,
               "exit_code": receipt["exit_code"], "cuda_api_used_by_owner": receipt["cuda_api_used_by_owner"],
               "static_guard_status": check["status"], "static_guard_cases": check.get("cpu_guard_cases"),
               "conclusion": conclusion}
    result = {"receipt": receipt, "static_check": check,
              "diagnostic": detail,
              "scope_mismatch": {"candidate_guard": "BM128/BQ16/page32", "actual_target": "BM256/BQ32/page16",
                                 "applicable_to_actual_target": False},
              "limitation": "CPU-only preparation; no tensor launch, model accuracy, GPU timing, or performance result."}
    row = {"run_id": run_id, "local_date": "2026-10-29", "utc_start": utc_start,
           "profile_id": "prefill-i32-offset", "phase": phase, "device": "CPU",
           "vllm_commit": "", "flaggems_commit": "", "input_len": "", "output_len": "",
           "concurrency": "", "num_prompts": "", "profiler": "",
           "status": status, "conclusion": conclusion}
    return row, summary, result


def write_bundle(packed: dict, row: dict, summary: dict, result: dict):
    stage_dir = packed["stage_dir"]
    packed["manifest"]["status"] = row["status"]
    write_json(stage_dir / "manifest.json", packed["manifest"])
    write_json(stage_dir / "raw.tar.gz.storage.json", {"format": "sha256-chunks-v1",
        "original_path": f"experiments/bundles/{row['run_id']}/raw.tar.gz",
        "original_bytes": packed["raw_info"]["raw_tar_bytes"],
        "original_sha256": packed["raw_info"]["raw_tar_sha256"], "parts": packed["raw_info"]["chunks"]})
    write_json(stage_dir / "summary.json", summary)
    write_json(stage_dir / "result.json", result)
    row["artifacts"] = f"experiments/bundles/{row['run_id']}"


def main():
    actual_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if actual_head != EXPECTED_HEAD:
        raise RuntimeError(f"checkout moved: expected {EXPECTED_HEAD}, got {actual_head}")
    old = REG.read_bytes()
    rows = list(csv.DictReader(io.StringIO(old.decode("utf-8-sig"))))
    if len(rows) != 470:
        raise RuntimeError(f"expected 470 existing rows unchanged, got {len(rows)}")
    expected_ids = [
        "20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2",
        "20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed",
        "20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed",
    ]
    if set(expected_ids) & {row["run_id"] for row in rows}:
        raise RuntimeError("target run already registered")

    packed_profile = pack_run(expected_ids[0], "profile", ["analysis"])
    profile_row, profile_summary, profile_result = profile_payload(expected_ids[0], packed_profile)
    write_bundle(packed_profile, profile_row, profile_summary, profile_result)
    print(json.dumps({"staged_archive": expected_ids[0], "raw_tar_sha256": packed_profile["raw_info"]["raw_tar_sha256"],
                      "raw_tar_bytes": packed_profile["raw_info"]["raw_tar_bytes"],
                      "chunks": len(packed_profile["raw_info"]["chunks"])}, ensure_ascii=False), flush=True)

    cpu_specs = [
        (expected_ids[1], "i32_v2", "prefill_i32_v2_compile_attrs_failed",
         "i32-offset v2 CPU-only编译因set_arg_attr attrs类型错误停止；静态guard通过但其BM128/BQ16/page32范围与实际目标BM256/BQ32/page16不符。无CUDA调用或性能结论。",
         "i32 offset v2 compile-only + ABI attrs fixture"),
        (expected_ids[2], "i32_v3", "prefill_i32_v3_normal_identity_mismatch",
         "i32-offset v3 CPU-only在A normal身份门停止，B未编译；静态guard的BM128/BQ16/page32范围与实际目标BM256/BQ32/page16不符。无CUDA调用或性能结论。",
         "i32 offset v3 compile-only + strict A identity gate"),
    ]
    staged = [{"row": profile_row, "summary": profile_summary, "result": profile_result, "packed": packed_profile}]
    for run_id, key, status, conclusion, scope in cpu_specs:
        packed = pack_run(run_id, key)
        row, summary, result = cpu_payload(run_id, key, status, conclusion, scope)
        write_bundle(packed, row, summary, result)
        staged.append({"row": row, "summary": summary, "result": result, "packed": packed})
        print(json.dumps({"staged_archive": run_id, "raw_tar_sha256": packed["raw_info"]["raw_tar_sha256"],
                          "raw_tar_bytes": packed["raw_info"]["raw_tar_bytes"],
                          "chunks": len(packed["raw_info"]["chunks"])}, ensure_ascii=False), flush=True)

    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=rows[0].keys(), lineterminator="\n")
    for item in staged:
        writer.writerow({key: item["row"].get(key, "") for key in writer.fieldnames})
    with REG.open("ab") as f:
        f.write(buf.getvalue().encode("utf-8"))
    if not REG.read_bytes().startswith(old):
        raise RuntimeError("previous registry bytes changed")
    result = subprocess.run([sys.executable, "scripts/build_team_view.py"], cwd=REPO,
                            check=True, capture_output=True, text=True, encoding="utf-8")
    generated = json.loads(result.stdout)
    if generated.get("registry_records") != 473 or generated.get("unique_runs") != 470:
        raise RuntimeError(f"team view count mismatch: {generated}")
    note = REPO / "analysis/stage-pr105-232613-prefill-i32-20261029.md"
    note.write_text(
        "# PR105 232613 诊断与 prefill i32 CPU 记录 staging\n\n"
        "本地暂存3条新记录（旧470行原始registry字节保留），未commit/push。232613为单次带ixsys的冷态16K诊断，128/128成功；driver/owner/collector exit 0，posthoc exit 1且fresh FX图证缺项，非官方成绩。其18文件只读分析作为独立supplemental archive加入同一raw bundle，原manifest分别保留。两次i32尝试只在CPU编译/身份门失败；BM256/BQ32/page16实际目标与旧guard的BM128/BQ16/page32不同。\n\n"
        "详细成员、原始SHA与1MiB分块见各 `experiments/bundles/<run_id>/`；实验表/方法页由真实 `scripts/build_team_view.py` 更新。发布payload尚未生成，等root安排后与后续终态批量构建。\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({"prior_rows": 470, "appended_rows": 3, "new_rows": 473,
                      "staged": [{"run_id": x["row"]["run_id"], "status": x["row"]["status"],
                                  "bundle": x["row"]["artifacts"],
                                  "raw_sha256": x["packed"]["raw_info"]["raw_tar_sha256"],
                                  "raw_bytes": x["packed"]["raw_info"]["raw_tar_bytes"],
                                  "chunks": len(x["packed"]["raw_info"]["chunks"])} for x in staged],
                      "generated_view": generated, "note": str(note)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
