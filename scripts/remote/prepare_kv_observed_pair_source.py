#!/usr/bin/env python3
"""给冻结capacity/FULL完整416树附同一6a观察器；新418树仅用于VERIFY0对照。"""
import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

import prepare_innovation_source as owner

EXPECTED_HELPER = "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca"
REFERENCES = {
    "capacity": {
        "control": "20261021T212106Z-kv-capacity-context16k-long-control",
        "base": "kv-capacity-20261021T212106Z",
        "source_manifest": "73e5d880f5a92f528618ffda71677c2b56c4b49ae582258dc0946ff20809a436",
        "innovation_manifest": "5bef5daf33f8d4ed31f4d146106ff2eb23f5a05f317c256f544a07332a6f872d",
        "protocol": "67e4c07566ee3e52f84d6a96a494b8976d858420dadd5f833e66c3291e32fb73",
        "transaction": "616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13",
        "worker": "31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf",
    },
    "full": {
        "control": "20261021T214400Z-kv-full-restore-context16k-long-control",
        "base": "kv-full-restore-20261021T214400Z",
        "source_manifest": "a67c717f5e1f7ab5e2240dc9cd8623c02a91aa2b2958b9ee0bf206c791183829",
        "innovation_manifest": "93375c426c9fb0b4d5abdb869ba94a8fab0a01ce1863ab0e1bd9785f586827fe",
        "protocol": "1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8",
        "transaction": "84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883",
        "worker": "5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477",
    },
}
OBSERVER = "biv150_kv_memory_observer.py"
EXPECTED_OBSERVER = "6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c"
# 原6a允许字典不改；FULL与capacity共享其中791c前缀值。
OBSERVER_PREFIXES = {
    "stable": "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff",
    "capacity": "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8",
}
INPUT_INIT = "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8"
OUTPUT_INIT = "39fb96f474c4bacc79ba4cdc1ae27ce877f9dd654825c792dc8446ac620b08e0"
MANIFEST = "memory-observer-source.json"


def prepare(variant, output, *, root=owner.ROOT):
    if variant not in REFERENCES:
        raise ValueError("只接受capacity/full")
    if output.exists() or output.is_symlink():
        raise FileExistsError("不覆盖任何已有目录")
    if owner.sha(Path(owner.__file__).read_bytes()) != EXPECTED_HELPER:
        raise RuntimeError("source_files辅助身份变化")
    root, output = root.resolve(), output.resolve()
    if output.parent != root / "code":
        raise ValueError("只接受ROOT/code全新直接子目录")
    policy = REFERENCES[variant]
    reference = root / "framework" / policy["control"]
    map_file = reference / "source-sha256.json"
    old_manifest = reference / "plugin-source/innovation-source.json"
    if (owner.sha(map_file.read_bytes()) != policy["source_manifest"]
            or owner.sha(old_manifest.read_bytes()) != policy["innovation_manifest"]):
        raise RuntimeError("固定完整参考manifest身份不符")
    expected_inputs = json.loads(map_file.read_text())
    prior = json.loads(old_manifest.read_text())
    if (len(expected_inputs) != 416
            or expected_inputs.get("innovation-source.json") != policy["innovation_manifest"]
            or expected_inputs.get(owner.INIT) != INPUT_INIT
            or expected_inputs.get(owner.RUNNER) != owner.BASE_HASHES[owner.RUNNER]
            or expected_inputs.get("vllm_fl/worker/worker.py") != "a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24"
            or any(expected_inputs.get(owner.PATCH_DIR + "biv150_kv_" + role + ".py") != policy[role]
                   for role in ("protocol", "transaction", "worker"))
            or {n: h for n, h in expected_inputs.items() if n != "innovation-source.json"}
               != prior["output_sha256_excluding_this_manifest"]):
        raise RuntimeError("只接受已审capacity/FULL完整416树及原三模块")
    base = root / "code" / policy["base"]
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
    if constants["EXPECTED_INIT_PREFIXES"] != OBSERVER_PREFIXES or INPUT_INIT not in OBSERVER_PREFIXES.values():
        raise RuntimeError("观察器允许的原init身份变化")
    original = (base / owner.INIT).read_bytes()
    changed = original + constants["INIT_FOOTER"]
    if owner.sha(original) != INPUT_INIT or owner.sha(changed) != OUTPUT_INIT:
        raise RuntimeError("必须完整原init/footer之后精确append")
    compile(raw, OBSERVER, "exec")
    compile(changed, owner.INIT, "exec")
    expected = {**inputs, owner.INIT: OUTPUT_INIT, owner.PATCH_DIR + OBSERVER: EXPECTED_OBSERVER}
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
            "kind": "common-memory-observer-capacity-full-VERIFY0-pair",
            "created_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
            "base_source": str(base), "output": str(output), "input_sha256": inputs,
            "observer_sha256": EXPECTED_OBSERVER, "preparer_sha256": owner.sha(Path(__file__).read_bytes()),
            "source_helper_sha256": EXPECTED_HELPER, "reference_source_manifest_sha256": policy["source_manifest"],
            "reference_innovation_manifest_sha256": policy["innovation_manifest"],
            "original_innovation_manifest_preserved_sha256": inputs.get("innovation-source.json"),
            "output_sha256_excluding_this_manifest": actual,
            "changes": {name: {"before": inputs.get(name), "after": value}
                        for name, value in actual.items() if inputs.get(name) != value},
            "limits": ["双方同一6a启动观察，原innovation-source/各自三模块字节不改。", "源码guard a8de/e155与协议原字节不变。",
                       "原bc51 context-long/VERIFY0短测；实际观察与各自传输链须后验，不是官方成绩或独立ZERO计时。"]}
    except BaseException as error:
        (output / MANIFEST).write_text(json.dumps({"status": "failed_preparation", "error": repr(error)}) + "\n")
        raise
    (output / MANIFEST).write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=REFERENCES, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.variant, args.output)
    print(json.dumps({"status": result["status"], "output": result["output"], "variant": result["variant"]}))
