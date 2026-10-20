#!/usr/bin/env python3
"""Measure BF16 linear-layer latency for MiniCPM decode token counts."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

import torch
import torch.nn.functional as F


SHAPES = {
    "qkv_proj": (2048, 2560),
    "o_proj": (2048, 2048),
    "gate_up_proj": (2048, 12288),
    "down_proj": (6144, 2048),
}


def elapsed_ms(fn, warmups: int, repeats: int) -> list[float]:
    for _ in range(warmups):
        fn()
    torch.cuda.synchronize()

    times = []
    for _ in range(repeats):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        fn()
        end.record()
        end.synchronize()
        times.append(start.elapsed_time(end))
    return times


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()

    device = torch.device("cuda")
    torch.cuda.set_device(0)
    rows = []

    for name, (k, n) in SHAPES.items():
        weight = torch.randn((n, k), device=device, dtype=torch.bfloat16)
        weight_bytes = weight.numel() * weight.element_size()
        for m in (1, 8, 16, 32, 64, 128, 256):
            x = torch.randn((m, k), device=device, dtype=torch.bfloat16)
            times = elapsed_ms(
                lambda: F.linear(x, weight),
                warmups=args.warmups,
                repeats=args.repeats,
            )
            median_ms = statistics.median(times)
            seconds = median_ms / 1000.0
            row = {
                "operator": name,
                "m": m,
                "k": k,
                "n": n,
                "dtype": "bfloat16",
                "median_ms": f"{median_ms:.6f}",
                "min_ms": f"{min(times):.6f}",
                "max_ms": f"{max(times):.6f}",
                "gflops": f"{(2 * m * k * n) / seconds / 1e9:.6f}",
                "weight_gbps": f"{weight_bytes / seconds / 1e9:.6f}",
                "status": "ok",
            }
            rows.append(row)
            print(row, flush=True)
        del weight
        torch.cuda.empty_cache()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
