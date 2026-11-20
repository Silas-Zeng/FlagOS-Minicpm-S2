#!/usr/bin/env python3
"""Explicit GPU stage-layout equality check; importing this module does no GPU work."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE_BYTES = 16384
GUARD = 256
STAGE_BYTES = 2048
PAGES = 4  # legal coverage pages 0 and 3


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def k_i8_index(slot: int, dim: int) -> int:
    panel, within = divmod(dim, 64)
    quartet, byte = divmod(within, 4)
    bank, subslot = divmod(slot, 4)
    return (panel * 1024 + bank * 256 + (quartet % 4) * 64 +
            ((quartet // 4) ^ bank) * 16 + subslot * 4 + byte)


def make_values(pattern: str, seed: int):
    import torch
    if pattern == "zero":
        return torch.zeros((16, 128), dtype=torch.int8)
    if pattern == "minus127":
        return torch.full((16, 128), -127, dtype=torch.int8)
    if pattern == "plus127":
        return torch.full((16, 128), 127, dtype=torch.int8)
    gen = torch.Generator(device="cpu").manual_seed(seed)
    return torch.randint(-128, 128, (16, 128), dtype=torch.int16,
                         generator=gen).to(torch.int8)


def put_page_head(cpu: object, page: int, head: int, values: object) -> None:
    start_page = GUARD + page * PAGE_BYTES + head * 128
    raw = values.contiguous().view(__import__("torch").uint8)
    for slot in range(16):
        start = start_page + slot * 256
        cpu[start:start + 128] = raw[slot]


def expected_stage(cpu: object, page: int, head: int) -> bytes:
    import torch
    key = cpu[GUARD + page * PAGE_BYTES + head * 128:
              GUARD + page * PAGE_BYTES + head * 128 + 16 * 256]
    # The 16 x 128B view has a 256B row pitch; reproduce the established
    # NativeK8 swizzle into the 2KiB stage image.
    out = bytearray(STAGE_BYTES)
    for slot in range(16):
        for dim in range(128):
            src = slot * 256 + dim
            out[k_i8_index(slot, dim)] = int(key[src])
    return bytes(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, default=HERE / "build/libnative_k8_sme_probe.so")
    parser.add_argument("--output", type=Path, default=HERE / "build/probe-result.json")
    args = parser.parse_args()
    lib_path = args.library.resolve()
    if not lib_path.is_file():
        raise SystemExit(f"missing shared library: {lib_path}; run build.sh explicitly first")

    # Deliberately delayed until explicit runner invocation.
    import torch

    if not torch.cuda.is_available():
        raise SystemExit("CUDA/CoreX device unavailable; no cases launched")
    device = torch.device("cuda", torch.cuda.current_device())
    lib = ctypes.CDLL(str(lib_path))
    fn_sig = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint,
              ctypes.c_void_p, ctypes.c_void_p]
    launch_a = lib.launch_k_i8_copy_probe
    launch_b = lib.launch_k_i8_sme_probe
    launch_a.argtypes = fn_sig
    launch_b.argtypes = fn_sig
    launch_a.restype = None
    launch_b.restype = None

    patterns = ("zero", "minus127", "plus127", "random")
    cases = [(pattern, page, head)
             for pattern in patterns for page in (0, PAGES - 1) for head in (0, 1)]
    records = []
    env = {
        "utc_start": datetime.now(timezone.utc).isoformat(),
        "argv": sys.argv,
        "cwd": os.getcwd(),
        "platform": platform.platform(),
        "python": sys.version,
        "torch": torch.__version__,
        "torch_cuda_version": torch.version.cuda,
        "device": torch.cuda.get_device_name(device),
        "device_index": torch.cuda.current_device(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "source_sha256": sha256(HERE / "native_k8_sme_probe.cu"),
        "library_sha256": sha256(lib_path),
        "build_command": (HERE / "build/build-command.txt").read_text().strip()
                          if (HERE / "build/build-command.txt").exists() else None,
        "page_bytes": PAGE_BYTES,
        "guard_bytes": GUARD,
        "stage_bytes": STAGE_BYTES,
        "partial_page_coverage": False,
    }

    for case_id, (pattern, page, head) in enumerate(cases):
        cpu = torch.full((GUARD + PAGES * PAGE_BYTES + GUARD,), 0x5A,
                         dtype=torch.uint8)
        values = make_values(pattern, 0xC0A5 + case_id)
        put_page_head(cpu, page, head, values)
        before = cpu.clone()
        key_gpu = cpu.to(device)
        key_ptr = key_gpu.data_ptr() + GUARD

        output_a = torch.full((GUARD + STAGE_BYTES + GUARD,), 0xA5,
                              dtype=torch.uint8, device=device)
        output_b = torch.full((GUARD + STAGE_BYTES + GUARD,), 0xA5,
                              dtype=torch.uint8, device=device)
        stream = ctypes.c_void_p(torch.cuda.current_stream(device).cuda_stream)
        out_a_ptr = output_a.data_ptr() + GUARD
        out_b_ptr = output_b.data_ptr() + GUARD

        launch_a(ctypes.c_void_p(key_ptr), page, head,
                 ctypes.c_void_p(out_a_ptr), stream)
        torch.cuda.synchronize(device)
        launch_b(ctypes.c_void_p(key_ptr), page, head,
                 ctypes.c_void_p(out_b_ptr), stream)
        torch.cuda.synchronize(device)

        result_a = output_a.cpu()
        result_b = output_b.cpu()
        input_after = key_gpu.cpu()
        pre_a = result_a[:GUARD]
        post_a = result_a[GUARD + STAGE_BYTES:]
        pre_b = result_b[:GUARD]
        post_b = result_b[GUARD + STAGE_BYTES:]
        stage_a = bytes(result_a[GUARD:GUARD + STAGE_BYTES].tolist())
        stage_b = bytes(result_b[GUARD:GUARD + STAGE_BYTES].tolist())
        expected = expected_stage(before, page, head)

        checks = {
            "A_matches_CPU_reference": stage_a == expected,
            "B_matches_A_bytewise": stage_b == stage_a,
            "B_matches_CPU_reference": stage_b == expected,
            "input_immutable": torch.equal(input_after, before),
            "A_output_guards": bool(torch.all(pre_a == 0xA5) and torch.all(post_a == 0xA5)),
            "B_output_guards": bool(torch.all(pre_b == 0xA5) and torch.all(post_b == 0xA5)),
        }
        record = {
            "case": case_id,
            "pattern": pattern,
            "page": page,
            "head": head,
            "checks": checks,
            "stage_a_sha256": hashlib.sha256(stage_a).hexdigest(),
            "stage_b_sha256": hashlib.sha256(stage_b).hexdigest(),
            "equal_bytes": sum(a == b for a, b in zip(stage_a, stage_b)),
            "bytes": STAGE_BYTES,
        }
        records.append(record)
        if not all(checks.values()):
            payload = {"environment": env, "status": "FAIL_STOP", "cases": records,
                       "failure_case": case_id}
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(record, ensure_ascii=False))
            return 1
        print(json.dumps(record, ensure_ascii=False))

    payload = {"environment": env, "status": "PASS", "case_count": len(records),
               "cases": records,
               "utc_end": datetime.now(timezone.utc).isoformat(),
               "claim_limit": "layout bytes only; no attention correctness or performance claim"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
