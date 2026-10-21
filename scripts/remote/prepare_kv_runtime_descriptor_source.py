#!/usr/bin/env python3
"""纯CPU包装KV元信息观察器；全新080656副本，仅改init并加一个模块。"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

import prepare_innovation_source as owner

EXPECTED_HELPER = "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca"
ASSET = "biv150_kv_runtime_descriptor.py"
EXPECTED_ASSET = "0c892ad02fbfe663d3f7c8f668cdd000c0c1fc7860ff915db8bce5949cae0667"
EXPECTED_INIT_OUTPUT = "90fe0b381fd53ec5273c623d91b806a0fc21f5b84165beba0b015a1e07d53e74"
CORE = {
    "vllm_fl/worker/worker.py": "a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24",
    "vllm_fl/patches/biv150_runtime.py": "a0c09c51826e0b9e0e5c4f320e68451359db44001d56fd68e1e78de8dda2c9b4",
    "vllm_fl/patches/biv150_top_p_triton.py": "da77c411a88ad4ead072c99cdc4edb52b5bef5b8e5990b9cc8e04db08ed31ca9",
}


def prepare(base, output, assets, *, root=owner.ROOT):
    if output.exists() or output.is_symlink():
        raise FileExistsError("输出须为全新目录，不覆盖/叠加候选")
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
        raise RuntimeError("基线已含候选manifest")
    expected_biv = {name for name in required if name.startswith(owner.PATCH_DIR)}
    actual_biv = {name for name in inputs if name.startswith(owner.PATCH_DIR)
                  and Path(name).name.startswith("biv150") and name.endswith(".py")}
    if expected_biv != actual_biv:
        raise RuntimeError("基线BIV模块集合不符，拒叠加其它候选")
    for name, expected in required.items():
        if inputs.get(name) != expected:
            raise RuntimeError("基线源码身份不符：" + name)
    path = assets / ASSET
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("观察器素材须为普通文件")
    raw = path.read_bytes()
    if owner.sha(raw) != EXPECTED_ASSET:
        raise RuntimeError("观察器素材SHA不符")
    compile(raw, "isolated:" + ASSET, "exec")
    # Read two literal assignments, without executing any candidate imports.
    constants = {node.targets[0].id: ast.literal_eval(node.value)
                 for node in ast.parse(raw).body if isinstance(node, ast.Assign)
                 and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id in ("EXPECTED_INIT", "INIT_FOOTER")}
    original = (base / owner.INIT).read_bytes()
    if constants["EXPECTED_INIT"] != inputs[owner.INIT] or owner.sha(original) != inputs[owner.INIT]:
        raise RuntimeError("init读取期间变化或transform常量不符")
    changed = original + constants["INIT_FOOTER"]
    if owner.sha(changed) != EXPECTED_INIT_OUTPUT:
        raise RuntimeError("init不是已审精确append产物")
    compile(changed, "isolated:" + owner.INIT, "exec")
    target = owner.PATCH_DIR + ASSET
    expected = {**inputs, owner.INIT: owner.sha(changed), target: EXPECTED_ASSET}
    aliases = {p.relative_to(base).as_posix(): {
        "link_target": str(p.readlink()), "resolved_file": p.resolve().relative_to(base).as_posix(),
        "sha256": inputs[p.relative_to(base).as_posix()]}
        for p in base.rglob("*") if p.is_symlink() and "__pycache__" not in p.relative_to(base).parts
        and p.suffix not in (".pyc", ".pyo")}
    shutil.copytree(base, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    try:
        if owner.source_files(output) != inputs:
            raise RuntimeError("复制期间基线变化或字节不符")
        (output / owner.INIT).write_bytes(changed)
        (output / target).write_bytes(raw)
        actual = owner.source_files(output)
        if actual != expected:
            raise RuntimeError("出现额外源码变化")
        manifest = {
            "status": "prepared_not_executed", "variant": "kv-runtime-descriptor-only-on-sql-c3",
            "created_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
            "base_source": str(base), "output": str(output),
            "preparer_sha256": owner.sha(Path(__file__).read_bytes()),
            "source_helper_sha256": EXPECTED_HELPER, "base_required_sha256": required,
            "input_sha256": inputs, "input_file_aliases_dereferenced": aliases,
            "asset_sha256": {ASSET: EXPECTED_ASSET},
            "changes": {name: {"before": inputs.get(name), "after": value}
                        for name, value in actual.items() if inputs.get(name) != value},
            "output_sha256_excluding_this_manifest": actual,
            "validation": "stdlib AST/compile/full-copy SHA only; never execute runtime/framework/model imports",
            "required_environment": {"BIV150_KV_DESCRIPTOR_DIR": "unique ROOT/framework/<run>/kv-descriptors"},
            "limits": ["默认install关闭；新隔离init才显式启用。", "INSTALLED不等观察完成。",
                       "smoke后须核42层完整worker-kv与core-objects JSON；缺项/错误不得当布局证据。",
                       "不含save/restore协议，不是性能/accuracy门；不叠其它候选。"],
        }
        (output / "innovation-source.json").write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    except BaseException as error:
        (output / "innovation-source.json").write_text(json.dumps({
            "status": "failed_preparation", "base_source": str(base), "output": str(output),
            "created_utc": datetime.now(timezone.utc).isoformat(), "error": repr(error)}, indent=2) + "\n", encoding="utf-8")
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
