#!/usr/bin/env python3
"""只读三个精确 Triton cache 条目和已安装源码；无运行时导入/编译/GPU。

必须在设备作业结束后执行，持同一实验锁。不会递归扫描 cache 根目录，
只尝试三条已知完整hash对应的hex/base32目录，缺项记录为证据不足。
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path("/workspace/experiments/minicpm-s2")
HASHES = {
    "service_original": "23d5fd23898e6eecfef38a539119ea5fd5e8f41ebc68639dc48b0685e0b69a51",
    "gate_baseline": "3639b8c97b8a4342970c3964dbabb29a1242f519fa9ad59761253a59d4346b5a",
    "gate_and_service_group8": "08afb5451fca98d698022dd9770db694d9e3786dbf3e4215e1a660a8b8e8305f",
}
SOURCES = ("__init__.py", "runtime/jit.py", "compiler/compiler.py", "runtime/cache.py",
           "runtime/autotuner.py", "backends/iluvatar/compiler.py", "backends/nvidia/compiler.py",
           "spec/iluvatar/triton/compiler/compiler.py", "spec/iluvatar/triton/runtime/jit.py",
           "spec/iluvatar/triton/runtime/cache.py", "spec/iluvatar/triton/runtime/autotuner.py",
           "spec/iluvatar/triton/backends/iluvatar/compiler.py")


def snapshot(source, target):
    before = source.stat()
    if source.is_symlink() or not source.is_file() or before.st_size > 64 * 1024 * 1024:
        return {"source": str(source), "status": "skipped_symlink_nonregular_or_over64MiB"}
    raw = source.read_bytes()
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError("证据文件在读取时改变：" + str(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(raw)
    return {"source": str(source), "status": "copied", "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache-root", type=Path,
                        default=Path(os.environ.get("TRITON_CACHE_DIR", "/root/.triton/cache")))
    parser.add_argument("--triton-source", type=Path,
                        default=Path("/usr/local/lib/python3.12/site-packages/triton"))
    args = parser.parse_args()
    import fcntl
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError("证据输出必须全新")
    output = args.output.resolve()
    if output.parent != (ROOT / "source-audits").resolve():
        raise ValueError("输出必须是本实验source-audits下新直接子目录")
    with (ROOT / "framework-device.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        output.mkdir(parents=True, exist_ok=False)
        result = {"created_utc": datetime.now(timezone.utc).isoformat(),
                  "kind": "CPU file evidence only; no runtime imports/compile/GPU/cache-root scan",
                  "command": [sys.executable, *sys.argv], "cache_root": str(args.cache_root),
                  "triton_source": str(args.triton_source), "sources": {}, "entries": {}}
        result["collector"] = snapshot(Path(__file__), output / "collector.py")
        for relative in SOURCES:
            path = args.triton_source / relative
            result["sources"][relative] = snapshot(path, output / "installed-triton" / relative) if path.exists() else {"status": "missing"}
        for role, key in HASHES.items():
            encoded = base64.b32encode(bytes.fromhex(key)).decode("ascii").rstrip("=")
            record = {"compiled_hash": key, "attempted_directories": [], "directories": {}}
            for name in (encoded, key):
                path = args.cache_root / name
                record["attempted_directories"].append(str(path))
                if not path.is_dir() or path.is_symlink():
                    continue
                # 只读精确条目直接子文件；不跟随group JSON中的外部路径。
                record["directories"][name] = {
                    entry.name: snapshot(entry, output / "cache" / role / name / entry.name)
                    for entry in sorted(path.iterdir()) if entry.is_file() and not entry.is_symlink()}
            record["found"] = bool(record["directories"])
            result["entries"][role] = record
        result["status"] = ("evidence_copied_not_a_kernel_equivalence_claim"
                            if all(record["found"] for record in result["entries"].values())
                            else "evidence_incomplete_cache_entries_missing")
        (output / "manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": result["status"], "output": str(output),
                          "entries_found": {role: record["found"] for role, record in result["entries"].items()}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
