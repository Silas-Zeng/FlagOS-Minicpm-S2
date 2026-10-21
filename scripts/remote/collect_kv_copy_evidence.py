#!/usr/bin/env python3
"""只读安装源码/已完成服务证据，供独立KV保存恢复门设计；禁止导入框架。"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import stat
import sys

ROOT = Path("/workspace/experiments/minicpm-s2")
SITE = Path("/usr/local/lib/python3.12/site-packages")
# 新增最小依赖：执行器/worker归属、真实KV布局、复制入口与完成ack数据结构。
NEW_SOURCES = (
    "vllm/v1/executor/abstract.py",
    "vllm/v1/executor/uniproc_executor.py",
    "vllm/v1/worker/gpu_worker.py",
    "vllm/v1/worker/gpu_model_runner.py",
    "vllm/v1/worker/kv_connector_model_runner_mixin.py",
    "vllm/distributed/kv_transfer/kv_connector/utils.py",
    "vllm/v1/outputs.py",
    "vllm/v1/worker/gpu/attn_utils.py",
    "vllm/v1/attention/backends/triton_attn.py",
    "vllm/v1/kv_cache_interface.py",
)
KNOWN = {
    "vllm/v1/engine/core.py": "27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71",
    "vllm/v1/core/sched/scheduler.py": "df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090",
    "vllm/v1/core/kv_cache_manager.py": "2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320",
}
RUN_FILES = ("manifest.json", "launch-command.json", "load-commands.json", "server.log",
             "postflight-full.json", "cpu-final.json", "gpu.csv", "finished-at.txt", "exit-code")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_optional(path):
    try:
        return {"path": str(path), "text": path.read_text(encoding="utf-8")}
    except OSError as error:
        return {"path": str(path), "unavailable": type(error).__name__}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="新的ROOT/source-audits直接子目录")
    parser.add_argument("--serve-run", type=Path, required=True, help="已完成exit0的ROOT/framework直接子目录")
    args = parser.parse_args()
    root, output, run = ROOT.resolve(), args.output.resolve(), args.serve_run.resolve()
    if (args.output.exists() or args.output.is_symlink()
            or output.parent != root / "source-audits" or run.parent != root / "framework"
            or not re.fullmatch(r"\d{8}T\d{6}Z-[a-z0-9-]+", output.name)
            or not re.fullmatch(r"\d{8}T\d{6}Z-[a-z0-9-]+", run.name)):
        raise ValueError("要求已完成服务目录及全新直接source-audits子目录")
    if (run / "exit-code").read_text().strip() != "0":
        raise RuntimeError("仅在原服务exit0后采集，不打断在途任务")
    post = json.loads((run / "postflight-full.json").read_text())
    if not all(post["ports_closed"].values()) or post["query"].strip() != "68, 0":
        raise RuntimeError("原服务封存未证明idle；本脚本不探测或操作设备")
    output.mkdir(exist_ok=False)
    manifest = {"utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
                "kind": "stdlib filesystem reads only; no framework imports, subprocesses or device API",
                "serve_run": str(run), "source_files": {}, "run_files": {}, "missing_sources": [],
                "known_source_mismatches": [], "runtime_python_types": "unobserved",
                "tensor_layout": "unobserved; derive candidate layouts from exact sources, validate actual descriptor before gate",
                "limitations": ["源码AST类名不是运行对象类型。日志相同PID前缀不证明同线程/stream。",
                                "postflight是已保存证据，非本脚本实时设备查询；owner仍负责设备互斥。",
                                "PCIe sysfs为协商链路信息，不能当有效带宽或DMA并发实测。"]}
    for relative in (*NEW_SOURCES, *KNOWN):
        path = SITE / relative
        try:
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(SITE.resolve()) or not resolved.is_file():
                raise ValueError("源码必须解析为site-packages内部regular file")
            raw = resolved.read_bytes()
        except FileNotFoundError:
            manifest["missing_sources"].append(relative)
            continue
        if len(raw) > 5 * 1024 * 1024:
            raise ValueError("源码超过预期大小：" + relative)
        destination = output / "source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        tree = ast.parse(raw, filename=relative)
        classes = [{"name": node.name, "bases": [ast.unparse(base) for base in node.bases],
                    "line": node.lineno} for node in tree.body if isinstance(node, ast.ClassDef)]
        metadata = resolved.stat()
        manifest["source_files"][relative] = {"path": str(path), "resolved": str(resolved),
            "was_symlink": path.is_symlink(), "bytes": len(raw), "sha256": sha(raw),
            "mode": oct(stat.S_IMODE(metadata.st_mode)), "mtime_ns": metadata.st_mtime_ns,
            "static_top_level_classes_not_runtime_types": classes}
        if relative in KNOWN and sha(raw) != KNOWN[relative]:
            manifest["known_source_mismatches"].append(relative)
    for filename in RUN_FILES:
        raw = (run / filename).read_bytes()
        destination = output / "serve-evidence" / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        manifest["run_files"][filename] = {"bytes": len(raw), "sha256": sha(raw)}
    log = (run / "server.log").read_text(errors="replace")
    manifest["type_related_log_lines_not_object_introspection"] = [line for line in log.splitlines()
        if any(word in line for word in ("executor", "Executor", "worker_cls", "Using Triton",
                                        "Attention backend", "Asynchronous scheduling", "GPU KV cache size"))]
    manifest["memory"] = [read_optional(Path(path)) for path in (
        "/sys/fs/cgroup/memory.current", "/sys/fs/cgroup/memory.max",
        "/sys/fs/cgroup/memory/memory.usage_in_bytes", "/sys/fs/cgroup/memory/memory.limit_in_bytes",
        "/proc/sys/vm/max_map_count")]
    pci = Path("/sys/bus/pci/devices/0000:16:00.0")
    manifest["pcie"] = [read_optional(pci / name) for name in (
        "current_link_speed", "current_link_width", "max_link_speed", "max_link_width", "numa_node")]
    own = Path(__file__).read_bytes()
    (output / "collector.py").write_bytes(own)
    manifest["collector_sha256"] = sha(own)
    manifest["status"] = "source_capture_complete_runtime_types_unobserved" if not (
        manifest["missing_sources"] or manifest["known_source_mismatches"]) else "source_capture_incomplete"
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "output": str(output),
                      "sources": len(manifest["source_files"]), "missing": manifest["missing_sources"],
                      "mismatches": manifest["known_source_mismatches"],
                      "runtime_python_types": "unobserved"}, ensure_ascii=False))
    return 0 if manifest["status"].startswith("source_capture_complete") else 2


if __name__ == "__main__":
    raise SystemExit(main())
