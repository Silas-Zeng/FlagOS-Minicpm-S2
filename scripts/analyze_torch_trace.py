#!/usr/bin/env python3
"""Aggregate PyTorch profiler Chrome traces into operator and kernel summaries."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_trace(path: Path) -> dict[str, Any] | list[dict[str, Any]]:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding="utf-8"))


def classify(category: str, name: str) -> str:
    lowered = f"{category} {name}".lower()
    if "kernel" in lowered or category.lower() in {"kernel", "gpu_kernel"}:
        return "kernel"
    if "gpu" in lowered or "cuda" in lowered:
        return "gpu_other"
    if "cpu_op" in lowered or category == "cpu_op":
        return "cpu_operator"
    if category in {"python_function", "user_annotation"}:
        return "host"
    return "other"


def summarize(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, dict[tuple[str, str], dict[str, Any]]] = {
        "kernel": {},
        "gpu_other": {},
        "cpu_operator": {},
        "host": {},
        "other": {},
    }
    for event in events:
        if event.get("ph") != "X":
            continue
        duration = event.get("dur")
        if not isinstance(duration, (int, float)):
            continue
        category = str(event.get("cat", ""))
        name = str(event.get("name", ""))
        kind = classify(category, name)
        key = (category, name)
        row = groups[kind].setdefault(
            key,
            {
                "category": category,
                "name": name,
                "count": 0,
                "duration_us": 0.0,
                "max_us": 0.0,
                "examples": 0,
            },
        )
        row["count"] += 1
        row["duration_us"] += float(duration)
        row["max_us"] = max(row["max_us"], float(duration))
        if event.get("args"):
            row["examples"] += 1

    result: dict[str, list[dict[str, Any]]] = {}
    for kind, raw in groups.items():
        rows = list(raw.values())
        total = sum(float(row["duration_us"]) for row in rows) or 1.0
        for row in rows:
            row["mean_us"] = row["duration_us"] / row["count"]
            row["share_percent"] = row["duration_us"] / total * 100.0
        rows.sort(key=lambda row: row["duration_us"], reverse=True)
        result[kind] = rows
    return result


def write_csv(path: Path, kind: str, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "kind",
                "rank",
                "category",
                "name",
                "count",
                "duration_us",
                "mean_us",
                "max_us",
                "share_percent",
            ],
        )
        writer.writeheader()
        for rank, row in enumerate(rows, start=1):
            writer.writerow(
                {
                    "kind": kind,
                    "rank": rank,
                    **{key: row[key] for key in (
                        "category",
                        "name",
                        "count",
                        "duration_us",
                        "mean_us",
                        "max_us",
                        "share_percent",
                    )},
                }
            )


def write_markdown(path: Path, summaries: dict[str, list[dict[str, Any]]]) -> None:
    lines = [
        "# PyTorch profiler summary",
        "",
        "Durations are derived from completed `X` events in the Chrome trace.",
        "Shares are within each event class; CPU and device residency can overlap.",
        "",
    ]
    for kind in ("kernel", "gpu_other", "cpu_operator", "host"):
        rows = summaries[kind]
        if not rows:
            continue
        cumulative = 0.0
        lines.extend(
            [
                f"## {kind}",
                "",
                "| Rank | Name | Category | Count | Mean us | Total us | Share |",
                "|---:|---|---|---:|---:|---:|---:|",
            ]
        )
        for rank, row in enumerate(rows[:30], start=1):
            cumulative += float(row["share_percent"])
            lines.append(
                f"| {rank} | `{row['name']}` | {row['category']} | "
                f"{row['count']} | {row['mean_us']:.2f} | "
                f"{row['duration_us']:.2f} | {row['share_percent']:.2f}% |"
            )
        lines.extend(["", f"Top-30 cumulative share: {cumulative:.2f}%.", ""])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    payload = load_trace(args.trace)
    if isinstance(payload, dict):
        events = payload.get("traceEvents", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise SystemExit("unsupported trace payload; expected object or array")
    summaries = summarize(events)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for kind, rows in summaries.items():
        write_csv(args.out_dir / f"{kind}.csv", kind, rows)
    write_markdown(args.out_dir / "summary.md", summaries)


if __name__ == "__main__":
    main()
