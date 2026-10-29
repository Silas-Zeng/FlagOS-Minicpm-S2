#!/usr/bin/env python3
"""Build two isolated host-launcher SOs; compile only, never initializes device."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
FLAGS = ["-O3", "-std=c++17", "-fPIC", "-shared", "-D__ILUVATAR__", "-D__MR__",
         "-DCOREX_NATIVE_GQA_V_OVERLAP=1", "-x", "ivcore", "--cuda-gpu-arch=ivcore11",
         "--cuda-path=/usr/local/corex"]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--compiler", default="/usr/local/corex/bin/clang++")
    a = ap.parse_args()
    out = a.out.resolve()
    if not out.is_absolute() or out.exists():
        ap.error("--out must be a fresh absolute output directory")
    if "torch" in sys.modules or "triton" in sys.modules:
        raise RuntimeError("build entry must remain framework/device initialization free")
    prepared = HERE / "source-manifest.json"
    if not prepared.is_file():
        ap.error("Run prepare_pair.py first")
    manifest = json.loads(prepared.read_text(encoding="utf-8"))
    compiler = Path(a.compiler)
    if not compiler.is_file():
        ap.error(f"compiler not found: {compiler}")
    out.mkdir(parents=True)
    (out / "build-input-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    result = dict(compile_only=True, runtime_executed=False, gpu_executed=False,
                  compiler=str(compiler), compiler_sha256=sha(compiler), flags=FLAGS,
                  arms={}, reducer="same unchanged framework _reduce_partials; loaded by runtime worker")
    version = subprocess.run([str(compiler), "--version"], capture_output=True, text=True)
    (out / "compiler-version.txt").write_text(version.stdout + version.stderr, encoding="utf-8")
    if version.returncode:
        raise RuntimeError("compiler --version failed")
    for arm in ("A", "B"):
        rel = manifest["arms"][arm]["source"]
        source = (HERE / rel).resolve()
        if sha(source) != manifest["arms"][arm]["source_sha256"]:
            raise RuntimeError(f"source drift: {arm}")
        target = out / f"libnative_k8_sme_{arm}.so"
        command = [str(compiler), *FLAGS, str(source), "-o", str(target)]
        proc = subprocess.run(command, capture_output=True, text=True)
        (out / f"{arm}.stdout.txt").write_text(proc.stdout, encoding="utf-8")
        (out / f"{arm}.stderr.txt").write_text(proc.stderr, encoding="utf-8")
        result["arms"][arm] = dict(command=command, exit_code=proc.returncode,
                                   library=target.name if target.is_file() else None,
                                   library_sha256=sha(target) if target.is_file() else None,
                                   source_sha256=sha(source))
        if proc.returncode or not target.is_file() or not target.stat().st_size:
            (out / "build-summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            return 1
    result["completed"] = True
    result["abi"] = {
        "arguments": ["query:void*", "key:int8*", "key_scale_full:float*", "value:bf16*", "seq_lens:int*",
                      "block_table:int*", "batch:int", "scale:float", "table_stride:i64", "q_token_stride:i64",
                      "q_head_stride:i64", "acc_token_stride:i64", "acc_head_stride:i64", "acc_segment_stride:i64",
                      "scalar_token_stride:i64", "scalar_head_stride:i64", "acc:float*", "maximum:float*",
                      "summation:float*", "stream:cudaStream_t"],
        "launchers": {arm: [f"launch_cjj_native_k8_{arm.lower()}_klookahead_s2", f"launch_cjj_native_k8_{arm.lower()}_klookahead_s4"]
                      for arm in ("A", "B")}}
    (out / "build-summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
