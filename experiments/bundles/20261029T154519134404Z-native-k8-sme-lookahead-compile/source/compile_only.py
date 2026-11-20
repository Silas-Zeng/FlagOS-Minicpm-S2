#!/usr/bin/env python3
"""Compile-only LLVM/ASM collector. Does not import Torch or initialize CUDA."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "biv150_native_k8_klookahead_sme.cu"
CODEC = HERE / "biv150_native_k8_codec.cuh"
FLAGS = ["-O3", "-std=c++17", "-D__ILUVATAR__", "-D__MR__",
         "-DCOREX_NATIVE_GQA_V_OVERLAP=1", "-x", "ivcore",
         "--cuda-gpu-arch=ivcore11", "--cuda-path=/usr/local/corex",
         "--cuda-device-only"]

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--compiler", default="/usr/local/corex/bin/clang++")
    p.add_argument("--source", type=Path, default=SOURCE)
    args = p.parse_args()
    source = args.source.resolve()
    out = args.out.resolve()
    if not out.is_absolute() or out.exists():
        p.error("--out must be a fresh absolute directory")
    if not source.is_file() or not CODEC.is_file():
        p.error("Run make_variant.py first; both pinned sources must exist")
    if "torch" in sys.modules or "triton" in sys.modules:
        raise RuntimeError("Compile-only collector must not import GPU frameworks")
    out.mkdir(parents=True)
    src_copy, codec_copy = out / source.name, out / CODEC.name
    src_copy.write_bytes(source.read_bytes())
    codec_copy.write_bytes(CODEC.read_bytes())
    compiler = Path(args.compiler)
    version = subprocess.run([str(compiler), "--version"], capture_output=True, text=True)
    (out / "compiler-version.txt").write_text(version.stdout + version.stderr, encoding="utf-8")
    result = {
        "source_sha256": sha(src_copy), "codec_sha256": sha(codec_copy),
        "compiler": str(compiler), "compiler_sha256": sha(compiler), "compiler_version_exit": version.returncode,
        "flags": FLAGS, "cuda_context": "not initialized; Torch not imported",
        "compile_only": True, "artifacts": {}, "commands": [],
        "scope": "single device translation unit instantiating the existing S2/S4 launch wrappers",
        "runtime_executed": False,
    }
    if version.returncode:
        result["error"] = "compiler --version failed"
    else:
        for kind, kind_flags in (("ll", ["-S", "-emit-llvm"]), ("s", ["-S"])):
            target = out / f"klookahead.{kind}"
            command = [str(compiler), *FLAGS, *kind_flags, str(src_copy), "-o", str(target)]
            proc = subprocess.run(command, capture_output=True, text=True)
            (out / f"klookahead.{kind}.stdout.txt").write_text(proc.stdout, encoding="utf-8")
            (out / f"klookahead.{kind}.stderr.txt").write_text(proc.stderr, encoding="utf-8")
            result["commands"].append({"argv": command, "exit_code": proc.returncode})
            if proc.returncode or not target.is_file() or target.stat().st_size == 0:
                result["error"] = f"compile failed: {kind}"
                (out / "compile-summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
                print(json.dumps(result, indent=2))
                return 1
            text = target.read_text(errors="replace")
            lines = text.splitlines()
            wanted = re.compile(r"sme_load_16x1b64|sl_waitcnt|matrix_mad|mma_sync|spill|vgpr|sgpr|register|shared", re.I)
            result["artifacts"][kind] = {
                "path": target.name, "bytes": target.stat().st_size,
                "sha256": sha(target),
                "s2_s4_symbols": [dict(line=i + 1, text=line[:500]) for i, line in enumerate(lines)
                                  if re.search(r"klookahead_gqa_producer.*(?:Li2E|Li4E)|<2>|<4>", line)],
                "instruction_and_resource_evidence": [dict(line=i + 1, text=line[:500])
                                   for i, line in enumerate(lines) if wanted.search(line)],
            }
    result["completed"] = "error" not in result
    result["outputs_sha256"] = {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()}
    (out / "compile-summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["completed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
