#!/usr/bin/env python3
"""Summarize official vLLM benchmark CSV files without changing measurements."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

METRICS = {
    "Benchmark Duration (s)": "duration_s",
    "Req/s": "request_throughput",
    "Output tok/s": "output_throughput",
    "Total tok/s": "total_throughput",
    "Mean TTFT (ms)": "mean_ttft_ms",
    "Median TTFT (ms)": "median_ttft_ms",
    "P99 TTFT (ms)": "p99_ttft_ms",
    "Mean TPOT (ms)": "mean_tpot_ms",
    "Median TPOT (ms)": "median_tpot_ms",
    "P99 TPOT (ms)": "p99_tpot_ms",
    "Mean ITL (ms)": "mean_itl_ms",
    "Median ITL (ms)": "median_itl_ms",
    "P99 ITL (ms)": "p99_itl_ms",
    "Total Input Tokens": "total_input_tokens",
    "Total Output Tokens": "total_output_tokens",
}


def as_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalize(row: dict[str, str]) -> dict[str, float | int | str | None]:
    result: dict[str, float | int | str | None] = {
        "prefill_tokens": int(float(row["Prefill"])),
        "decode_tokens": int(float(row["Decode"])),
        "concurrency": int(float(row["Conc"])),
        "num_prompts": int(float(row["Num Prompts"])),
    }
    for source, target in METRICS.items():
        result[target] = as_float(row.get(source))

    ttft = result["mean_ttft_ms"]
    tpot = result["mean_tpot_ms"]
    decode_tokens = result["decode_tokens"]
    if isinstance(ttft, float) and isinstance(tpot, float) and isinstance(decode_tokens, int):
        decode_ms = max(decode_tokens - 1, 1) * tpot
        total_ms = ttft + decode_ms
        result["estimated_decode_ms"] = decode_ms
        result["estimated_request_ms"] = total_ms
        result["estimated_ttft_share"] = ttft / total_ms if total_ms else None
        result["estimated_decode_share"] = decode_ms / total_ms if total_ms else None
    return result


def valid_raw_rows(rows: list[dict[str, str]]) -> list[dict[str, float | int | str | None]]:
    normalized = [normalize(row) for row in rows]
    by_case: dict[tuple[int, int, int, int], list[dict[str, float | int | str | None]]] = {}
    for row in normalized:
        key = (
            row["prefill_tokens"],
            row["decode_tokens"],
            row["concurrency"],
            row["num_prompts"],
        )
        by_case.setdefault(key, []).append(row)

    result: list[dict[str, float | int | str | None]] = []
    for group in by_case.values():
        # Apply SKIP_FIRST to original positions, including a failed warmup.
        successes = [
            row
            for row in group[1:]
            if row.get("total_throughput") is not None
            and row.get("total_output_tokens") == row.get("decode_tokens") * row.get("num_prompts")
        ]
        result.extend(successes)
    return result


def pct_variation(values: list[float]) -> float | None:
    if len(values) < 2 or statistics.mean(values) == 0:
        return None
    return statistics.pstdev(values) / statistics.mean(values) * 100.0


def markdown(
    raw_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> str:
    valid = valid_raw_rows(raw_rows)
    summaries = [normalize(row) for row in summary_rows]
    lines = [
        "# Official benchmark analysis",
        "",
        "Generated from the unmodified official summary/raw CSV files.",
        "",
        "The official script uses `RUNS=4` and `SKIP_FIRST=1`; variation below uses",
        "usable rows after removing each case's original first row. Fewer than",
        "three retained rows is incomplete, not a complete official result.",
        "This summary helper does not replace `run_official_gate.py` validation.",
        "",
        "## Summary",
        "",
        "| Case | Total tok/s | Output tok/s | Mean TTFT ms | Mean TPOT ms | Duration s |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            "| {prefill_tokens}/{decode_tokens} c{concurrency} | "
            "{total_throughput:.2f} | {output_throughput:.2f} | "
            "{mean_ttft_ms:.2f} | {mean_tpot_ms:.2f} | {duration_s:.2f} |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Mean-request latency approximation",
            "",
            "Estimated request latency is `Mean TTFT + (output_len - 1) * Mean TPOT`.",
            "This removes batch queuing from the denominator and is a diagnostic proxy,",
            "not a replacement for an engine timeline.",
            "",
            "| Case | Estimated request ms | TTFT share | Decode share |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in summaries:
        lines.append(
            "| {prefill_tokens}/{decode_tokens} c{concurrency} | "
            "{estimated_request_ms:.2f} | {estimated_ttft_share:.2%} | "
            "{estimated_decode_share:.2%} |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Run-to-run variation",
            "",
            "| Case | Usable retained rows | CV total tok/s | CV TTFT | CV TPOT |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in summaries:
        key = (
            row["prefill_tokens"],
            row["decode_tokens"],
            row["concurrency"],
            row["num_prompts"],
        )
        matching = [
            item
            for item in valid
            if (
                item["prefill_tokens"],
                item["decode_tokens"],
                item["concurrency"],
                item["num_prompts"],
            )
            == key
        ]
        totals = [float(item["total_throughput"]) for item in matching]
        ttfts = [float(item["mean_ttft_ms"]) for item in matching]
        tpots = [float(item["mean_tpot_ms"]) for item in matching]
        cv_total = pct_variation(totals)
        cv_ttft = pct_variation(ttfts)
        cv_tpot = pct_variation(tpots)
        def display_cv(value):
            return "N/A" if value is None else f"{value:.2f}%"
        lines.append(
            f"| {row['prefill_tokens']}/{row['decode_tokens']} c{row['concurrency']} | "
            f"{len(matching)} | "
            f"{display_cv(cv_total)} | {display_cv(cv_ttft)} | {display_cv(cv_tpot)} |"
        )
        if len(matching) != 3:
            lines.extend(["", f"Incomplete retained coverage for {row['prefill_tokens']}/"
                          f"{row['decode_tokens']} c{row['concurrency']}: "
                          f"expected 3 usable retained rows, found {len(matching)}.", ""])

    lines.extend(
        [
            "",
            "## Interpretation limits",
            "",
            "- TTFT includes queuing and does not isolate prefill kernel time.",
            "- The latency approximation is based on mean values and does not model",
            "  continuous batching overlap.",
            "- Kernel-level conclusions require a separate profiler trace.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    raw_rows = read_rows(args.raw)
    summary_rows = read_rows(args.summary)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown(raw_rows, summary_rows), encoding="utf-8")

    if args.json_out:
        payload = {
            "summary": [normalize(row) for row in summary_rows],
            "valid_raw": valid_raw_rows(raw_rows),
        }
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
