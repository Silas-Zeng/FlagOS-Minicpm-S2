#!/usr/bin/env python3
"""Compile A/B isolated Torch dispatcher SOs only; never calls an operator or initializes a GPU."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"
CUDA_FLAGS = ["-O3", "-std=c++17", "-D__ILUVATAR__", "-D__MR__",
              "-DCOREX_NATIVE_GQA_V_OVERLAP=1", "-x", "ivcore",
              "--cuda-gpu-arch=ivcore11", "--cuda-path=/usr/local/corex"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=SOURCES)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cxx", default="/usr/local/corex/bin/clang++")
    args = parser.parse_args()
    sources = args.sources.resolve()
    if not args.out.is_absolute():
        parser.error("--out must be an absolute path")
    out = args.out.resolve()
    if out.exists():
        parser.error("--out must be a fresh absolute path")
    manifest_path = sources / "dispatcher-source-manifest.json"
    if not manifest_path.is_file():
        parser.error("prepared sources missing; run prepare_dispatcher_pair.py first")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = sorted(p for p in sources.iterdir() if p.is_file() and p.name != manifest_path.name)
    source_identity = {p.name: sha(p) for p in files}
    for arm in ("A", "B"):
        suffix = arm.lower()
        pinned = manifest["arms"][arm]
        for key, name in (("host_sha256", f"dispatcher_{suffix}.cpp"),
                          ("codec_sha256", f"codec_{suffix}.cu"),
                          ("producer_sha256", f"producer_{suffix}.cu")):
            if source_identity.get(name) != pinned[key]:
                raise SystemExit(f"Source drift: {name}")
    if source_identity.get("biv150_native_k8_codec.cuh") != manifest["inputs"]["header"]["sha256"]:
        raise SystemExit("Pinned codec header drift")
    if {"torch", "triton"}.intersection(sys.modules):
        raise SystemExit("Build entry must start without torch/triton already imported")
    out.mkdir(parents=True)
    (out / "prepared-source-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = {"compile_only": True, "operator_called": False, "gpu_initialized": False,
              "sources": source_identity, "source_manifest_sha256": sha(manifest_path),
              "torch_cuda_arch_list": "7.1", "cuda_flags": CUDA_FLAGS, "arms": {}, "completed": False}
    result["build_invocation"] = ["python", str(Path(__file__).resolve()), "--sources", str(sources),
                                  "--out", str(out), "--cxx", str(args.cxx)]
    try:
        os.environ["CXX"] = args.cxx
        os.environ["MAX_JOBS"] = "1"
        os.environ["TORCH_CUDA_ARCH_LIST"] = "7.1"
        import torch
        from torch.utils.cpp_extension import load
        result["torch"] = {"version": torch.__version__, "file": torch.__file__,
                           "cuda_initialized_before": torch.cuda.is_initialized()}
        cxx_path = Path(args.cxx)
        if cxx_path.is_file():
            version = subprocess.run([str(cxx_path), "--version"], capture_output=True, text=True)
            result["compiler"] = {"path": str(cxx_path.resolve()), "sha256": sha(cxx_path),
                                  "version": (version.stdout + version.stderr).strip(),
                                  "version_exit_code": version.returncode}
        if result["torch"]["cuda_initialized_before"]:
            raise RuntimeError("Refusing build: CUDA context already initialized")
        for arm in ("A", "B"):
            suffix = arm.lower()
            ext_name = f"cjj_native_k8_klookahead_probe_{suffix}"
            build_dir = out / "build" / arm
            build_dir.mkdir(parents=True)
            source_paths = [sources / f"dispatcher_{suffix}.cpp",
                            sources / f"producer_{suffix}.cu",
                            sources / f"codec_{suffix}.cu"]
            if any(not p.is_file() for p in source_paths):
                raise RuntimeError(f"Missing source file for {arm}")
            # Matches tools/build_biv150_native_gqa.py: same CoreX architecture,
            # Torch frontend, and no production registration or operator invocation.
            library = Path(load(name=ext_name, sources=list(map(str, source_paths)),
                               build_directory=str(build_dir), extra_cflags=["-O3", "-std=c++17"],
                               extra_cuda_cflags=CUDA_FLAGS, is_python_module=False, verbose=True)).resolve()
            if not library.is_file() or not library.stat().st_size:
                raise RuntimeError(f"Torch frontend did not emit {arm} SO")
            final = out / f"libnative_k8_sme_dispatch_{arm}.so"
            shutil.copy2(library, final)
            ninja_file = build_dir / "build.ninja"
            ninja_commands = []
            if ninja_file.is_file():
                for line in ninja_file.read_text(encoding="utf-8", errors="replace").splitlines():
                    match = re.match(r"\s*command\s*=\s*(.*)$", line)
                    if match:
                        ninja_commands.append(match.group(1))
            result["arms"][arm] = {"extension_name": ext_name,
                                   "sources": [p.name for p in source_paths],
                                   "source_sha256": {p.name: sha(p) for p in source_paths},
                                   "torch_build_library": str(library),
                                   "library": final.name, "library_sha256": sha(final),
                                   "build_ninja": str(ninja_file),
                                   "build_ninja_sha256": sha(ninja_file) if ninja_file.is_file() else None,
                                   "build_commands": ninja_commands}
        result["torch"]["cuda_initialized_after"] = torch.cuda.is_initialized()
        if result["torch"]["cuda_initialized_after"]:
            raise RuntimeError("Unexpected CUDA context initialization during compile-only")
        result["completed"] = True
    except Exception as exc:
        result["error"] = repr(exc)
        (out / "failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
    result["artifacts"] = [{"path": p.relative_to(out).as_posix(), "bytes": p.stat().st_size,
                            "sha256": sha(p)} for p in sorted(out.rglob("*")) if p.is_file()]
    (out / "dispatcher-build-summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
