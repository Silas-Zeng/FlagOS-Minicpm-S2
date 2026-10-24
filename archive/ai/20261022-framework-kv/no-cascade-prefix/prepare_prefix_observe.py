"""生成独立clean6f公共前缀成本观察源；只CPU复制，不启动服务。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

RUNNER = "vllm_fl/worker/model_runner.py"
INIT = "vllm_fl/__init__.py"
HELPER = "vllm_fl/patches/biv150_no_cascade_prefix.py"
ASSETS = {"biv150_no_cascade_prefix.py": "e17af034150a6274c4d14c94b7bf355a1541f05929521c846a4e3de320314131", "observe_init_footer.py": "002007a57474d8502c9e5f29aeda5c5fa0ad610a8590920a7ed93bc5de262679"}

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
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + "-preparation.json")
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise ValueError("输出须全新且不交叠")
    assets = Path(__file__).parent
    reference = json.loads((assets / "base-source-sha256.json").read_text(encoding="utf-8"))
    before = mapping(base)
    if len(reference) != 412 or before != reference:
        raise ValueError("非完整clean6f412源")
    values = {}
    for name, expected in ASSETS.items():
        values[name] = (assets / name).read_bytes()
        if sha(values[name]) != expected:
            raise ValueError("资产SHA变化: " + name)
    raw = (base / INIT).read_bytes()
    changed = raw + values["observe_init_footer.py"]
    compile(changed, "isolated:prefix-observe-init", "exec")
    compile(values["biv150_no_cascade_prefix.py"], "isolated:prefix-observe-helper", "exec")
    shutil.copytree(base, output, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    (output / INIT).write_bytes(changed)
    (output / HELPER).write_bytes(values["biv150_no_cascade_prefix.py"])
    expected = {**before, INIT: sha(changed), HELPER: ASSETS["biv150_no_cascade_prefix.py"]}
    if mapping(base) != before or mapping(output) != expected:
        raise ValueError("非预期源变更")
    receipt.write_text(json.dumps({"kind": "CPU prefix-cost observation only; no skip deployment", "base_source_sha256": before,
        "source_sha256": expected, "changed_paths": [INIT, HELPER], "runner_unchanged": expected[RUNNER] == before[RUNNER],
        "source": str(output), "mode": "observe", "enabled_environment": "BIV150_PREFIX_COST_OBSERVE=1"}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source": str(output), "receipt": str(receipt)}))

if __name__ == "__main__":
    main()
