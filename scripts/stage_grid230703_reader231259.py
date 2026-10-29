from __future__ import annotations

import csv
import hashlib
import io
import json
import os
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


def sha(path: Path) -> str:
    h = hashlib.sha256()
    path = long_path(path)
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def long_path(path: Path) -> Path:
    value = str(path)
    if value.startswith("\\\\?\\"):
        return Path(value)
    p = Path(path).resolve()
    value = str(p)
    return Path("\\\\?\\" + value) if os.name == "nt" and len(value) >= 240 else p


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def stage(run_id: str, source_rel: str, source_count: int, row: dict, summary: dict, result: dict) -> dict:
    src = ARCHIVE / source_rel
    manifest_path = src / "manifest.json"
    source_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if source_manifest.get("run") != run_id:
        raise RuntimeError(f"{source_rel}: source run mismatch")
    files = source_manifest["files"]
    if len(files) != source_count:
        raise RuntimeError(f"{source_rel}: expected {source_count} files, got {len(files)}")
    for item in files:
        p = long_path(src / item["path"])
        if not p.is_file() or p.stat().st_size != item["bytes"] or sha(p) != item["sha256"]:
            raise RuntimeError(f"archive evidence mismatch: {p}")
    bundle = EXP / "bundles" / run_id
    bundle.mkdir(parents=True, exist_ok=False)
    fd, tmp_name = tempfile.mkstemp(prefix="stage-pr105-grid-reader-", suffix=".tar.gz")
    os.close(fd)
    try:
        with tarfile.open(tmp_name, "w:gz", compresslevel=6) as tf:
            for item in files:
                tf.add(long_path(src / item["path"]), arcname=f"framework/{run_id}/{item['path']}", recursive=False)
            tf.add(long_path(manifest_path), arcname=f"framework/{run_id}/archive-manifest.json", recursive=False)
        raw = Path(tmp_name)
        raw_sha, raw_bytes = sha(raw), raw.stat().st_size
        blob_dir = EXP / "raw-blobs" / raw_sha
        blob_dir.mkdir(parents=True, exist_ok=True)
        parts = []
        with raw.open("rb") as f:
            index = 0
            while True:
                block = f.read(CHUNK)
                if not block:
                    break
                digest = hashlib.sha256(block).hexdigest()
                part = blob_dir / f"{index:04d}.part"
                if part.exists():
                    if sha(part) != digest:
                        raise RuntimeError(f"raw chunk collision: {part}")
                else:
                    part.write_bytes(block)
                parts.append({"path": part.relative_to(REPO).as_posix(), "bytes": len(block), "sha256": digest})
                index += 1
        write_json(bundle / "manifest.json", {
            "run_id": run_id, "status": row["status"], "source_archive": source_rel,
            "source_file_count": len(files), "source_manifest_sha256": sha(manifest_path),
            "source_files": files, "raw_tar_sha256": raw_sha, "raw_tar_bytes": raw_bytes,
        })
        write_json(bundle / "raw.tar.gz.storage.json", {
            "format": "sha256-chunks-v1", "original_path": f"experiments/bundles/{run_id}/raw.tar.gz",
            "original_bytes": raw_bytes, "original_sha256": raw_sha, "parts": parts,
        })
        write_json(bundle / "summary.json", summary)
        write_json(bundle / "result.json", result)
        row["artifacts"] = f"experiments/bundles/{run_id}"
        return {"run_id": run_id, "source_files": len(files), "source_manifest_sha256": sha(manifest_path),
                "raw_tar_bytes": raw_bytes, "raw_tar_sha256": raw_sha, "chunks": len(parts), "bundle": row["artifacts"]}
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def main() -> None:
    head = os.popen(f'git -C "{REPO}" rev-parse HEAD').read().strip()
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"checkout moved: expected {EXPECTED_HEAD}, got {head}")
    old = REG.read_bytes()
    reader = csv.DictReader(io.StringIO(old.decode("utf-8-sig")))
    rows, header = list(reader), reader.fieldnames
    if len(rows) != 468:
        raise RuntimeError(f"expected 468 existing data rows unchanged, got {len(rows)}")
    existing = {r["run_id"] for r in rows}
    run_grid = "20261028T230703857834Z-native-gqa-grid-order-hotspot-component"
    run_profile = "20261028T231259Z-pr105-hotspot16k-single-diagnostic"
    if {run_grid, run_profile} & existing:
        raise RuntimeError("one of target runs already registered")

    grid_src = ARCHIVE / "native-gqa-grid-order-20261029/batch-230703-component-negative/framework" / run_grid / "results.json"
    grid = json.loads(grid_src.read_text(encoding="utf-8"))
    event, wall = grid["summary"]["event"], grid["summary"]["wall"]
    grid_summary = {
        "run_id": run_grid, "scope": "BI-V150 native GQA N64/S2 component; CTA/grid order only, not model or official qualification",
        "status": "component_negative_stopped", "event_ms": event, "wall_ms": wall,
        "correctness_gate_count": len(grid["checks"]),
        "correctness_all_passed": all(all(v is True for v in c.get("checks", {}).values()) for c in grid["checks"]),
        "benchmark_or_model_score": False,
        "conclusion": "32-call ABBA：event 0.409491345→0.410414010 ms，候选慢0.2253%；wall 0.412703422→0.413091609 ms，慢0.0941%。9类数值/Graph/side/输入RNG门通过，按负结果停止；非模型准确率或官方成绩。",
    }
    grid_row = {k: "" for k in header}
    grid_row.update(run_id=run_grid, local_date="2026-10-29", utc_start="2026-10-28T23:07:03.857834+00:00",
                    profile_id="shape-gemm", phase="component", device="Iluvatar BI-V150",
                    status="shape_gemm_native_gqa_grid_order_negative", conclusion=grid_summary["conclusion"])

    profile_src = ARCHIVE / "pr105-hotspot16k-20261029/batch-231259-diagnostic-failed"
    profile_manifest = json.loads((profile_src / "manifest.json").read_text(encoding="utf-8"))
    profile = json.loads((profile_src / "profiles/20261028T231259Z-pr105-hotspot16k-single-diagnostic/manifest.json").read_text(encoding="utf-8"))
    profile_summary = {
        "run_id": run_profile, "scope": "PR105 16K single cold hotspot diagnostic; prebenchmark reader gate only",
        "status": "reader_gate_failed_before_benchmark", "source_file_count": len(profile_manifest["files"]),
        "benchmark_started": False, "successful_requests": 0, "throughput_sample": False,
        "gqa_library_sha256": profile["gqa_library_sha256"], "source_tree": profile["tree"],
        "failure": "reader incorrectly required overlap_v=false while PR105 macro1 receipt/real GQA markers have overlap_v=true; valid INSTALL and S2/S4 SELECTED/CAPTURED records were rejected before requests.",
        "model_error": False, "performance_result": False,
        "conclusion": "预检在benchmark前因GQA reader契约错误退出；没有模型请求、吞吐样本或性能/数值结论。不是模型错误。清理及DB/source恢复通过。",
    }
    profile_row = {k: "" for k in header}
    profile_row.update(run_id=run_profile, local_date="2026-10-29", utc_start="2026-10-28T23:12:59+00:00",
                       profile_id="shape-gemm", phase="profile_diagnostic", device="Iluvatar BI-V150",
                       vllm_commit="b3b87d2a1c13448bd8c6bc24e8045c0458b8b9dd", input_len="16384",
                       output_len="1024", concurrency="64", num_prompts="128", profiler="cuda",
                       status="profile_diagnostic_reader_gate_failed_before_benchmark", conclusion=profile_summary["conclusion"])

    records = [
        (grid_row, "native-gqa-grid-order-20261029/batch-230703-component-negative", 78, grid_summary,
         {"source_result": grid, "source_result_sha256": sha(grid_src)}),
        (profile_row, "pr105-hotspot16k-20261029/batch-231259-diagnostic-failed", 1609, profile_summary,
         {"profile_manifest": profile, "terminal_review": (ROOT / "analysis/pr105-hotspot16k-20261029/231259-terminal-review.md").read_text(encoding="utf-8")}),
    ]
    staged = []
    for row, source_rel, count, summary, result in records:
        out = stage(row["run_id"], source_rel, count, row, summary, result)
        staged.append(out)
        short = REPO / "team/runs/bi-v150" / f"{row['run_id']}.md"
        short.parent.mkdir(parents=True, exist_ok=True)
        short.write_text(f"# {row['run_id']}\n\n- 尝试：{summary['scope']}。\n- 结果：{summary['conclusion']}\n- 原件：`{out['bundle']}`；source manifest SHA256 `{out['source_manifest_sha256']}`。\n- 处理：保留原件；v2诊断终态未到，不在此预填。\n", encoding="utf-8", newline="\n")
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=header, lineterminator="\n")
    for row, *_ in records:
        writer.writerow({k: row.get(k, "") for k in header})
    with REG.open("ab") as f:
        f.write(buf.getvalue().encode("utf-8"))
    if not REG.read_bytes().startswith(old):
        raise RuntimeError("registry prior bytes changed")
    note = REPO / "analysis/stage-grid230703-reader231259-20261029.md"
    note.write_text("# grid 230703 与 reader 231259 登记准备\n\n本地追加两条实验登记及 1 MiB SHA256 raw bundle，未提交/推送。输入原件分别来自 `archive/native-gqa-grid-order-20261029/batch-230703-component-negative`（78 files）与 `archive/pr105-hotspot16k-20261029/batch-231259-diagnostic-failed`（1609 files）；source manifest 和原件 bytes/SHA 在stage时核对。231259 是benchmark前reader资格失败、0请求，不是模型错误；等待v2实际终态后再另行登记，不预填。\n", encoding="utf-8", newline="\n")
    print(json.dumps({"prior_data_rows": 468, "appended_rows": 2, "new_data_rows": 470,
                      "staged": staged, "registry_old_bytes_preserved": True,
                      "registry_sha256": sha(REG), "script": str(Path(__file__).resolve()),
                      "stage_note": str(note)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
