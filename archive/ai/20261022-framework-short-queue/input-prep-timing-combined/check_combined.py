"""只核组合基点新增锚点与完整准备调用，复用原诊断语义验证。"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.with_name("input-prep-timing")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def context_function(data):
    tree = ast.parse(data)
    return ast.dump(next(n for n in ast.walk(tree)
                         if isinstance(n, ast.FunctionDef) and n.name == "synchronize_input_prep"))


def main():
    old_hashes = {p.name: sha(p.read_bytes()) for p in OLD.iterdir() if p.is_file()}
    old, new = module(OLD / "prepare_input_prep_timing.py", "old_prep"), module(HERE / "prepare_input_prep_timing.py", "new_prep")
    for key in ("OLD_HEADER", "NEW_HEADER", "OLD_CALL", "NEW_CALL"):
        assert getattr(old, key) == getattr(new, key), key
    assert (OLD / "biv150_input_prep_timing.py").read_bytes() == (HERE / "biv150_input_prep_timing.py").read_bytes()
    combined = (ROOT / "docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py").read_bytes()
    baseline = (ROOT / "docs/pr-preparation/combination-artifacts/base-model_runner.py").read_bytes()
    assert sha(combined) == new.BASE_SHA
    assert context_function(combined) == context_function(baseline)
    changed = new.transform(combined)
    # 原装饰器、默认/dummy 调用及真实调用仍唯一；没有增加模型侧同步。
    assert context_function(changed) == context_function(old.transform(baseline))
    assert changed.count(b"self.synchronize_input_prep(_biv150_measure=True)") == 1
    assert changed.count(b"with self.synchronize_input_prep():") == 1
    source = ROOT / "experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k-control/plugin-source"
    command = [sys.executable, str(HERE / "prepare_input_prep_timing.py"),
               "--base-dir", str(source), "--output-dir", str(HERE / "prepared-source")]
    (HERE / "check-command.json").write_text(json.dumps(command, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
    (HERE / "check-preparation.log").write_text(completed.stdout + completed.stderr, encoding="utf-8")
    assert (HERE / "prepared-source" / new.RUNNER).read_bytes() == changed
    for path, expected in new.COMBINED_HELPERS.items():
        assert sha((HERE / "prepared-source" / path).read_bytes()) == expected
    assert old_hashes == {p.name: sha(p.read_bytes()) for p in OLD.iterdir() if p.is_file()}
    receipt = json.loads((HERE / "prepared-source-preparation.json").read_text(encoding="utf-8"))
    result = {"combined_exact_sha": new.BASE_SHA, "context_ast_unchanged_from_e155": True,
              "diagnostic_branch_and_helper_unchanged": True, "real_dummy_anchors_unique": True,
              "existing_original_package_unchanged": True, "full_prepare_exit_code": completed.returncode,
              "base_file_count": len(receipt["base_source_sha256"]),
              "prepared_file_count": len(receipt["source_sha256"]),
              "runner_sha256": sha(changed),
              "artifact_sha256": {name: sha((HERE / name).read_bytes()) for name in
                 ("prepare_input_prep_timing.py", "biv150_input_prep_timing.py", "launch_input_prep_timing.sh")},
              "scope": "CPU only; prior diagnostic runtime tests reused; no torch/SSH/GPU"}
    (HERE / "cpu-check-combined.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
