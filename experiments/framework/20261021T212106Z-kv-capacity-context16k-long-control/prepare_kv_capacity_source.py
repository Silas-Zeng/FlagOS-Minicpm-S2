#!/usr/bin/env python3
"""从冻结080656包装独立容量快拒候选，输入新asset、输出canonical模块名。"""
import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

import prepare_innovation_source as owner

EXPECTED_HELPER = "0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca"
ASSETS = {
    "biv150_kv_completion_probe.py": "a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6",
    "biv150_kv_page_copy.py": "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c",
    "biv150_kv_transaction.py": "616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13",
    "biv150_kv_protocol.py": "67e4c07566ee3e52f84d6a96a494b8976d858420dadd5f833e66c3291e32fb73",
    "biv150_kv_worker.py": "31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf",
}
ASSET_INPUT_FILES = {"biv150_kv_protocol.py": "biv150_kv_capacity_protocol.py"}
CORE = {
    "vllm_fl/worker/worker.py": "a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24",
    "vllm_fl/patches/biv150_runtime.py": "a0c09c51826e0b9e0e5c4f320e68451359db44001d56fd68e1e78de8dda2c9b4",
    "vllm_fl/patches/biv150_top_p_triton.py": "da77c411a88ad4ead072c99cdc4edb52b5bef5b8e5990b9cc8e04db08ed31ca9",
}
EXPECTED_INIT_OUTPUT = "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8"


def prepare(base, output, assets, *, root=owner.ROOT):
    if any(len(value) != 64 for value in (*ASSETS.values(), EXPECTED_INIT_OUTPUT)):
        raise RuntimeError("协议素材尚未完成最终互审固定，禁止包装执行")
    if output.exists() or output.is_symlink():
        raise FileExistsError("输出须为全新目录，不覆盖旧实验")
    if owner.sha(Path(owner.__file__).read_bytes()) != EXPECTED_HELPER:
        raise RuntimeError("source_files辅助脚本身份不符")
    root, base, output, assets = root.resolve(), base.resolve(), output.resolve(), assets.resolve()
    if (base.parent != root / "code" or base.name != owner.BASE_NAME or not base.is_dir()
            or output.parent != root / "code" or output == base
            or assets != root / "scripts" or not assets.is_dir()):
        raise ValueError("只接受原080656、ROOT/code全新直接子目录、ROOT/scripts素材")
    inputs = owner.source_files(base)
    required = {**owner.BASE_HASHES, **CORE}
    if "innovation-source.json" in inputs:
        raise RuntimeError("拒绝叠加已有候选")
    expected_biv = {name for name in required if name.startswith(owner.PATCH_DIR)}
    actual_biv = {name for name in inputs if name.startswith(owner.PATCH_DIR)
                  and Path(name).name.startswith("biv150") and name.endswith(".py")}
    if expected_biv != actual_biv or any(inputs.get(n) != h for n, h in required.items()):
        raise RuntimeError("冻结基线源码/模块集合身份不符")
    raw_assets = {}
    for name, expected in ASSETS.items():
        path = assets / ASSET_INPUT_FILES.get(name, name)
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("素材必须为普通文件：" + name)
        raw = path.read_bytes()
        if owner.sha(raw) != expected:
            raise RuntimeError("素材SHA不符：" + name)
        compile(raw, "isolated:" + name, "exec")
        raw_assets[name] = raw
    constants = {node.targets[0].id: ast.literal_eval(node.value)
                 for node in ast.parse(raw_assets["biv150_kv_protocol.py"]).body
                 if isinstance(node, ast.Assign) and len(node.targets) == 1
                 and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id in ("EXPECTED_INIT", "INIT_FOOTER")}
    original = (base / owner.INIT).read_bytes()
    if constants["EXPECTED_INIT"] != inputs[owner.INIT] or owner.sha(original) != inputs[owner.INIT]:
        raise RuntimeError("init读取期间变化或协议常量身份不符")
    changed = original + constants["INIT_FOOTER"]
    if owner.sha(changed) != EXPECTED_INIT_OUTPUT:
        raise RuntimeError("init不是已审精确append产物")
    compile(changed, "isolated:" + owner.INIT, "exec")
    expected = {**inputs, owner.INIT: owner.sha(changed),
                **{owner.PATCH_DIR + n: h for n, h in ASSETS.items()}}
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
        for name, raw in raw_assets.items():
            (output / owner.PATCH_DIR / name).write_bytes(raw)
        actual = owner.source_files(output)
        if actual != expected:
            raise RuntimeError("包装出现额外源码变化")
        manifest = {
            "status": "prepared_not_executed", "variant": "single-victim-kv-capacity-fast-reject-on-sql-c3",
            "created_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
            "base_source": str(base), "output": str(output),
            "preparer_sha256": owner.sha(Path(__file__).read_bytes()),
            "source_helper_sha256": EXPECTED_HELPER, "base_required_sha256": required,
            "input_sha256": inputs, "input_file_aliases_dereferenced": aliases, "asset_sha256": ASSETS,
            "asset_input_files": {name: ASSET_INPUT_FILES.get(name, name) for name in ASSETS},
            "changes": {n: {"before": inputs.get(n), "after": h}
                        for n, h in actual.items() if inputs.get(n) != h},
            "output_sha256_excluding_this_manifest": actual,
            "validation": "stdlib AST/compile/full-copy SHA only; no candidate/framework imports",
            "limits": ["仅隔离init显式启用协议，runner e155保持不变。",
                       "capacity新asset只映射到新source的canonical协议名，不覆盖当前0e。",
                       "Request guard只控制快捷路径，须实际fast_rejects>0才证明生效。",
                       "首门VERIFY_RESTORE=1是诊断，不作性能或accuracy结论。",
                       "须有实际保存/恢复/字节回读/后继消费；安装标记不代表路径完成。"],
        }
    except BaseException as error:
        (output / "innovation-source.json").write_text(json.dumps({
            "status": "failed_preparation", "base_source": str(base), "output": str(output),
            "error": repr(error)}, indent=2) + "\n", encoding="utf-8")
        raise
    (output / "innovation-source.json").write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--asset-dir", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.base_source, args.output, args.asset_dir)
    print(json.dumps({"status": result["status"], "output": result["output"], "changes": result["changes"]}))
