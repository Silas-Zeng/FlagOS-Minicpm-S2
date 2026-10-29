"""Build local Git blob payloads and source tree for the four-run prefill i32 component batch.

This script only writes the requested local output directory. It never commits, pushes,
or calls GitHub. Raw evidence files ignored by Git are included through each bundle's
raw.tar.gz.storage.json chunk references.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "35bfd52ba722bd2c6b2403184d0996f625634b66"
PUBLISHED_PARENT = "9da89b753e36e2c7179854f80672c650a272228a"
BASE_TREE = "c64cf635a62613df761e5066791d785f65534669"
RUNS = [
    "20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component",
    "20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component",
    "20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component",
    "20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component",
]
GENERATED_OLD_RUNS = [
    "team/runs/bi-v150/20261026T150802838380Z-main594-m64-mm-provider-probe.md",
    "team/runs/bi-v150/20261026T153134266216Z-main594-m64-fixed-address-component.md",
    "team/runs/bi-v150/20261026T154111Z-main594-official-control-four-rounds.md",
    "team/runs/bi-v150/20261026T164443Z-main594-control-16k-four-rounds.md",
    "team/runs/bi-v150/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds.md",
    "team/runs/bi-v150/20261026T173900314676Z-main594-m32-mm-provider-probe.md",
    "team/runs/bi-v150/20261026T174414509153Z-main594-m32-fixed-address-component.md",
    "team/runs/bi-v150/20261026T180653Z-main594-m32-fixed-address-16384-four-rounds.md",
    "team/runs/bi-v150/20261027T190017939358Z-qkv-bn32-component.md",
]
CHUNK_BYTES = 1024 * 1024


def git(*args: str, data: bytes | None = None, env=None) -> bytes:
    p = subprocess.run(["git", *args], cwd=REPO, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace"))
    return p.stdout


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tracked_changes() -> list[str]:
    raw = git("diff", "--name-only", "HEAD", "--")
    return [x.decode("utf-8") for x in raw.splitlines() if x]


def changed_since_head(rel: str) -> bool:
    path = REPO / rel
    try:
        base = git("show", f"HEAD:{rel}")
    except RuntimeError:
        return True
    return git("hash-object", "--stdin", data=path.read_bytes()).decode("ascii").strip() != \
        git("hash-object", "--stdin", data=base).decode("ascii").strip()


def registry_rows() -> list[dict[str, str]]:
    with (REPO / "experiments/registry.csv").open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def append_bundle_files(paths: set[str], row: dict[str, str]) -> None:
    bundle_rel = row.get("artifacts", "")
    if not bundle_rel:
        raise RuntimeError(f"registry row has no artifact bundle: {row.get('run_id')}")
    bundle = REPO / bundle_rel
    if not bundle.is_dir():
        raise RuntimeError(f"bundle directory missing: {bundle_rel}")
    for p in bundle.rglob("*"):
        if p.is_file() and p.name != "raw.tar.gz":
            paths.add(p.relative_to(REPO).as_posix())
    storage = json.loads((bundle / "raw.tar.gz.storage.json").read_text(encoding="utf-8"))
    if storage.get("format") != "sha256-chunks-v1":
        raise RuntimeError(f"unsupported raw storage format: {row.get('run_id')}")
    # Explicitly include ignored raw-blobs payloads referenced by the bundle.
    for part in storage["parts"]:
        part_path = REPO / part["path"]
        data = part_path.read_bytes()
        if len(data) != part["bytes"] or sha256(data) != part["sha256"]:
            raise RuntimeError(f"raw evidence chunk mismatch: {part['path']}")
        paths.add(part_path.relative_to(REPO).as_posix())


def publication_paths() -> list[str]:
    changes = tracked_changes()
    permitted_tracked = {
        "experiments/registry.csv", "scripts/build_team_view.py",
        "team/experiments.md", "team/generated-index.md", "team/README.md",
        "team/platforms/bi-v150.md", "team/platforms/cpu.md", "team/methods/shape-gemm.md",
        "team/methods/prefill-i32-offset.md",
        "team/runs/cpu/20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed.md",
        "team/runs/cpu/20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed.md",
        "team/runs/cpu/20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed.md",
        "team/runs/cpu/20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic.md",
        *GENERATED_OLD_RUNS,
    }
    if set(changes) - permitted_tracked:
        raise RuntimeError(f"unexpected tracked changes; inspect before publishing: {sorted(set(changes)-permitted_tracked)}")
    paths: set[str] = set(changes)
    fixed = [
        "scripts/stage_grid230703_reader231259.py",
        "scripts/stage_pr105_232613_prefill_i32_20261029.py",
        "scripts/stage_prefill_i32_v5v6_20261029.py",
        "scripts/build_grid_reader_publication_payload.py",
        "scripts/stage_prefill_i32_component_batch_20261029.py",
        "scripts/build_prefill_i32_component_publication_payload.py",
        "analysis/stage-prefill-i32-component-batch-20261029.md",
        "scripts/build_team_view.py",
        "analysis/stage-grid230703-reader231259-20261029.md",
        "analysis/stage-pr105-232613-prefill-i32-20261029.md",
        "analysis/publication-builder-grid-reader-v2.md",
        "team/experiments.md", "team/generated-index.md", "team/README.md",
        "team/platforms/bi-v150.md", "team/platforms/cpu.md", "team/methods/shape-gemm.md",
        "team/methods/prefill-i32-offset.md", *GENERATED_OLD_RUNS,
        "team/runs/bi-v150/20261028T230703857834Z-native-gqa-grid-order-hotspot-component.md",
        "team/runs/bi-v150/20261028T231259Z-pr105-hotspot16k-single-diagnostic.md",
        "team/runs/bi-v150/20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2.md",
        "team/runs/bi-v150/20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component.md",
        "team/runs/bi-v150/20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component.md",
        "team/runs/bi-v150/20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component.md",
        "team/runs/bi-v150/20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component.md",
        "team/runs/cpu/20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed.md",
        "team/runs/cpu/20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed.md",
        "team/runs/cpu/20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed.md",
        "team/runs/cpu/20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic.md",
        "team/runs/bi-v150/20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component.md",
        "team/runs/bi-v150/20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component.md",
        "team/runs/bi-v150/20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component.md",
        "team/runs/bi-v150/20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component.md",
        "scripts/stage_prefill_i32_component_batch_20261029.py",
        "scripts/build_prefill_i32_component_publication_payload.py",
        "analysis/stage-prefill-i32-component-batch-20261029.md",
    ]
    for rel in fixed:
        if not (REPO / rel).is_file():
            raise RuntimeError(f"expected staged file missing: {rel}")
        if changed_since_head(rel):
            paths.add(rel)

    rows = registry_rows()
    by_id = {r["run_id"]: r for r in rows}
    if len(rows) != 479 or len(by_id) != 476:
        raise RuntimeError(f"registry count mismatch: rows={len(rows)} unique={len(by_id)}")
    for run_id in RUNS:
        row = by_id.get(run_id)
        if not row or not row.get("artifacts"):
            raise RuntimeError(f"expected staged run missing: {run_id}")
        if any(word in row.get("status", "").lower() for word in ("pending", "running", "in_progress")):
            raise RuntimeError(f"nonterminal run: {run_id} / {row['status']}")
        append_bundle_files(paths, row)
        short_dir = "cpu" if row.get("device") == "CPU" else "bi-v150"
        short = f"team/runs/{short_dir}/{run_id}.md"
        if not (REPO / short).is_file():
            raise RuntimeError(f"short record missing: {short}")
        paths.add(short)
        bundle = REPO / row["artifacts"]
        if not (bundle / "summary.json").is_file() or not (bundle / "result.json").is_file():
            raise RuntimeError(f"bundle summary/result missing: {run_id}")
    return sorted(paths)


def build_payload(rel: str, out: Path) -> dict:
    path = REPO / rel
    if not path.is_file():
        raise RuntimeError(f"payload source is not a file: {rel}")
    data = path.read_bytes()
    blob_sha = git("hash-object", "-w", "--stdin", data=data).decode("ascii").strip()
    # Independently verify the Git blob framing/hash implementation.
    framed = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    check = hashlib.sha1(framed).hexdigest()
    if check != blob_sha:
        raise RuntimeError(f"Git blob SHA mismatch for {rel}: {check} != {blob_sha}")
    payload_dir = out / "payloads" / blob_sha
    payload_dir.mkdir(parents=True, exist_ok=True)
    chunks = []
    for i, start in enumerate(range(0, len(data), CHUNK_BYTES)):
        block = data[start:start + CHUNK_BYTES]
        name = f"{i:06d}.part"
        target = payload_dir / name
        target.write_bytes(block)
        chunks.append({"path": target.relative_to(out).as_posix(), "bytes": len(block), "sha256": sha256(block)})
    if not data:
        target = payload_dir / "000000.part"
        target.write_bytes(b"")
        chunks.append({"path": target.relative_to(out).as_posix(), "bytes": 0, "sha256": sha256(b"")})
    return {"path": rel, "mode": "100644", "type": "blob", "git_blob_sha1": blob_sha,
            "bytes": len(data), "payload_sha256": sha256(data), "chunks": chunks}


def build_tree(entries: list[dict], out: Path) -> str:
    # This checkout is a partial clone: the base tree is present but many unrelated
    # blobs are promisor objects. Rebuild only changed ancestor trees, preserving
    # every untouched object id, so no network fetch is needed.
    changes = {e["path"]: (e["mode"], e["git_blob_sha1"]) for e in entries}
    empty_tree = git("hash-object", "-w", "-t", "tree", "--stdin", data=b"").decode().strip()

    def parse_tree(oid: str) -> dict[bytes, tuple[str, str]]:
        raw = git("cat-file", "tree", oid)
        found: dict[bytes, tuple[str, str]] = {}
        pos = 0
        while pos < len(raw):
            space = raw.index(b" ", pos)
            nul = raw.index(b"\0", space)
            mode = raw[pos:space].decode("ascii")
            name = raw[space + 1:nul]
            child = raw[nul + 1:nul + 21].hex()
            found[name] = (mode, child)
            pos = nul + 21
        return found

    def write_tree(found: dict[bytes, tuple[str, str]]) -> str:
        ordered = sorted(found.items(), key=lambda item: item[0] + (b"/" if item[1][0] == "40000" else b""))
        body = b"".join(mode.encode("ascii") + b" " + name + b"\0" + bytes.fromhex(oid)
                        for name, (mode, oid) in ordered)
        return git("hash-object", "-w", "-t", "tree", "--stdin", data=body).decode("ascii").strip()

    def update(tree_oid: str, subset: dict[str, tuple[str, str]]) -> str:
        found = parse_tree(tree_oid)
        grouped: dict[bytes, dict[str, tuple[str, str]]] = {}
        for path, replacement in subset.items():
            first, sep, rest = path.partition("/")
            name = first.encode("utf-8")
            if sep:
                grouped.setdefault(name, {})[rest] = replacement
            elif replacement[0] == "DELETE":
                found.pop(name, None)
            else:
                found[name] = replacement
        for name, nested in grouped.items():
            current = found.get(name)
            if current and current[0] != "40000":
                raise RuntimeError(f"cannot replace non-tree path with directory: {name!r}")
            child = update(current[1] if current else empty_tree, nested)
            found[name] = ("40000", child)
        return write_tree(found)

    return update(BASE_TREE, changes)


def build_source_commit(tree_sha: str) -> str:
    name = git("config", "user.name").decode("utf-8").strip()
    email = git("config", "user.email").decode("utf-8").strip()
    if not name or not email:
        raise RuntimeError("configured Git author identity is required for a reproducible source commit")
    epoch = str(int(datetime.now(timezone.utc).timestamp()))
    identity = f"{name} <{email}> {epoch} +0000"
    content = (f"tree {tree_sha}\nparent {PUBLISHED_PARENT}\nauthor {identity}\ncommitter {identity}\n\n"
               "记录PR105诊断与prefill i32 CPU筛查结果\n").encode("utf-8")
    return git("hash-object", "-w", "-t", "commit", "--stdin", data=content).decode("ascii").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPO.parent.parent / "analysis/publication-prefill-i32-component-batch-20261029")
    args = parser.parse_args()
    head = git("rev-parse", "HEAD").decode().strip()
    head_tree = git("rev-parse", "HEAD^{tree}").decode().strip()
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"expected incremental source HEAD {EXPECTED_HEAD}, got {head}")
    if head_tree != BASE_TREE:
        raise RuntimeError(f"HEAD tree {head_tree} does not match published base tree {BASE_TREE}")
    # The plan directory is local generated output; allow deterministic refreshes
    # after a reviewed correction to registry/bundle metadata.
    relpaths = publication_paths()
    args.out.mkdir(parents=True, exist_ok=True)
    entries = [build_payload(rel, args.out) for rel in relpaths]
    final_tree = build_tree(entries, args.out)
    source_commit = build_source_commit(final_tree)
    pr_body = """## 变更内容

