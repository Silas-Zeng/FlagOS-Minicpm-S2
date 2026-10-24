"""生成独立clean6f基线或no-cascade skip候选源；只CPU复制。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

RUNNER = "vllm_fl/worker/model_runner.py"
INIT = "vllm_fl/__init__.py"
HELPER = "vllm_fl/patches/biv150_no_cascade_prefix.py"
ASSETS = {"biv150_no_cascade_prefix.py": "e17af034150a6274c4d14c94b7bf355a1541f05929521c846a4e3de320314131", "skip_init_footer.py": "b588a3d516e0ab748164679d0815e625695b1fb433335b91dfa96d73351baf70"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def mapping(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder)
        if any(part in (".git", "__pycache__") for part in rel.parts) or path.suffix in (".pyc", ".pyo"):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(folder):
                raise ValueError("外部/目录link")
        if path.is_file():
            result[rel.as_posix()] = sha(path.read_bytes())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--variant", choices=("candidate", "baseline"), required=True)
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + "-preparation.json")
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise ValueError("输出须全新且不交叠")
    assets = Path(__file__).parent
    reference_raw = (assets / "base-source-sha256.json").read_bytes()
    if sha(reference_raw) != "443555886596b94372076aa40e1b159f70475bca7f7a1e0fc901a69804566a34":
        raise ValueError("基点map变化")
    reference = json.loads(reference_raw)
    before = mapping(base)
    if len(reference) != 412 or before != reference:
        raise ValueError("非完整clean6f412源")
    values = {}
    for name, expected in ASSETS.items():
        values[name] = (assets / name).read_bytes()
        if sha(values[name]) != expected:
            raise ValueError("资产SHA变化: " + name)
    raw = (base / INIT).read_bytes()
    changed = raw + values["skip_init_footer.py"]
    compile(changed, "isolated:prefix-skip-init", "exec")
    compile(values["biv150_no_cascade_prefix.py"], "isolated:prefix-skip-helper", "exec")
    shutil.copytree(base, output, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    expected = dict(before)
    changed_paths = []
    if args.variant == "candidate":
        (output / INIT).write_bytes(changed)
        (output / HELPER).write_bytes(values["biv150_no_cascade_prefix.py"])
        expected.update({INIT: sha(changed), HELPER: ASSETS["biv150_no_cascade_prefix.py"]})
        changed_paths = [INIT, HELPER]
    if mapping(base) != before or mapping(output) != expected:
        raise ValueError("非预期源变更")
    receipt.write_text(json.dumps({"kind": "独立no-cascade公共前缀统计skip服务对照；非observer", "variant": args.variant,
        "base_source_sha256": before, "source_sha256": expected, "changed_paths": changed_paths,
        "runner_unchanged": expected[RUNNER] == before[RUNNER], "source": str(output),
        "mode": "skip" if args.variant == "candidate" else "clean6f",
        "enabled_environment": "BIV150_NO_CASCADE_PREFIX_SKIP=1" if args.variant == "candidate" else None,
        "observe_enabled": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source": str(output), "receipt": str(receipt)}))


if __name__ == "__main__":
    main()
