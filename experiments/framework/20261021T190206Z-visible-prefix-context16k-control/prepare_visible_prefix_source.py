#!/usr/bin/env python3
"""纯 CPU 制作隔离 prefix-mask 服务副本；不导入 Torch 或改原目录。"""
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
ASSETS = {
    "biv150_prefill_visible_prefix.py": "87c6a31075939c551402d7007b491546a215584a58ec82caddc08fc7249998d6",
    "biv150_visible_prefix_service.py": "7258ad7929ad22676201fec045184f0038be4689f2eef3a51b21e30c658029da",
    "biv150_visible_prefix_service_source.py": "464b9ea73f6961097c1cde2c92d97bdf9ed50909e9da1ecbb65f1dd437bccaba",
}


def prepare(base, output, assets, *, root=owner.ROOT):
    if output.exists() or output.is_symlink():
        raise FileExistsError("输出目录必须全新")
    if hashlib.sha256(Path(owner.__file__).read_bytes()).hexdigest() != EXPECTED_HELPER:
        raise RuntimeError("未经审阅的source_files辅助脚本")
    root, base, output, assets = root.resolve(), base.resolve(), output.resolve(), assets.resolve()
    if (base.parent != root / "code" or base.name != owner.BASE_NAME
            or output.parent != root / "code" or output == base or assets != root / "scripts"
            or output.exists() or output.is_symlink()):
        raise ValueError("要求原080656 base、全新直接code子目录和scripts素材目录")
    inputs = owner.source_files(base)
    if "innovation-source.json" in inputs:
        raise RuntimeError("不接受叠加其它候选的base")
    for relative, expected in owner.BASE_HASHES.items():
        if inputs.get(relative) != expected:
            raise RuntimeError("base identity不符：" + relative)
    raw = {}
    for name, expected in ASSETS.items():
        path = assets / name
        if path.is_symlink() or not path.is_file() or owner.sha(path.read_bytes()) != expected:
            raise RuntimeError("未经审阅的素材：" + name)
        raw[name] = path.read_bytes()
    namespace = {}
    tool = "biv150_visible_prefix_service_source.py"
    exec(compile(raw[tool], tool, "exec"), namespace)
    changed = namespace["transform_source"]((base / owner.RUNNER).read_bytes())
    outputs = dict(inputs)
    outputs[owner.RUNNER] = owner.sha(changed)
    additions = [name for name in ASSETS if name != tool]
    for name in additions:
        target = owner.PATCH_DIR + name
        if target in inputs:
            raise RuntimeError("base已有prefix模块")
        outputs[target] = owner.sha(raw[name])
        compile(raw[name], target, "exec")
    compile(changed, owner.RUNNER, "exec")
    shutil.copytree(base, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    if owner.source_files(output) != inputs:
        raise RuntimeError("base复制字节不一致；保留新目录供诊断")
    (output / owner.RUNNER).write_bytes(changed)
    for name in additions:
        (output / owner.PATCH_DIR / name).write_bytes(raw[name])
    if owner.source_files(output) != outputs:
        raise RuntimeError("出现额外源码变化；保留新目录供诊断")
    manifest = {
        "status": "prepared_not_executed", "variant": "visible-prefix-only",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "base_source": str(base), "output": str(output), "command": [sys.executable, *sys.argv],
        "preparer_sha256": owner.sha(Path(__file__).read_bytes()),
        "source_helper_sha256": owner.sha(Path(owner.__file__).read_bytes()),
        "input_sha256": inputs, "asset_sha256": ASSETS,
        "output_sha256_excluding_this_manifest": outputs,
        "changes": {relative: {"before": inputs.get(relative), "after": value}
                    for relative, value in outputs.items() if inputs.get(relative) != value},
        "validation": "stdlib byte/compile/copy only; no runtime, accelerator, model, performance or accuracy"}
    (output / "innovation-source.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--asset-dir", required=True, type=Path)
    args = parser.parse_args()
    result = prepare(args.base_source, args.output, args.asset_dir)
    print(json.dumps({"status": result["status"], "output": result["output"], "changes": result["changes"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
