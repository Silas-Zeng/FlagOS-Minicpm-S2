#!/usr/bin/env python3
"""CPU-only packaging of the already measured 080656 SQL+C3 candidate.

Read the pinned local Git objects, apply the two unchanged patches in fresh
scratch clones, compare every archived plugin file, then verify one-step apply.
No framework imports, installation, device access, commit, push or network.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import posixpath
import subprocess


ROOT = Path(__file__).resolve().parents[3]
BASE = "13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0"
RETAINED = "d60b02367a852826f653165953f31b6dc696658e"
REFERENCE = ROOT / "tmp/src/vllm-plugin-FL"
PERFORMANCE = ROOT / "patches/vllm-plugin-FL-biv150-performance.patch"
JOINT = ROOT / "patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode.patch"
OUTPUT = ROOT / "patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch"
OFFICIAL = ROOT / "experiments/official/20261021T092944Z-sql-mixed-official"
SCREEN = ROOT / "experiments/framework/20261021T080656Z-sql-mixed-screen"
REMOTE_SOURCE = "/workspace/experiments/minicpm-s2/code/sql-mixed-20261021T080656Z"
INPUT_SHA = {
    PERFORMANCE: "6e8d9fa631b7e2f9aa0a848443e602c224c1bbd1f0787b417f78dd3b9f51e99b",
    JOINT: "4b3e2e52b01d04a0f0477ae4e9b8dc3fed3c1f721360af3bbe6b01014572bbba",
}
CHANGED = {
    "vllm_fl/__init__.py",
    "vllm_fl/dispatch/backends/vendor/iluvatar/iluvatar.py",
    "vllm_fl/patches/biv150_runtime.py",
    "vllm_fl/patches/biv150_top_p_triton.py",
    "vllm_fl/patches/biv150_sql_reflection.py",
    "vllm_fl/patches/biv150_decode_launch_runtime.py",
    "vllm_fl/patches/biv150_mixed_decode.py",
    "vllm_fl/platform.py",
    "vllm_fl/worker/model_runner.py",
}
TOP_LEVEL = {"pyproject.toml", "setup.py", "setup.cfg", "README.md", "LICENSE"}
COMMANDS = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args, input=None):
    command = ["git", "-c", "core.autocrlf=false", "-c", "core.safecrlf=false",
               "-c", "core.symlinks=false", "-C", str(repo), *args]
    result = subprocess.run(command, input=input, capture_output=True, check=True)
    COMMANDS.append({"argv": command, "exit_code": result.returncode,
                     "stdout_bytes": len(result.stdout), "stdout_sha256": sha(result.stdout),
                     "stderr": result.stderr.decode("utf-8", errors="replace")})
    return result.stdout


def fresh_clone(path):
    if path.exists():
        raise RuntimeError("scratch checkout already exists: " + str(path))
    command = ["git", "clone", "--quiet", "--no-checkout", "--local", "--no-hardlinks",
               str(REFERENCE), str(path)]
    result = subprocess.run(command, capture_output=True, check=True)
    COMMANDS.append({"argv": command, "exit_code": result.returncode,
                     "stderr": result.stderr.decode("utf-8", errors="replace")})
    # Git's Windows symlink placeholders keep the index's original mode 120000.
    git(path, "config", "core.autocrlf", "false")
    git(path, "config", "core.symlinks", "false")
    git(path, "checkout", "--quiet", "--detach", BASE)
    if git(path, "rev-parse", "HEAD").decode().strip() != BASE:
        raise RuntimeError("scratch did not start at the exact base")


def index_snapshot(repo):
    entries = {}
    for item in git(repo, "ls-files", "--stage", "-z").split(b"\0"):
        if not item:
            continue
        header, name = item.split(b"\t", 1)
        mode, oid, stage = header.decode("ascii").split()
        if stage != "0" or mode not in {"100644", "100755", "120000"}:
            raise RuntimeError("unsupported index entry")
        entries[name.decode("utf-8")] = {"mode": mode, "git_blob": oid}
    ids = sorted({item["git_blob"] for item in entries.values()})
    stream = git(repo, "cat-file", "--batch", input=("\n".join(ids) + "\n").encode())
    offset, blobs = 0, {}
    for oid in ids:
        end = stream.index(b"\n", offset)
        actual, kind, size = stream[offset:end].decode("ascii").split()
        if actual != oid or kind != "blob":
            raise RuntimeError("unexpected Git object")
        offset, size = end + 1, int(size)
        blobs[oid] = stream[offset:offset + size]
        offset += size
        if stream[offset:offset + 1] != b"\n":
            raise RuntimeError("invalid Git object framing")
        offset += 1
    if offset != len(stream):
        raise RuntimeError("unexpected trailing Git object data")
    for item in entries.values():
        item["sha256"] = sha(blobs[item["git_blob"]])
    return entries, blobs


def content(name, entries, blobs, seen=()):
    if name in seen:
        raise RuntimeError("symlink cycle")
    item = entries[name]
    data = blobs[item["git_blob"]]
    if item["mode"] != "120000":
        return data, name
    target = data.decode("utf-8")
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
    if posixpath.isabs(target) or resolved == ".." or resolved.startswith("../"):
        raise RuntimeError("symlink escapes repository")
    return content(resolved, entries, blobs, (*seen, name))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    if OUTPUT.exists() != args.verify_existing:
        parser.error("use --verify-existing only after the packaged patch exists")
    for path, expected in INPUT_SHA.items():
        if sha(path.read_bytes()) != expected:
            raise RuntimeError("input patch identity mismatch: " + str(path))
    if git(REFERENCE, "rev-parse", "HEAD").decode().strip() != BASE:
        raise RuntimeError("local pristine reference HEAD is not the pinned 13eb")
    base_tree = git(REFERENCE, "rev-parse", BASE + "^{tree}").decode().strip()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    scratch = ROOT / "tmp/patch-check" / ("sql-mixed-full-" + stamp)
    scratch.mkdir(exist_ok=False)
    stacked, single = scratch / "stacked", scratch / "one-step"
    fresh_clone(stacked)
    base_entries, _ = index_snapshot(stacked)
    for patch in [PERFORMANCE, JOINT]:
        git(stacked, "apply", "--check", "--index", str(patch))
        git(stacked, "apply", "--index", str(patch))
    entries, blobs = index_snapshot(stacked)
    changed = set(git(stacked, "diff", "--cached", "--name-only", "-z", BASE).decode().strip("\0").split("\0"))
    if changed != CHANGED:
        raise RuntimeError("unexpected changed paths: " + repr(changed ^ CHANGED))
    for name in CHANGED:
        compile(blobs[entries[name]["git_blob"]], name, "exec")
    official = json.loads((OFFICIAL / "manifest.json").read_bytes())
    screen = json.loads((SCREEN / "manifest.json").read_bytes())
    if official["source_dir"] != REMOTE_SOURCE or screen["source_dir"] != REMOTE_SOURCE:
        raise RuntimeError("archive source identity mismatch")
    expected = {name.removeprefix("plugin/"): value for name, value in official["sha256"].items()
                if name.startswith("plugin/")}
    metadata = expected.pop("base-revision.txt")
    metadata_bytes = (OFFICIAL / "source/plugin/base-revision.txt").read_bytes()
    if sha(metadata_bytes) != metadata or metadata_bytes.strip().decode() != RETAINED:
        raise RuntimeError("archive provenance metadata mismatch")
    selected = {name for name in entries if name.startswith("vllm_fl/") or name in TOP_LEVEL}
    if selected != set(expected):
        raise RuntimeError("archive plugin path set mismatch: " + repr(selected ^ set(expected)))
    comparisons = {}
    links = {}
    for name, expected_sha in sorted(expected.items()):
        archived = (OFFICIAL / "source/plugin" / name).read_bytes()
        actual, final_name = content(name, entries, blobs)
        if sha(archived) != expected_sha or sha(actual) != expected_sha or actual != archived:
            raise RuntimeError("archive bytes mismatch: " + name)
        comparisons[name] = {"sha256": expected_sha, "bytes": len(actual),
                             "git_mode": entries[name]["mode"], "byte_equal": True}
        if entries[name]["mode"] == "120000":
            if entries[name] != base_entries[name]:
                raise RuntimeError("base symlink identity changed")
            links[name] = {"mode": "120000", "unchanged_from_base": True,
                           "link_target": blobs[entries[name]["git_blob"]].decode(),
                           "link_blob_sha256": entries[name]["sha256"],
                           "resolved_path": final_name, "resolved_sha256": expected_sha,
                           "archive_copy_dereferenced": True}
    screen_checks = {}
    for remote, expected_sha in screen["sha256"].items():
        if remote.startswith(REMOTE_SOURCE + "/"):
            name = remote.removeprefix(REMOTE_SOURCE + "/")
            actual, _ = content(name, entries, blobs)
            if sha(actual) != expected_sha:
                raise RuntimeError("080656 screen core identity mismatch: " + name)
            screen_checks[name] = expected_sha
    patch = git(stacked, "diff", "--cached", "--binary", "--full-index", "--no-ext-diff", "--no-color", BASE, "--")
    patch_for_check = scratch / OUTPUT.name
    patch_for_check.write_bytes(patch)
    fresh_clone(single)
    git(single, "apply", "--check", "--index", str(patch_for_check))
    git(single, "apply", "--index", str(patch_for_check))
    one_entries, _ = index_snapshot(single)
    stacked_tree = git(stacked, "write-tree").decode().strip()
    one_tree = git(single, "write-tree").decode().strip()
    if entries != one_entries or stacked_tree != one_tree:
        raise RuntimeError("one-step full tree differs from the two-patch reconstruction")
    git(single, "apply", "--reverse", "--check", "--index", str(patch_for_check))
    git(single, "apply", "--reverse", "--index", str(patch_for_check))
    if git(single, "write-tree").decode().strip() != base_tree:
        raise RuntimeError("reverse apply did not recover the exact original Git tree")
    if args.verify_existing:
        if OUTPUT.read_bytes() != patch:
            raise RuntimeError("existing full patch differs from the deterministic reconstruction")
    else:
        with OUTPUT.open("xb") as handle:
            handle.write(patch)
    for path, expected_sha in INPUT_SHA.items():
        if sha(path.read_bytes()) != expected_sha:
            raise RuntimeError("input changed during packaging")
    report = {"utc": datetime.now(timezone.utc).isoformat(), "cpu_only": True,
              "base_commit": BASE, "base_tree": base_tree, "candidate_tree": stacked_tree,
              "reference_git": str(REFERENCE.relative_to(ROOT)),
              "scratch": str(scratch.relative_to(ROOT)),
              "input_patch_sha256": {str(path.relative_to(ROOT)): value for path, value in INPUT_SHA.items()},
              "output": str(OUTPUT.relative_to(ROOT)), "output_sha256": sha(patch),
              "output_bytes": len(patch), "changed_paths": sorted(CHANGED),
              "official_manifest_sha256": sha((OFFICIAL / "manifest.json").read_bytes()),
              "archive_source_dir": REMOTE_SOURCE, "archive_file_checks": comparisons,
              "archive_provenance_only": {"base-revision.txt": {"sha256": metadata,
                  "value": RETAINED, "excluded_from_patch": True}},
              "symlinks": links, "screen_080656_core_checks": screen_checks,
              "one_step_apply_full_tree_equal": True, "reverse_apply_exact_base": True,
              "changed_python_compile": True, "default_and_deltas_unchanged": True,
              "commands": COMMANDS}
    encoded = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode()
    (scratch / "rebuild-manifest.json").write_bytes(encoded)
    if not args.verify_existing:
        with Path(__file__).with_name("rebuild-manifest.json").open("xb") as handle:
            handle.write(encoded)
    print(json.dumps({"scratch": report["scratch"], "output_sha256": sha(patch),
                      "archive_plugin_files_equal": len(comparisons), "symlinks": links,
                      "screen_core_checks": len(screen_checks), "candidate_tree": stacked_tree,
                      "one_step_apply_full_tree_equal": True, "reverse_apply_exact_base": True}, indent=2))


if __name__ == "__main__":
    main()
