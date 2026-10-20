#!/usr/bin/env python3
"""Extract vLLM engine progress metrics from a service log."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

LINE_RE = re.compile(
    r"(?P<timestamp>\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?"
    r"Avg prompt throughput:\s*(?P<prompt>[\d.]+) tokens/s,\s*"
    r"Avg generation throughput:\s*(?P<generation>[\d.]+) tokens/s,\s*"
    r"Running:\s*(?P<running>\d+) reqs,\s*"
    r"Waiting:\s*(?P<waiting>\d+) reqs,\s*"
    r"GPU KV cache usage:\s*(?P<kv>[\d.]+)%,\s*"
    r"Prefix cache hit rate:\s*(?P<prefix>[\d.]+)%"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--start", help="inclusive timestamp prefix, e.g. 10-21 00:19")
    parser.add_argument("--end", help="inclusive timestamp prefix, e.g. 10-21 00:31")
    args = parser.parse_args()

    rows = []
    for line in args.log.read_text(encoding="utf-8", errors="replace").splitlines():
        match = LINE_RE.search(line)
        if not match:
            continue
        timestamp = match.group("timestamp")
        if args.start and timestamp < args.start:
            continue
        if args.end and timestamp > args.end:
            continue
        rows.append(
            {
                "timestamp": timestamp,
                "prompt_tokens_s": float(match.group("prompt")),
                "generation_tokens_s": float(match.group("generation")),
                "running_requests": int(match.group("running")),
                "waiting_requests": int(match.group("waiting")),
                "kv_cache_percent": float(match.group("kv")),
                "prefix_hit_percent": float(match.group("prefix")),
            }
        )

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [
            "timestamp",
            "prompt_tokens_s",
            "generation_tokens_s",
            "running_requests",
            "waiting_requests",
            "kv_cache_percent",
            "prefix_hit_percent",
        ])
        writer.writeheader()
        writer.writerows(rows)

    prefill_samples = [row for row in rows if row["prompt_tokens_s"] > 0]
    decode_samples = [
        row
        for row in rows
        if row["prompt_tokens_s"] == 0 and row["generation_tokens_s"] > 0
    ]
    print(f"engine_samples={len(rows)}")
    print(f"prefill_phase_samples={len(prefill_samples)}")
    print(f"decode_phase_samples={len(decode_samples)}")
    if prefill_samples:
        print(
            "prefill_tokens_s_mean="
            f"{sum(row['prompt_tokens_s'] for row in prefill_samples) / len(prefill_samples):.2f}"
        )
    if decode_samples:
        print(
            "generation_tokens_s_mean="
            f"{sum(row['generation_tokens_s'] for row in decode_samples) / len(decode_samples):.2f}"
        )
    segments = []
    current = None
    for row in rows:
        if row["prompt_tokens_s"] > 0 and row["generation_tokens_s"] > 0:
            segment = "mixed"
        elif row["prompt_tokens_s"] > 0:
            segment = "prefill"
        elif row["generation_tokens_s"] > 0:
            segment = "decode"
        else:
            segment = "idle"
        if current is None or current["segment"] != segment:
            if current is not None:
                segments.append(current)
            current = {
                "segment": segment,
                "start": row["timestamp"],
                "end": row["timestamp"],
                "samples": 0,
            }
        current["end"] = row["timestamp"]
        current["samples"] += 1
    if current is not None:
        segments.append(current)
    for segment in segments:
        print(
            f"segment={segment['segment']} start={segment['start']} "
            f"end={segment['end']} samples={segment['samples']}"
        )


if __name__ == "__main__":
    main()
