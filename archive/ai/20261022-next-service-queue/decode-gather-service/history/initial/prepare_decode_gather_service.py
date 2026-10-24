"""从精确 6f918 组合创建 baseline 或独立纯 decode CPU gather 副本；不安装或启动设备。"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone

BASE_SHA = "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141"
RUNTIME_SHA = "1a9de781b2f9504c627991071c5ee4b52eda59ca8af283f28a15b9fab38ef7bd"
FOOTER_SHA = "5b9dcc8a61ceaaf36aa627eff5a8a832f99863f8b9342b5110081f9dc279b23b"
RUNNER = "vllm_fl/worker/model_runner.py"
HELPER = "vllm_fl/patches/biv150_decode_cpu_gather.py"
DEPENDENCIES = {
    "vllm_fl/patches/biv150_cpu_metadata.py": "0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f",
    "vllm_fl/patches/biv150_async_token_update.py": "1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc",
    "vllm_fl/patches/biv150_mixed_decode.py": "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42",
}
ANCHOR = b'    print("BIV150_MIXED_DECODE_INSTALLED", _install_mixed_decode(), flush=True)\n'



def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_runtime():
    path = Path(__file__).with_name("biv150_decode_cpu_gather.py")
    if digest(path.read_bytes()) != RUNTIME_SHA:
        raise RuntimeError("原 runtime 1a9de781 变化")
    spec = importlib.util.spec_from_file_location("decode_gather_service_transformer", path)
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    return runtime


def transform(raw):
    if digest(raw) != BASE_SHA or raw.count(ANCHOR) != 1 or not raw.endswith(ANCHOR):
        raise RuntimeError("只接受精确6f组合，无C3views或其他候选")
    footer = Path(__file__).with_name("service_append.py").read_bytes()
    if digest(footer) != FOOTER_SHA:
        raise RuntimeError("真实 execute 观察 footer 变化")
    runtime = load_runtime()
    prepared = runtime.transform(raw)
    changed = prepared + footer
    if runtime.reverse(changed[:-len(footer)]) != raw:
        raise RuntimeError("原6f不可逐字节逆回")
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
    parser.add_argument("--variant", required=True, choices=("baseline", "candidate"))
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + "-preparation.json")
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise RuntimeError("输出必须新建且与基点互不包含")
    before = source_map(base)
    if before.get(RUNNER) != BASE_SHA or any(before.get(p) != s for p, s in DEPENDENCIES.items()):
        raise RuntimeError("当前组合基点变化")
    if HELPER in before:
        raise RuntimeError("基点已含纯gather候选，不能重复计收益")
    helper = Path(__file__).with_name("biv150_decode_cpu_gather.py").read_bytes()
    if digest(helper) != RUNTIME_SHA:
        raise RuntimeError("受测runtime必须逐字节保留1a9de781")
    compile(helper, HELPER, "exec")
    raw = (base / RUNNER).read_bytes()
    changed = transform(raw) if args.variant == "candidate" else raw
    expected = dict(before)
    changed_paths = []
    shutil.copytree(base, output, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    if args.variant == "candidate":
        (output / RUNNER).write_bytes(changed)
        (output / HELPER).write_bytes(helper)
        expected.update({RUNNER: digest(changed), HELPER: digest(helper)})
        changed_paths = [RUNNER, HELPER]
    if source_map(output) != expected or source_map(base) != before:
        raise RuntimeError("副本或基点出现未声明变化")
    data = {"utc": datetime.now(timezone.utc).isoformat(), "argv": sys.argv,
            "base": str(base), "source": str(output), "variant": args.variant,
            "base_runner_sha256": BASE_SHA, "runtime_sha256": RUNTIME_SHA, "observer_footer_sha256": FOOTER_SHA,
            "kind": "paired short service screen; not official result",
            "changed_paths": changed_paths, "source_sha256": expected,
            "base_source_sha256": before, "preparer_sha256": digest(Path(__file__).read_bytes())}
    receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"prepared": str(output), "receipt": str(receipt),
                      "variant": args.variant, "runner_sha256": digest(changed)}))


if __name__ == "__main__":
    main()
