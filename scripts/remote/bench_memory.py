#!/usr/bin/env python3
"""Measure basic BF16 device copy and read bandwidth."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

import torch


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
    parser.add_argument("--bytes", type=int, default=512 * 1024 * 1024)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()

    elements = args.bytes // 2
    source = torch.randn(elements, device="cuda", dtype=torch.bfloat16)
    destination = torch.empty_like(source)
    operations = {
        "copy": (lambda: destination.copy_(source), 2 * args.bytes),
        "fill": (lambda: destination.fill_(1.0), args.bytes),
    }
    rows = []
    for name, (fn, bytes_moved) in operations.items():
        times = elapsed_ms(fn, args.warmups, args.repeats)
        median_ms = statistics.median(times)
        rows.append(
            {
                "operation": name,
                "bytes": bytes_moved,
                "median_ms": f"{median_ms:.6f}",
                "min_ms": f"{min(times):.6f}",
                "max_ms": f"{max(times):.6f}",
                "effective_gbps": f"{bytes_moved / (median_ms / 1000) / 1e9:.6f}",
            }
        )
        print(rows[-1], flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
