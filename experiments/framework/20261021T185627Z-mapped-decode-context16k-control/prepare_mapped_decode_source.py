#!/usr/bin/env python3
"""纯CPU制作独立mapped服务副本；不导入模型，不触碰installed或基线。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

import prepare_innovation_source as owner

EXPECTED_HELPER = "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca"
EXPECTED_RUNNER_OUTPUT = "3566099b2f336f3e7ae768adeca5b0da169748324fec26fc00b150b26b246a73"
ASSETS = {
    "biv150_mapped_decode.py": "d085ad6dcc0fd5dc26188d3e0f5801b8e394dc07a79c05a376192ec9e1e95b4b",
    "biv150_mapped_decode_source.py": "919e80abf5b95c55ea63aa8619fa3202cd78b0c4cc0e303df7b4197bf1898316",
    "biv150_mapped_attention.py": "72713a90584bc6567706fb881188afa04335230afc13e021c10f862f88d054a1",
    # Gate is evidence only; it is not installed in the serving package.
    "validate_mapped_decode.py": "ede4519424d467bb4f47f52cb57429c5e489ee2324070c482225cc0499b0dc2f",
}
CORE = {
    "vllm_fl/patches/biv150_runtime.py": "a0c09c51826e0b9e0e5c4f320e68451359db44001d56fd68e1e78de8dda2c9b4",
    "vllm_fl/patches/biv150_top_p_triton.py": "da77c411a88ad4ead072c99cdc4edb52b5bef5b8e5990b9cc8e04db08ed31ca9",
}
PACKAGED = tuple(name for name in ASSETS if name != "validate_mapped_decode.py")


def prepare(base, output, assets, *, root=owner.ROOT):
    if output.exists() or output.is_symlink():
        raise FileExistsError("输出必须全新，不能覆盖或叠加候选")
    if owner.sha(Path(owner.__file__).read_bytes()) != EXPECTED_HELPER:
        raise RuntimeError("未经审阅的source_files辅助脚本")
    root, base, output, assets = root.resolve(), base.resolve(), output.resolve(), assets.resolve()
    if (base.parent != root / "code" or base.name != owner.BASE_NAME or not base.is_dir()
            or output.parent != root / "code" or output == base
            or assets != root / "scripts" or not assets.is_dir()):
        raise ValueError("仅接受ROOT/code原080656、全新直接code子目录、ROOT/scripts素材")
    inputs = owner.source_files(base)
    required = {**owner.BASE_HASHES, **CORE}
    if "innovation-source.json" in inputs:
        raise RuntimeError("基线已含候选manifest，拒绝叠加")
    expected_biv = {relative for relative in required if relative.startswith(owner.PATCH_DIR)}
    actual_biv = {relative for relative in inputs if relative.startswith(owner.PATCH_DIR)
                  and Path(relative).name.startswith("biv150") and relative.endswith(".py")}
    if actual_biv != expected_biv:
        raise RuntimeError("基线BIV模块集合不符，可能叠加了其它候选")
    for relative, expected in required.items():
        if inputs.get(relative) != expected:
            raise RuntimeError("基线核心源码身份不符：" + relative)
    raw = {}
    for name, expected in ASSETS.items():
        path = assets / name
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("素材须为普通文件：" + name)
        raw[name] = path.read_bytes()
        if owner.sha(raw[name]) != expected:
            raise RuntimeError("候选素材SHA不符：" + name)
        compile(raw[name], "isolated:" + name, "exec")
    namespace = {}
    # Exact pinned transformer uses hashlib only. Never execute candidate
    # runtime, derived JIT or gate imports while packaging.
    tool = "biv150_mapped_decode_source.py"
    exec(compile(raw[tool], tool, "exec"), namespace)
    changed = namespace["transform_runner"]((base / owner.RUNNER).read_bytes())
    if owner.sha(changed) != EXPECTED_RUNNER_OUTPUT:
        raise RuntimeError("runner不是已审精确追加产物")
    compile(changed, "isolated:" + owner.RUNNER, "exec")
    expected = dict(inputs)
    expected[owner.RUNNER] = owner.sha(changed)
    for name in PACKAGED:
        target = owner.PATCH_DIR + name
        if target in inputs:
            raise RuntimeError("基线已含mapped模块")
        expected[target] = owner.sha(raw[name])
    aliases = {path.relative_to(base).as_posix(): {
        "link_target": str(path.readlink()),
        "resolved_file": path.resolve().relative_to(base).as_posix(),
        "sha256": inputs[path.relative_to(base).as_posix()],
    } for path in base.rglob("*") if path.is_symlink()
        and "__pycache__" not in path.relative_to(base).parts and path.suffix not in (".pyc", ".pyo")}
    shutil.copytree(base, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    try:
        if owner.source_files(output) != inputs:
            raise RuntimeError("复制期间基线变化或拷贝字节不符")
        (output / owner.RUNNER).write_bytes(changed)
        for name in PACKAGED:
            (output / owner.PATCH_DIR / name).write_bytes(raw[name])
        actual = owner.source_files(output)
        if actual != expected:
            raise RuntimeError("出现额外源码变化；保留新目录供诊断")
        manifest = {
            "status": "prepared_not_executed", "variant": "mapped-decode-only-on-sql-c3",
            "created_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
            "base_source": str(base), "output": str(output),
            "preparer_sha256": owner.sha(Path(__file__).read_bytes()),
            "source_helper_sha256": EXPECTED_HELPER, "base_required_sha256": required,
            "input_sha256": inputs, "input_file_aliases_dereferenced": aliases,
            "asset_sha256": ASSETS, "gate_is_evidence_only_not_packaged": True,
            "changes": {relative: {"before": inputs.get(relative), "after": value}
                        for relative, value in actual.items() if inputs.get(relative) != value},
            "output_sha256_excluding_this_manifest": actual,
            "validation": "stdlib compile/full copy SHA only; no runtime/JIT/framework/model import or installed writes",
            "limits": ["单层正确门不等整模型accuracy。", "服务需真实FIRST_SELECTED real_execute=1，startup不等命中。",
                       "只含mapped；不叠CPUmetadata/async/CTA/prefix/growth/bucket/gather。"]}
        (output / "innovation-source.json").write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    except BaseException as error:
        (output / "innovation-source.json").write_text(json.dumps({
            "status": "failed_preparation", "created_utc": datetime.now(timezone.utc).isoformat(),
            "base_source": str(base), "output": str(output), "error": repr(error)}, indent=2) + "\n", encoding="utf-8")
        raise
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--asset-dir", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.base_source, args.output, args.asset_dir)
    print(json.dumps({"status": result["status"], "output": result["output"], "changes": result["changes"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
