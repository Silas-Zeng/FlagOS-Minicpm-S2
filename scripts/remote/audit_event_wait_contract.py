#!/usr/bin/env python3
"""仅读取本实例Event构造/等待契约源；无Torch导入、库加载、编译或设备API。"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys

ROOT = Path("/workspace/experiments/minicpm-s2")
TORCH = Path("/usr/local/lib/python3.12/site-packages/torch")
COREX = Path("/usr/local/corex-4.5.0/include/IX")
# 只访问固定文件，不扫描site-packages或用较新上游源补本实例缺项。
PROBES = [
    (TORCH / "cuda/streams.py", r"class Event|blocking|def synchronize|super\(\)\.__new__", "c8cb35dccf58685a7025a3af1f3082d274b7b13e42cc8b0f4609a0245ee90c7b"),
    (TORCH / "_streambase.py", r"class _EventBase|synchronize|def record|def wait", None),
    (TORCH / "include/torch/csrc/Event.h", r"Event|blocking|synchronize", None),
    (TORCH / "csrc/Event.cpp", r"blocking|EventFlag|synchronize|THPEvent", None),
    (TORCH / "include/torch/csrc/cuda/Event.h", r"Event|blocking|synchronize", None),
    (TORCH / "csrc/cuda/Event.cpp", r"blocking|cudaEventBlockingSync|synchronize|cudaEventSynchronize", None),
    (TORCH / "include/ATen/cuda/CUDAEvent.h", r"CUDAEvent\(|flags_|cudaEventCreateWithFlags|cudaEventSynchronize", None),
    (TORCH / "include/c10/cuda/impl/CUDAGuardImpl.h", r"EventFlag|record\(|synchronizeEvent|cudaEventCreate|cudaEventSynchronize", None),
    (TORCH / "include/c10/core/impl/InlineEvent.h", r"EventFlag|flag_|synchronize|createEvent", None),
    (COREX / "ixrt/driver_types.h", r"ixEventDefault|ixEventBlockingSync|ixEventDisableTiming|ixEventInterprocess", "93c8f434cef524cd2370c003506da3301f55dd022593349122548647b9317069"),
    (COREX / "ixrt/ix_runtime_api.h", r"ixEventCreateWithFlags|ixEventSynchronize|ixEventQuery|ixEventRecord\(", "7dca9b9187cf2f7dda5ff75760ae2d56d04007fb07eacc3c74242b63e6c90a5b"),
    (COREX / "mapping_cudart.h", r"cudaEvent(Default|BlockingSync|DisableTiming|CreateWithFlags|Synchronize|Query|Record)", "ca962a4e5e051a6de6e8c84c89cf6ec9430d8fbb225a78708731b928662984fb"),
]
RUNNER = ROOT / "framework/20261021T214400Z-kv-full-restore-context16k-long-control/plugin-source/vllm_fl/worker/model_runner.py"
RUNNER_SHA = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"


def probe(path, pattern, expected, windows=None):
    item = {"path": str(path), "expected_sha256": expected,
            "equivalent_probe_argv_not_executed": ["rg", "-n", "-C", "6", "-e", pattern, str(path)]}
    if not path.is_file():
        return {**item, "status": "missing", "boundary": "安装包未提供该源；不推断绑定实现。"}
    raw = path.read_bytes()
    item.update(resolved=str(path.resolve()), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    item["expected_identity_matches"] = expected is None or item["sha256"] == expected
    lines = raw.decode("utf-8", errors="replace").splitlines()
    hits = [i for i, line in enumerate(lines) if re.search(pattern, line)]
    ranges = windows or [(max(0, i - 6), min(len(lines), i + 13)) for i in hits[:20]]
    chosen = sorted({i for start, end in ranges for i in range(start, min(end, len(lines)))})
    item.update(status="read_only", matched_lines=len(hits), matches_truncated=windows is None and len(hits) > 20,
                excerpts=[{"line": i + 1, "text": lines[i]} for i in chosen],
                exact_reader="Path.read_bytes; SHA256完整字节；片段行号从1开始；不exec源")
    return item


def main():
    if len(sys.argv) != 1:
        raise ValueError("不接受路径/参数覆盖，只读取固定本实例源")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / "source-audits" / (stamp + "-event-wait-contract")
    output.mkdir(parents=True, exist_ok=False)
    files = [probe(*spec) for spec in PROBES]
    files.append(probe(RUNNER, r"torch.Event|prepare_inputs_event|async_copy_ready_event", RUNNER_SHA,
                       [(304, 352), (748, 763), (3822, 3842), (4155, 4172)]))
    mismatches = [x["path"] for x in files if x.get("expected_identity_matches") is False]
    result = {"run_id": output.name, "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "status": "source_identity_mismatch" if mismatches else "read_only_collection_not_semantic_pass",
              "command": [sys.executable, *sys.argv], "command_shell": shlex.join([sys.executable, *sys.argv]),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "files": files, "identity_mismatches": mismatches,
              "missing_paths": [x["path"] for x in files if x["status"] == "missing"],
              "limits_zh": ["只读实际安装源与已有e155归档，不导入Torch、加载库、编译或调用设备API。",
                            "generic torch.Event与torch.cuda.Event必须分别跟踪；缺绑定源不假定其blocking参数相同。",
                            "头文件/声明只证明可得契约，不证明Corex真实等待会睡眠或其性能。",
                            "既有event记录后不能换event；所有SDK/device probe均未执行。"]}
    with (output / "result.json").open("x", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(json.dumps({"output": str(output), "status": result["status"], "missing": len(result["missing_paths"])}))
    return 2 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
