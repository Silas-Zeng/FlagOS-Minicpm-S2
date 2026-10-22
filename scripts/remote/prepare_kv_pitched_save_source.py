#!/usr/bin/env python3
"""给冻结214400 FULL416树仅替换SAVE worker并附已验桥，输出420项；不导入框架。"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

import prepare_innovation_source as owner

EXPECTED_HELPER = "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca"
REFERENCE = {
    "control": "20261021T214400Z-kv-full-restore-context16k-long-control",
    "base": "kv-full-restore-20261021T214400Z",
    "source_manifest": "a67c717f5e1f7ab5e2240dc9cd8623c02a91aa2b2958b9ee0bf206c791183829",
    "innovation_manifest": "93375c426c9fb0b4d5abdb869ba94a8fab0a01ce1863ab0e1bd9785f586827fe",
    "protocol": "1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8",
    "transaction": "84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883",
    "worker": "5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477",
}
INIT = "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8"
ASSETS = {
    "vllm_fl/patches/biv150_kv_worker.py": ("biv150_kv_pitched_save_worker.py", "a662e478d20884c5b1d65e0ee3d270a62453d88166b28e092dcaf3b35a3df854"),
    "vllm_fl/patches/biv150_kv_pitched_copy.py": ("biv150_kv_pitched_copy.py", "818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd"),
    "vllm_fl/patches/biv150_kv_pitched_bridge.cpp": ("biv150_kv_pitched_bridge.cpp", "0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44"),
    "vllm_fl/patches/biv150_kv_pitched_bridge.so": ("biv150_kv_pitched_bridge.so", "9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0"),
}
MANIFEST = "pitched-save-source.json"


def prepare(output, *, root=owner.ROOT):
    if any(len(value) != 64 or any(c not in "0123456789abcdef" for c in value) for _, value in ASSETS.values()):
        raise RuntimeError("新SAVE素材未完成最终互审固定，禁止包装")
    if output.exists() or output.is_symlink():
        raise FileExistsError("输出必须为新目录，不覆盖任何原件")
    if owner.sha(Path(owner.__file__).read_bytes()) != EXPECTED_HELPER:
        raise RuntimeError("source_files辅助脚本身份变化")
    root, output = root.resolve(), output.resolve()
    if output.parent != root / "code" or not output.name.startswith("kv-pitched-save-"):
        raise ValueError("只接受ROOT/code下独立kv-pitched-save新目录")
    reference = root / "framework" / REFERENCE["control"]
    map_file = reference / "source-sha256.json"
    old_manifest = reference / "plugin-source/innovation-source.json"
    if (owner.sha(map_file.read_bytes()) != REFERENCE["source_manifest"]
            or owner.sha(old_manifest.read_bytes()) != REFERENCE["innovation_manifest"]):
        raise RuntimeError("214400完整参考manifest身份不符")
    expected_inputs = json.loads(map_file.read_text(encoding="utf-8"))
    prior = json.loads(old_manifest.read_text(encoding="utf-8"))
    required = {
        **{name: value for name, value in owner.BASE_HASHES.items() if name != owner.INIT},
        owner.INIT: INIT,
        "vllm_fl/worker/worker.py": "a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24",
        "vllm_fl/patches/biv150_runtime.py": "a0c09c51826e0b9e0e5c4f320e68451359db44001d56fd68e1e78de8dda2c9b4",
        "vllm_fl/patches/biv150_kv_page_copy.py": "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c",
        **{owner.PATCH_DIR + "biv150_kv_" + role + ".py": REFERENCE[role]
           for role in ("protocol", "transaction", "worker")},
    }
    if (len(expected_inputs) != 416
            or expected_inputs.get("innovation-source.json") != REFERENCE["innovation_manifest"]
            or any(expected_inputs.get(name) != value for name, value in required.items())
            or {n: h for n, h in expected_inputs.items() if n != "innovation-source.json"}
               != prior["output_sha256_excluding_this_manifest"]):
        raise RuntimeError("不接受其它FULL/观察器树或不完整416输入")
    base = root / "code" / REFERENCE["base"]
    if not base.is_dir() or base.resolve().parent != root / "code" or base.resolve() == output:
        raise ValueError("基点不是固定ROOT/code/214400 FULL")
    inputs = owner.source_files(base)
    if inputs != expected_inputs or MANIFEST in inputs:
        raise RuntimeError("完整基点变化或已叠本候选")
    raw_assets = {}
    for target, (name, expected_sha) in ASSETS.items():
        asset = root / "scripts" / name
        if asset.is_symlink() or not asset.is_file():
            raise RuntimeError("SAVE素材须普通文件：" + name)
        raw = asset.read_bytes()
        if owner.sha(raw) != expected_sha:
            raise RuntimeError("SAVE素材不是已审字节：" + name)
        if target.endswith(".py"):
            compile(raw, "isolated:" + target, "exec")
        raw_assets[target] = raw
    expected = {**inputs, **{name: value for name, (_, value) in ASSETS.items()}}
    if len(expected) != 419:
        raise RuntimeError("新树应为419项加独立manifest，禁止其它附加")
    shutil.copytree(base, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    try:
        if owner.source_files(output) != inputs or owner.source_files(base) != inputs:
            raise RuntimeError("复制期间基点变化或复制字节不符")
        for target, raw in raw_assets.items():
            (output / target).write_bytes(raw)
        actual = owner.source_files(output)
        if actual != expected:
            raise RuntimeError("除SAVE worker与固定附加桥素材外出现其它字节变化")
        result = {
            "status": "prepared_not_executed", "variant": "full-R-pitched-save-on-frozen-full-restore",
            "created_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
            "base_source": str(base), "output": str(output), "input_sha256": inputs,
            "preparer_sha256": owner.sha(Path(__file__).read_bytes()), "source_helper_sha256": EXPECTED_HELPER,
            "reference": REFERENCE, "asset_input_files": {n: v[0] for n, v in ASSETS.items()},
            "asset_sha256": {n: v[1] for n, v in ASSETS.items()}, "source_count_including_this_manifest": 420,
            "original_innovation_manifest_preserved_sha256": inputs["innovation-source.json"],
            "output_sha256_excluding_this_manifest": actual,
            "changes": {n: {"before": inputs.get(n), "after": h} for n, h in actual.items() if inputs.get(n) != h},
            "limits": ["原innovation-source.json仅为冻结FULL基点证据，不是新树的当前完整身份。",
                       "当前完整身份由本manifest输出映射及自身SHA组成；只替换canonical worker的SAVE并附三个固定素材。",
                       "init791c/protocol1aff/txn84be/e155/c95f不改；worker5d9a只在独立树替为新SAVE实现，不叠6a/72942。",
                       "安装marker仅预检；须新SAVE真ACK及源free前42层c95f字节对照、旧FULL回读和原消费者。",
                       "桥SO固定为已验SDK编译9e33，不在worker编译；首轮VERIFY1仅机制诊断，不计性能或新accuracy。"],
        }
    except BaseException as error:
        with (output / MANIFEST).open("x", encoding="utf-8") as file:
            json.dump({"status": "failed_preparation", "error": repr(error)}, file)
            file.write("\n")
        raise
    with (output / MANIFEST).open("x", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=True, indent=2)
        file.write("\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.output)
    print(json.dumps({"status": result["status"], "output": result["output"], "changes": result["changes"]}))
