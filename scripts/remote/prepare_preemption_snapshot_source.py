#!/usr/bin/env python3
"""从固定080656完整410树包装只观察抢占诊断413树；不执行框架/设备。"""
import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

import prepare_innovation_source as owner

EXPECTED_HELPER = "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca"
REFERENCE = "20261021T212106Z-kv-capacity-context16k-long-control"
REFERENCE_SOURCE = "73e5d880f5a92f528618ffda71677c2b56c4b49ae582258dc0946ff20809a436"
REFERENCE_MANIFEST = "5bef5daf33f8d4ed31f4d146106ff2eb23f5a05f317c256f544a07332a6f872d"
ASSETS = {
    "biv150_preemption_snapshot.py": "c6b3baa96db494e7c22d8c7a3f02980d06d3469c491bf850e9ebac77675204f6",
    "biv150_kv_completion_probe.py": "a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6",
}
INIT_OUTPUT = "01c42c6938efb61476669b9bdb76207e79d20d7e19ac4d0165e617649d2a85dd"
MANIFEST = "preemption-snapshot-source.json"


def prepare(output, *, root=owner.ROOT):
    if output.exists() or output.is_symlink():
        raise FileExistsError("输出必须全新，不覆盖或叠候选")
    if owner.sha(Path(owner.__file__).read_bytes()) != EXPECTED_HELPER:
        raise RuntimeError("完整source helper身份变化")
    root, output = root.resolve(), output.resolve()
    if output.parent != root / "code":
        raise ValueError("只接受ROOT/code新直接子目录")
    ref = root / "framework" / REFERENCE
    if (owner.sha((ref / "source-sha256.json").read_bytes()) != REFERENCE_SOURCE
            or owner.sha((ref / "plugin-source/innovation-source.json").read_bytes()) != REFERENCE_MANIFEST):
        raise RuntimeError("固定参考manifest变化")
    expected_inputs = json.loads((ref / "plugin-source/innovation-source.json").read_text())["input_sha256"]
    if len(expected_inputs) != 410 or any(expected_inputs.get(n) != h for n, h in owner.BASE_HASHES.items()):
        raise RuntimeError("非原080656完整410输入")
    base = root / "code" / owner.BASE_NAME
    if not base.is_dir() or base.resolve().parent != root / "code" or output == base.resolve():
        raise ValueError("原树路径不符")
    inputs = owner.source_files(base)
    if (inputs != expected_inputs or MANIFEST in inputs or "innovation-source.json" in inputs
            or any(owner.PATCH_DIR + name in inputs for name in ASSETS)):
        raise RuntimeError("原树变化或已叠后造scope/observer")
    raw_assets = {}
    for name, expected in ASSETS.items():
        path = root / "scripts" / name
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("素材必须是普通文件：" + name)
        raw = path.read_bytes()
        if owner.sha(raw) != expected:
            raise RuntimeError("未审素材：" + name)
        compile(raw, "isolated:" + name, "exec")
        raw_assets[name] = raw
    constants = {n.targets[0].id: ast.literal_eval(n.value)
                 for n in ast.parse(raw_assets["biv150_preemption_snapshot.py"]).body
                 if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                 and n.targets[0].id in ("EXPECTED_INIT", "INIT_FOOTER")}
    original = (base / owner.INIT).read_bytes()
    changed = original + constants["INIT_FOOTER"]
    if constants["EXPECTED_INIT"] != inputs[owner.INIT] or owner.sha(original) != inputs[owner.INIT] or owner.sha(changed) != INIT_OUTPUT:
        raise RuntimeError("必须原e043完整末尾append")
    compile(changed, "isolated:" + owner.INIT, "exec")
    expected = {**inputs, owner.INIT: INIT_OUTPUT, **{owner.PATCH_DIR + n: h for n, h in ASSETS.items()}}
    aliases = {p.relative_to(base).as_posix(): {"link_target": str(p.readlink()),
               "resolved_file": p.resolve().relative_to(base).as_posix(), "sha256": inputs[p.relative_to(base).as_posix()]}
               for p in base.rglob("*") if p.is_symlink() and "__pycache__" not in p.relative_to(base).parts
               and p.suffix not in (".pyc", ".pyo")}
    shutil.copytree(base, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    try:
        if owner.source_files(output) != inputs or owner.source_files(base) != inputs:
            raise RuntimeError("复制期间输入变化或字节不符")
        (output / owner.INIT).write_bytes(changed)
        for name, raw in raw_assets.items():
            (output / owner.PATCH_DIR / name).write_bytes(raw)
        actual = owner.source_files(output)
        if actual != expected:
            raise RuntimeError("init和两个新module之外发生变化")
        result = {"status": "prepared_not_executed", "kind": "first-running-allocation-failure-cpu-snapshot-only",
            "created_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
            "base_source": str(base), "output": str(output), "input_sha256": inputs,
            "preparer_sha256": owner.sha(Path(__file__).read_bytes()), "source_helper_sha256": EXPECTED_HELPER,
            "reference_source_manifest_sha256": REFERENCE_SOURCE, "reference_innovation_manifest_sha256": REFERENCE_MANIFEST,
            "asset_sha256": ASSETS, "input_file_aliases_dereferenced": aliases,
            "output_sha256_excluding_this_manifest": actual,
            "changes": {n: {"before": inputs.get(n), "after": v} for n, v in actual.items() if inputs.get(n) != v},
            "limits": ["只观察、无victim策略，不叠capacity/FULL/6a。", "a4de仅用资格函数，不install旧probe。",
                       "INSTALLED不是完整snapshot；需FIRST_RUNNING_FAILURE completeTrue及原pop/原输出/后态实际原件。",
                       "一次CPU页遍历/stdout有诊断扰动，非性能对照或模型accuracy。"]}
    except BaseException as error:
        (output / MANIFEST).write_text(json.dumps({"status": "failed_preparation", "error": repr(error)}) + "\n")
        raise
    (output / MANIFEST).write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.output)
    print(json.dumps({"status": result["status"], "output": result["output"]}))
