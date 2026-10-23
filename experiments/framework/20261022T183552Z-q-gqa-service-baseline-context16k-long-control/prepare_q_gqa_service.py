"""从固定完整6f组合创建独立GQA基线或GQA+Q候选；只对exact GQA扩展Q身份守卫。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone

BASE_SHA = "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141"
EXPECTED_POLICY = "51fcaf55133124c2e51dfa0385e1939bf908b65f8444ac63f912329f6ca73800"
EXPECTED_APPEND = "409e4896ad1b85848d2b1b4afb3e144d6cff8a42aeb1316c78d61ee117300ace"
EXPECTED_BASE_MAP = "443555886596b94372076aa40e1b159f70475bca7f7a1e0fc901a69804566a34"
EXPECTED_GQA = "1a81409ba23a149081f7fc257460ea1512cbfdceeb0af32a2698994958749b9a"
EXPECTED_GQA_APPEND = "ba28b9d9bff49a761b2606aa6f707c5c7ef813d665cc8fac85ad665029433803"
EXPECTED_GQA_RUNNER = "cc7f834d25ccbe5d839a731b8e9aa8bf7533bea6f2f937c394423b3844842dfe"
GQA = "vllm_fl/patches/biv150_gqa_decode.py"
RUNNER = "vllm_fl/worker/model_runner.py"
HELPER = "vllm_fl/patches/biv150_q_fragment_service.py"
ANCHOR = b'    print("BIV150_MIXED_DECODE_INSTALLED", _install_mixed_decode(), flush=True)\n'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def transform(raw, gqa_suffix, suffix, variant):
    if digest(raw) != BASE_SHA or raw.count(ANCHOR) != 1 or not raw.endswith(ANCHOR):
        raise RuntimeError("只接受完整6f918原C3安装后的接点")
    gqa_runner = raw + gqa_suffix
    if digest(gqa_runner) != EXPECTED_GQA_RUNNER:
        raise RuntimeError("原PR12 runner不是exact6f+exact GQA footer")
    changed = gqa_runner + suffix if variant == "candidate" else gqa_runner
    if not changed.startswith(raw):
        raise RuntimeError("原runner未逐字节保留")
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
    parser.add_argument("--variant", choices=("baseline","candidate"), required=True)
    parser.add_argument("--base-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + "-preparation.json")
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise RuntimeError("输出必须新建且与基点互不包含")
    assets = Path(__file__).parent
    map_raw = (assets / "base-source-sha256.json").read_bytes()
    helper = (assets / "biv150_q_fragment_service.py").read_bytes()
    suffix = (assets / "service_append.py").read_bytes()
    gqa = (assets / "biv150_gqa_decode.py").read_bytes()
    gqa_suffix = (assets / "gqa_append.py").read_bytes()
    if (digest(map_raw) != EXPECTED_BASE_MAP or digest(helper) != EXPECTED_POLICY
            or digest(suffix) != EXPECTED_APPEND
            or digest(gqa) != EXPECTED_GQA or digest(gqa_suffix) != EXPECTED_GQA_APPEND):
        raise RuntimeError("未冻结或已变化的Q-hoist接线素材")
    expected_base = json.loads(map_raw)
    before = source_map(base)
    if len(expected_base) != 412 or before != expected_base or before.get(RUNNER) != BASE_SHA:
        raise RuntimeError("完整412文件的6f组合基点不匹配")
    if HELPER in before or GQA in before:
        raise RuntimeError("基点已叠Q-hoist候选")
    compile(helper, HELPER, "exec")
    compile(gqa, GQA, "exec")
    changed = transform((base / RUNNER).read_bytes(), gqa_suffix, suffix, args.variant)
    expected = dict(before)
    expected.update({RUNNER: digest(changed), GQA: digest(gqa)})
    if args.variant == "candidate": expected[HELPER] = digest(helper)
    if len(expected) != (414 if args.variant == "candidate" else 413):
        raise RuntimeError("只允许runner替换及exact GQA/Q helper")
    shutil.copytree(base, output, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    (output / RUNNER).write_bytes(changed)
    (output / GQA).write_bytes(gqa)
    if args.variant == "candidate": (output / HELPER).write_bytes(helper)
    if source_map(output) != expected or source_map(base) != before:
        raise RuntimeError("副本或基点出现未声明变化")
    data = {
        "utc": datetime.now(timezone.utc).isoformat(), "argv": sys.argv,
        "base": str(base), "source": str(output), "variant": args.variant,
        "base_runner_sha256": BASE_SHA, "policy_sha256": digest(helper),
        "append_sha256": digest(suffix), "base_map_sha256": digest(map_raw),
        "kind": "original-parameter GQA baseline vs Q+GQA; combination accuracy not inherited",
        "gqa_sha256": digest(gqa), "gqa_append_sha256": digest(gqa_suffix),
        "changed_paths": [RUNNER, GQA, HELPER] if args.variant == "candidate" else [RUNNER,GQA], "source_sha256": expected,
        "base_source_sha256": before, "preparer_sha256": digest(Path(__file__).read_bytes()),
    }
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"prepared": str(output), "receipt": str(receipt),
                      "runner_sha256": digest(changed), "source_files": len(expected)}))


if __name__ == "__main__":
    main()
