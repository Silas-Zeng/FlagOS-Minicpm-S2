"""从精确 6f918 组合基点创建独立诊断副本；不安装、不启动服务。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone

BASE_SHA = "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141"
RUNNER = "vllm_fl/worker/model_runner.py"
HELPER = "vllm_fl/patches/biv150_input_prep_timing.py"
COMBINED_HELPERS = {
    "vllm_fl/patches/biv150_cpu_metadata.py": "0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f",
    "vllm_fl/patches/biv150_async_token_update.py": "1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc",
}
OLD_HEADER = b"    def synchronize_input_prep(self):\n"
NEW_HEADER = b'''    def synchronize_input_prep(self, _biv150_measure=False):
        if _biv150_measure and self.prepare_inputs_event is not None:
            from vllm_fl.patches.biv150_input_prep_timing import get_recorder
            recorder = get_recorder(self)
            started = time.perf_counter_ns()
            try:
                self.prepare_inputs_event.synchronize()
            except BaseException:
                elapsed = time.perf_counter_ns() - started
                recorder.add(elapsed, elapsed, failed_wait=True)
                raise
            waited = time.perf_counter_ns() - started
            try:
                yield
            finally:
                try:
                    self.prepare_inputs_event.record()
                finally:
                    elapsed = time.perf_counter_ns() - started
                    recorder.add(waited, elapsed)
            return
'''
OLD_CALL = b'''            record_function_or_nullcontext("gpu_model_runner: preprocess"),
            self.synchronize_input_prep(),
'''
NEW_CALL = b'''            record_function_or_nullcontext("gpu_model_runner: preprocess"),
            self.synchronize_input_prep(_biv150_measure=True),
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def transform(original):
    if digest(original) != BASE_SHA:
        raise RuntimeError("拒绝非 6f918 组合基点")
    if original.count(OLD_HEADER) != 1 or original.count(OLD_CALL) != 1:
        raise RuntimeError("真实服务挂点不唯一")
    if original.count(b"        with self.synchronize_input_prep():\n") != 1:
        raise RuntimeError("dummy_run 挂点变化")
    changed = original.replace(OLD_HEADER, NEW_HEADER).replace(OLD_CALL, NEW_CALL)
    if changed.replace(NEW_HEADER, OLD_HEADER).replace(NEW_CALL, OLD_CALL) != original:
        raise RuntimeError("诊断替换不可逐字节逆回")
    compile(changed, RUNNER, "exec")
    return changed


def source_map(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder)
        if any(x in (".git", "__pycache__") for x in rel.parts) or path.suffix in (".pyc", ".pyo"):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(folder.resolve()):
                raise RuntimeError("拒绝外部或目录链接: " + str(rel))
        if path.is_file():
            result[rel.as_posix()] = digest(path.read_bytes())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + "-preparation.json")
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise RuntimeError("输出必须是新建且与基点互不包含的目录")
    before = source_map(base)
    if any(before.get(path) != sha for path, sha in COMBINED_HELPERS.items()):
        raise RuntimeError("组合基点的 metadata/async 实现缺失或变化")
    changed = transform((base / RUNNER).read_bytes())
    helper = Path(__file__).with_name("biv150_input_prep_timing.py").read_bytes()
    compile(helper, HELPER, "exec")
    if HELPER in before:
        raise RuntimeError("基点已有同名诊断")
    shutil.copytree(base, output, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    (output / RUNNER).write_bytes(changed)
    (output / HELPER).write_bytes(helper)
    expected = dict(before, **{RUNNER: digest(changed), HELPER: digest(helper)})
    if source_map(output) != expected or source_map(base) != before:
        raise RuntimeError("副本或原基点发生未声明变化")
    data = {"utc": datetime.now(timezone.utc).isoformat(), "argv": sys.argv,
            "base": str(base), "output": str(output), "base_runner_sha256": BASE_SHA,
            "kind": "diagnostic_only_not_performance", "changed_paths": [RUNNER, HELPER],
            "source_sha256": expected, "base_source_sha256": before,
            "preparer_sha256": digest(Path(__file__).read_bytes())}
    receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"prepared": str(output), "receipt": str(receipt),
                      "runner_sha256": digest(changed), "helper_sha256": digest(helper)}))


if __name__ == "__main__":
    main()