新增四条 BI-V150 prefill i32 单层组件记录，保留四份原始归档、source/命令/状态和完整 SHA 分块证据，并更新 registry、中文团队视图及方法页。没有改实验框架或官方 benchmark。

## 结果与边界

- 前三次分别因GQA依赖遗漏、scope断言和结果记录器异常退出；都未形成候选数值或计时结果，不记为正确性/性能失败。
- 第四次 M2048/KV16384、BM128/BQ16/page16 单层组件通过既定数值门；FP64为采样。ABBA Event 8.347575→9.235266 ms（慢10.63%），wall 8.441216→9.303357 ms（慢10.21%），按负向停止。
- 该静态资源变化没有转化为吞吐收益。结果只覆盖单层合成shape，不是完整模型、准确率、生产接入或官方成绩。

仅同步实验记录，不申请优化代码合并或更新基线。
"""
    pr_path = args.out / "PR-body.md"
    pr_path.write_text(pr_body, encoding="utf-8", newline="\n")
    plan = {
        "schema": "local-incremental-git-tree-plan-v2",
        "published_parent_commit": PUBLISHED_PARENT,
        "base_tree": BASE_TREE,
        "source_head": head,
        "source_head_tree": head_tree,
        "expected_tree": final_tree,
        "source_commit": source_commit,
        "included_runs": RUNS,
        "incremental_scope": "HEAD-to-worktree publication delta containing all seven registered runs, generated team views, bundles, and referenced 1MiB evidence chunks",
        "entry_count": len(entries), "entries": entries,
        "publication_actions": {"commit_ref_updated": False, "push": False, "github_write": False},
        "pr_body_file": "PR-body.md",
    }
    plan_path = args.out / "tree-plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"plan": str(plan_path), "entries": len(entries), "parent": PUBLISHED_PARENT,
                      "base_tree": BASE_TREE, "payload_root": str(args.out / "payloads"),
                      "expected_tree": final_tree, "source_commit": source_commit,
                      "tree_plan_sha256": sha256(plan_path.read_bytes()), "dry_local_only": True}, indent=2))


if __name__ == "__main__":
    main()
