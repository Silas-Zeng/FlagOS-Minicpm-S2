"""从固定完整6f创建独立异步bookkeeping候选或原基线；不改变事件与输出快照。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone

BASE_SHA = "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141"
EXPECTED_POLICY = "c7c91ecee246661977444b53af08e8d1327c1ef32e3cbae5f54689b391ef402f"
EXPECTED_APPEND = "7e8196ada53eb15d3c435a4451c4197d5ceef556f2d43442996ceca07ba750ca"
EXPECTED_BASE_MAP = "443555886596b94372076aa40e1b159f70475bca7f7a1e0fc901a69804566a34"
RUNNER = "vllm_fl/worker/model_runner.py"
HELPER = "vllm_fl/patches/biv150_async_bookkeeping.py"
ANCHOR = b'    print("BIV150_MIXED_DECODE_INSTALLED", _install_mixed_decode(), flush=True)\n'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def transform(raw, suffix):
    if digest(raw) != BASE_SHA or raw.count(ANCHOR) != 1 or not raw.endswith(ANCHOR):
        raise RuntimeError("只接受完整6f918原C3安装后的接点")
    text = raw.decode("utf-8")
    cls = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef) and n.name == "ModelRunnerFL")
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_bookkeeping_sync")
    loops = [n for n in method.body if isinstance(n, ast.For) and isinstance(n.target, ast.Name) and n.target.id == "req_idx"]
    if len(loops) != 1:
        raise RuntimeError("原bookkeeping循环不唯一")
    loop = loops[0]
    lines = text.splitlines(keepends=True)
    original = "".join(lines[loop.lineno-1:loop.end_lineno])
    # sync分支没有invalid_req_indices_set；左侧短路须先于helper实参求值。
    guard = ("        if not (self.use_async_scheduling and num_sampled_tokens >= 16 and\n"
             "                _biv150_try_bulk_bookkeeping(self, num_sampled_tokens, sampled_token_ids,\n"
             "                                             invalid_req_indices_set, scheduler_output)):\n")
    replacement = guard + "".join("    " + line for line in original.splitlines(keepends=True))
    anchor = "from vllm_fl.patches.biv150_async_token_update import fused_sampled_token_update as _biv150_fused_sampled_token_update\n"
    added = "from vllm_fl.patches.biv150_async_bookkeeping import try_bulk_bookkeeping as _biv150_try_bulk_bookkeeping\n"
    if text.count(anchor) != 1 or text.count(original) != 1:
        raise RuntimeError("接点不唯一")
    changed = text.replace(original, replacement, 1).replace(anchor, anchor + added, 1).encode() + suffix
    inverse = changed[:-len(suffix)].decode().replace(anchor + added, anchor, 1).replace(replacement, original, 1).encode()
    if inverse != raw:
        raise RuntimeError("新增import/guard/footer不能精确逆回6f")
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
    parser.add_argument("--variant", choices=("baseline", "candidate"), required=True)
    parser.add_argument("--base-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + "-preparation.json")
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise RuntimeError("输出必须新建且与基点互不包含")
    assets = Path(__file__).parent
    map_raw = (assets / "base-source-sha256.json").read_bytes()
    helper = (assets / "biv150_async_bookkeeping.py").read_bytes()
    suffix = (assets / "service_append.py").read_bytes()
    if (digest(map_raw) != EXPECTED_BASE_MAP or digest(helper) != EXPECTED_POLICY
            or digest(suffix) != EXPECTED_APPEND):
        raise RuntimeError("未冻结或已变化的async-bookkeeping接线素材")
    expected_base = json.loads(map_raw)
    before = source_map(base)
    if len(expected_base) != 412 or before != expected_base or before.get(RUNNER) != BASE_SHA:
        raise RuntimeError("完整412文件的6f组合基点不匹配")
    if HELPER in before:
        raise RuntimeError("基点已叠async-bookkeeping候选")
    compile(helper, HELPER, "exec")
    changed = transform((base / RUNNER).read_bytes(), suffix)
    expected = dict(before)
    if args.variant == "candidate":
        expected.update({RUNNER: digest(changed), HELPER: digest(helper)})
    if len(expected) != (413 if args.variant == "candidate" else 412):
        raise RuntimeError("仅candidate允许runner替换和一个独立helper")
    shutil.copytree(base, output, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    if args.variant == "candidate":
        (output / RUNNER).write_bytes(changed)
        (output / HELPER).write_bytes(helper)
    if source_map(output) != expected or source_map(base) != before:
        raise RuntimeError("副本或基点出现未声明变化")
    data = {
        "utc": datetime.now(timezone.utc).isoformat(), "argv": sys.argv,
        "base": str(base), "source": str(output), "variant": args.variant,
        "base_runner_sha256": BASE_SHA, "policy_sha256": digest(helper),
        "append_sha256": digest(suffix), "base_map_sha256": digest(map_raw),
        "kind": "original-parameter async CPU bookkeeping short screen; not accuracy or matched-performance proof",
        "changed_paths": [RUNNER, HELPER] if args.variant == "candidate" else [], "source_sha256": expected,
        "base_source_sha256": before, "preparer_sha256": digest(Path(__file__).read_bytes()),
    }
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"prepared": str(output), "receipt": str(receipt),
                      "runner_sha256": expected[RUNNER], "source_files": len(expected)}))


if __name__ == "__main__":
    main()
