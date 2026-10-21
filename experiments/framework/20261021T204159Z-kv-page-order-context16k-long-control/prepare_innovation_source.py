#!/usr/bin/env python3
"""Create one new, byte-audited innovation source copy; never run an accelerator.

The CLI only accepts the frozen 080656 source and direct children of ROOT/code.
All candidate assets are pinned. Existing output directories are never reused.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shutil
import sys
import json


ROOT = Path("/workspace/experiments/minicpm-s2")
BASE_NAME = "sql-mixed-20261021T080656Z"
RUNNER = "vllm_fl/worker/model_runner.py"
INIT = "vllm_fl/__init__.py"
PATCH_DIR = "vllm_fl/patches/"
BASE_HASHES = {
    RUNNER: "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1",
    INIT: "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff",
    PATCH_DIR + "biv150_sql_reflection.py": "ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e",
    PATCH_DIR + "biv150_decode_launch_runtime.py": "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f",
    PATCH_DIR + "biv150_mixed_decode.py": "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42",
}
VARIANTS = {
    "bucket": {
        "runtime": "biv150_mixed_token_bucket.py",
        "tool": "mixed_token_bucket_footer.py", "target": RUNNER,
        "runtime_sha256": "d2620ff750beb3fab97f372d64a1ec0e5550ee133cc6ca33adb8ba3f43de4605",
        "tool_sha256": "21074c950f7ebfec73215f8db746f13b6980779277b084cec6c79e27b706e620",
    },
    "growth": {
        "runtime": "biv150_growth_admission.py",
        "tool": "biv150_growth_admission_source.py", "target": INIT,
        "runtime_sha256": "9245dd089a310620840a1c056544e66fb2dd0ea24f41ef8f0e4b22721bac7e49",
        "tool_sha256": "b0d5516684e4092dd643836c7bf43ffcd3681d855a32033d6745f13fda0cb709",
    },
    "hidden-gather": {
        "runtime": "biv150_hidden_row_gather.py",
        "tool": "biv150_hidden_row_gather_source.py", "target": RUNNER,
        "runtime_sha256": "109905b3d276d6e4ff6cc74a7b97dfe6e8ee31a517b0ac7c4fdb163cc37ad8fd",
        "tool_sha256": "881f2cf209da11842577aab01cca3830e985ad7c9030554156757a5de7e791f2",
    },
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_files(directory):
    """Match ignored caches; dereference internal file aliases only."""
    result = {}
    for path in directory.rglob("*"):
        relative = path.relative_to(directory)
        if "__pycache__" in relative.parts or path.suffix in (".pyc", ".pyo"):
            continue
        if path.is_symlink():
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(directory.resolve()) or not resolved.is_file():
                raise RuntimeError("source alias must resolve to an internal regular file: " + str(relative))
            result[relative.as_posix()] = sha(resolved.read_bytes())
            continue
        if path.is_file():
            result[relative.as_posix()] = sha(path.read_bytes())
    return dict(sorted(result.items()))


def prepare(base_source, output, asset_dir, variant, *, root=ROOT):
    """Filesystem-only seam; root override is for local packaging verification."""
    root = root.resolve()
    code = root / "code"
    if output.exists() or output.is_symlink():
        raise FileExistsError("output must be a completely new directory: " + str(output))
    base, target, assets = base_source.resolve(), output.resolve(), asset_dir.resolve()
    if (base.parent != code or base.name != BASE_NAME or not base.is_dir()
            or target.parent != code or target == base
            or assets != root / "scripts" or not assets.is_dir()):
        raise ValueError("require frozen 080656 ROOT/code base, new direct ROOT/code output, and ROOT/scripts assets")
    if variant not in VARIANTS:
        raise ValueError("unsupported variant: " + variant)
    inputs = source_files(base)
    for relative, expected in BASE_HASHES.items():
        if inputs.get(relative) != expected:
            raise RuntimeError("unaudited frozen source: " + relative)
    if "innovation-source.json" in inputs:
        raise RuntimeError("base already contains an innovation-source manifest")
    policy = VARIANTS[variant]
    raw_assets = {}
    for role in ("runtime", "tool"):
        path = assets / policy[role]
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("missing or symlinked candidate asset: " + str(path))
        raw = path.read_bytes()
        if sha(raw) != policy[role + "_sha256"]:
            raise RuntimeError("unaudited candidate asset: " + path.name)
        raw_assets[role] = raw
    runtime_target = PATCH_DIR + policy["runtime"]
    if runtime_target in inputs:
        raise RuntimeError("base already contains this candidate module")
    original = (base / policy["target"]).read_bytes()
    if sha(original) != inputs[policy["target"]]:
        raise RuntimeError("base source seam changed during preparation")
    if variant == "bucket":
        changed = original + raw_assets["tool"]
    else:
        # Both fixed-byte transformers import hashlib only; never import vLLM
        # or candidate runtimes (which can initialize the accelerator stack).
        namespace = {}
        exec(compile(raw_assets["tool"], policy["tool"], "exec"), namespace)
        changed = namespace["transform_source"](original)
    if changed == original:
        raise RuntimeError("candidate did not change its intended source seam")
    compile(changed, "isolated:" + policy["target"], "exec")
    compile(raw_assets["runtime"], "isolated:" + runtime_target, "exec")
    expected_outputs = dict(inputs)
    expected_outputs[policy["target"]] = sha(changed)
    expected_outputs[runtime_target] = sha(raw_assets["runtime"])
    # copytree creates exclusively. All checks and transformations above are
    # read-only; no failed preflight can leave a partial candidate directory.
    shutil.copytree(base, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    try:
        if source_files(target) != inputs:
            raise RuntimeError("base changed during copy or copied bytes differ")
        (target / policy["target"]).write_bytes(changed)
        (target / runtime_target).write_bytes(raw_assets["runtime"])
        outputs = source_files(target)
        if outputs != expected_outputs:
            raise RuntimeError("unintended file addition/removal/change in isolated source")
        manifest = {
            "created_utc": datetime.now(timezone.utc).isoformat(), "status": "prepared_not_executed",
            "variant": variant, "base_source": str(base), "output": str(target),
            "asset_dir": str(assets), "preparer_sha256": sha(Path(__file__).read_bytes()),
            "input_file_aliases_dereferenced": {
                p.relative_to(base).as_posix(): {
                    "link_target": str(p.readlink()),
                    "resolved_file": p.resolve().relative_to(base).as_posix(),
                    "sha256": inputs[p.relative_to(base).as_posix()],
                } for p in base.rglob("*") if p.is_symlink()
                and "__pycache__" not in p.relative_to(base).parts
                and p.suffix not in (".pyc", ".pyo")},
            "command": [sys.executable, *sys.argv],
            "base_required_sha256": dict(BASE_HASHES), "input_sha256": inputs,
            "asset_sha256": {policy[role]: sha(raw_assets[role]) for role in ("runtime", "tool")},
            "changes": {relative: {"before": inputs.get(relative), "after": outputs[relative]}
                        for relative in (policy["target"], runtime_target)},
            "output_sha256_excluding_this_manifest": outputs,
            "validation": "compile and full copied-file hash comparison only; no candidate-runtime/vLLM imports, GPU, accuracy, or performance run",
        }
        (target / "innovation-source.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    except BaseException as error:
        # Preserve a partially prepared new directory for diagnosis; never
        # recursively remove/move it or silently reuse it on a later command.
        (target / "innovation-source.json").write_text(json.dumps({
            "status": "failed_preparation", "variant": variant,
            "created_utc": datetime.now(timezone.utc).isoformat(), "error": repr(error),
            "base_source": str(base), "output": str(target)}, indent=2) + "\n", encoding="utf-8")
        raise
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--asset-dir", type=Path, required=True)
    parser.add_argument("--variant", choices=tuple(VARIANTS), required=True)
    args = parser.parse_args()
    result = prepare(args.base_source, args.output, args.asset_dir, args.variant)
    print(json.dumps({"status": result["status"], "variant": result["variant"],
                      "output": result["output"], "changes": result["changes"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
