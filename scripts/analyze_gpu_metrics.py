#!/usr/bin/env python3
"""Summarize ixsmi samples produced by monitor_gpu.sh."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


def number(value: str) -> float | None:
    token = value.strip().split()[0]
    try:
        return float(token)
    except ValueError:
        return None


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()

    rows = []
    with args.csv.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            parsed = {
                "utilization_gpu": number(row.get("utilization.gpu", "")),
                "utilization_memory": number(row.get("utilization.memory", "")),
                "memory_used_mib": number(row.get("memory.used", "")),
                "temperature_c": number(row.get("temperature.gpu", "")),
                "gpu_power_w": number(row.get("gpu.power.draw", "")),
                "board_power_w": number(row.get("board.power.draw", "")),
            }
            if all(value is not None for value in parsed.values()):
                rows.append(parsed)

    if not rows:
        raise SystemExit("No valid samples")

    print(f"samples={len(rows)}")
    for key in rows[0]:
        values = [float(row[key]) for row in rows]
        print(
            f"{key}: mean={statistics.mean(values):.3f} "
            f"p50={percentile(values, 0.50):.3f} "
            f"p90={percentile(values, 0.90):.3f} "
            f"p99={percentile(values, 0.99):.3f} "
            f"max={max(values):.3f}"
        )
    active = [row for row in rows if row["utilization_gpu"] >= 1]
    print(f"active_sample_fraction={len(active) / len(rows):.4f}")


if __name__ == "__main__":
    main()
