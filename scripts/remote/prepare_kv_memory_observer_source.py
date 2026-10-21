#!/usr/bin/env python3
"""给冻结stable/capacity原init完整尾部附同一观察器；仅新目录、无框架导入。"""
import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

import prepare_innovation_source as owner

EXPECTED_HELPER = "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca"
REFERENCE_NAME = "20261021T212106Z-kv-capacity-context16k-long-control"
EXPECTED_REFERENCE = "73e5d880f5a92f528618ffda71677c2b56c4b49ae582258dc0946ff20809a436"
EXPECTED_CAPACITY_MANIFEST = "5bef5daf33f8d4ed31f4d146106ff2eb23f5a05f317c256f544a07332a6f872d"
OBSERVER = "biv150_kv_memory_observer.py"
EXPECTED_OBSERVER = "6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c"
INPUT_INIT = {
    "stable": "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff",
    "capacity": "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8",
}
OUTPUT_INIT = {
    "stable": "00e8def05ec16d3dcc01bcfe47c976dd4954402984b0a9ba1162d4b72547c3f4",
    "capacity": "39fb96f474c4bacc79ba4cdc1ae27ce877f9dd654825c792dc8446ac620b08e0",
}
MANIFEST = "memory-observer-source.json"


def prepare(variant, output, *, root=owner.ROOT):
    if variant not in INPUT_INIT:
        raise ValueError("只接受stable/capacity")
    if output.exists() or output.is_symlink():
        raise FileExistsError("不覆盖任何已有目录")
    if owner.sha(Path(owner.__file__).read_bytes()) != EXPECTED_HELPER:
        raise RuntimeError("source_files辅助身份变化")
    root, output = root.resolve(), output.resolve()
    if output.parent != root / "code":
        raise ValueError("只接受ROOT/code全新直接子目录")
    reference = root / "framework" / REFERENCE_NAME
    map_file = reference / "source-sha256.json"
    old_manifest = reference / "plugin-source/innovation-source.json"
    if (owner.sha(map_file.read_bytes()) != EXPECTED_REFERENCE
            or owner.sha(old_manifest.read_bytes()) != EXPECTED_CAPACITY_MANIFEST):
        raise RuntimeError("212106完整参考manifest身份不符")
    capacity = json.loads(map_file.read_text())
    prior = json.loads(old_manifest.read_text())
    stable = prior["input_sha256"]
    if (len(stable) != 410 or len(capacity) != 416
            or capacity["innovation-source.json"] != EXPECTED_CAPACITY_MANIFEST
            or any(stable.get(k) != v for k, v in owner.BASE_HASHES.items())):
        raise RuntimeError("原410/416完整输入身份不符")
    expected_inputs = stable if variant == "stable" else capacity
    base_name = owner.BASE_NAME if variant == "stable" else "kv-capacity-20261021T212106Z"
    base = root / "code" / base_name
    if not base.is_dir() or base.resolve().parent != root / "code" or output == base.resolve():
        raise ValueError("原树必须是ROOT/code冻结目录")
    inputs = owner.source_files(base)
    if inputs != expected_inputs or MANIFEST in inputs or owner.PATCH_DIR + OBSERVER in inputs:
        raise RuntimeError("完整原树变化或已附观察器")
    asset = root / "scripts" / OBSERVER
    if asset.is_symlink() or not asset.is_file():
        raise RuntimeError("观察器素材须普通文件")
    raw = asset.read_bytes()
    if owner.sha(raw) != EXPECTED_OBSERVER:
        raise RuntimeError("观察器不是最终6a772a")
    constants = {node.targets[0].id: ast.literal_eval(node.value)
                 for node in ast.parse(raw).body
                 if isinstance(node, ast.Assign) and len(node.targets) == 1
                 and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id in ("INIT_FOOTER", "EXPECTED_INIT_PREFIXES")}
    if constants["EXPECTED_INIT_PREFIXES"] != INPUT_INIT:
        raise RuntimeError("观察器允许的原init身份变化")
    original = (base / owner.INIT).read_bytes()
    changed = original + constants["INIT_FOOTER"]
    if owner.sha(original) != INPUT_INIT[variant] or owner.sha(changed) != OUTPUT_INIT[variant]:
        raise RuntimeError("必须完整原init/footer之后精确append")
    compile(raw, OBSERVER, "exec")
    compile(changed, owner.INIT, "exec")
    expected = {**inputs, owner.INIT: OUTPUT_INIT[variant], owner.PATCH_DIR + OBSERVER: EXPECTED_OBSERVER}
    shutil.copytree(base, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    try:
        if owner.source_files(output) != inputs or owner.source_files(base) != inputs:
            raise RuntimeError("复制期间原树变化/复制字节不符")
        (output / owner.INIT).write_bytes(changed)
        (output / owner.PATCH_DIR / OBSERVER).write_bytes(raw)
        actual = owner.source_files(output)
        if actual != expected:
            raise RuntimeError("除init append/新观察器外出现变化")
        result = {"status": "prepared_not_executed", "variant": variant,
            "created_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
            "base_source": str(base), "output": str(output), "input_sha256": inputs,
            "observer_sha256": EXPECTED_OBSERVER, "preparer_sha256": owner.sha(Path(__file__).read_bytes()),
            "source_helper_sha256": EXPECTED_HELPER, "reference_source_manifest_sha256": EXPECTED_REFERENCE,
            "reference_innovation_manifest_sha256": EXPECTED_CAPACITY_MANIFEST,
            "original_innovation_manifest_preserved_sha256": inputs.get("innovation-source.json"),
            "output_sha256_excluding_this_manifest": actual,
            "changes": {name: {"before": inputs.get(name), "after": value}
                        for name, value in actual.items() if inputs.get(name) != value},
            "limits": ["仅启动标量观察，原innovation-source字节不改。", "源码guard a8de/e155与协议原字节不变。",
                       "原bc51 smoke-only/VERIFY0，非性能或官方成绩；安装/ARM不证明实际观察。"]}
    except BaseException as error:
        (output / MANIFEST).write_text(json.dumps({"status": "failed_preparation", "error": repr(error)}) + "\n")
        raise
    (output / MANIFEST).write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=INPUT_INIT, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.variant, args.output)
    print(json.dumps({"status": result["status"], "output": result["output"], "variant": result["variant"]}))
