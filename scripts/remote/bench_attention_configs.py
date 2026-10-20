#!/usr/bin/env python3
"""Microbenchmark FlagGems paged FlashAttention tile configurations."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import torch
import flag_gems
from flag_gems import flash_attn_varlen_func
from flag_gems.ops import attention as attention_mod


CANDIDATES = {
    "prefill": [
        (128, 32, 4, 3),
        (128, 64, 4, 2),
        (128, 64, 8, 3),
        (64, 64, 4, 2),
        (64, 128, 8, 2),
        (64, 64, 8, 3),
    ],
    "decode": [
        (8, 32, 2, 2),
        (8, 32, 2, 3),
        (8, 32, 4, 2),
        (8, 64, 2, 2),
        (8, 64, 4, 2),
        (16, 32, 4, 3),
        (16, 64, 4, 2),
        (16, 32, 8, 2),
        (32, 32, 4, 3),
        (32, 64, 4, 2),
        (32, 64, 8, 3),
    ],
}


def make_inputs(batch: int, seq_len: int, phase: str, block_size: int = 16):
    device = torch.device("cuda")
    query_len = seq_len if phase == "prefill" else 1
    num_blocks_per_seq = math.ceil(seq_len / block_size)
    total_pages = batch * num_blocks_per_seq
    q = torch.randn(
        batch * query_len, 16, 128, device=device, dtype=torch.bfloat16
    )
    k_cache = torch.randn(
        total_pages, block_size, 2, 128, device=device, dtype=torch.bfloat16
    )
    v_cache = torch.randn_like(k_cache)
    out = torch.empty_like(q)
    cu_seqlens_q = torch.arange(
        0, (batch + 1) * query_len, query_len, device=device, dtype=torch.int32
    )
    seqused_k = torch.full(
        (batch,), seq_len, device=device, dtype=torch.int32
    )
    block_table = (
        torch.arange(total_pages, device=device, dtype=torch.int32)
        .reshape(batch, num_blocks_per_seq)
    )
    return {
        "q": q,
        "k": k_cache,
        "v": v_cache,
        "out": out,
        "cu_seqlens_q": cu_seqlens_q,
        "seqused_k": seqused_k,
        "block_table": block_table,
        "max_seqlen_q": query_len,
        "max_seqlen_k": seq_len,
    }


def install_config(block_m: int, block_n: int, warps: int, stages: int) -> None:
    cfg = {
        "BLOCK_M": lambda _args: block_m,
        "BLOCK_N": lambda _args: block_n,
        "num_warps": lambda _args: warps,
        "num_stages": lambda _args: stages,
    }
    attention_mod.runtime.get_heuristic_config = lambda _name: cfg


def invoke(inputs: dict, phase: str) -> None:
    flash_attn_varlen_func(
        q=inputs["q"],
        k=inputs["k"],
        v=inputs["v"],
        out=inputs["out"],
        cu_seqlens_q=inputs["cu_seqlens_q"],
        max_seqlen_q=inputs["max_seqlen_q"],
        seqused_k=inputs["seqused_k"],
        max_seqlen_k=inputs["max_seqlen_k"],
        softmax_scale=128 ** -0.5,
        causal=phase == "prefill",
        window_size=(-1, -1),
        block_table=inputs["block_table"],
        fa_version=2,
        num_splits=0,
    )


def measure(inputs: dict, phase: str, warmups: int, repeats: int) -> list[float]:
    for _ in range(warmups):
        invoke(inputs, phase)
    torch.cuda.synchronize()

    times = []
    for _ in range(repeats):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        invoke(inputs, phase)
        end.record()
        end.synchronize()
        times.append(start.elapsed_time(end))
    return times


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=sorted(CANDIDATES), required=True)
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument("--seq-len", type=int, required=True)
    parser.add_argument("--block-size", type=int, default=16)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    print(
        json.dumps(
            {
                "vendor": flag_gems.vendor_name,
                "device": torch.cuda.get_device_name(0),
                "phase": args.phase,
                "batch": args.batch,
                "seq_len": args.seq_len,
                "block_size": args.block_size,
            }
        ),
        flush=True,
    )
    inputs = make_inputs(
        args.batch, args.seq_len, args.phase, block_size=args.block_size
    )
    rows = []
    for block_m, block_n, warps, stages in CANDIDATES[args.phase]:
        row = {
            "block_m": block_m,
            "block_n": block_n,
            "warps": warps,
            "stages": stages,
            "block_size": args.block_size,
            "status": "ok",
            "error": "",
        }
        try:
            install_config(block_m, block_n, warps, stages)
            times = measure(inputs, args.phase, args.warmups, args.repeats)
            row.update(
                {
                    "min_ms": min(times),
                    "median_ms": sorted(times)[len(times) // 2],
                    "mean_ms": sum(times) / len(times),
                }
            )
        except Exception as exc:
            row.update(
                {
                    "status": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                    "min_ms": "",
                    "median_ms": "",
                    "mean_ms": "",
                }
            )
        rows.append(row)
        print(json.dumps(row), flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
