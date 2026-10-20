#!/usr/bin/env python3
"""Benchmark generic TRITON_ATTN launch tiles for the MiniCPM prefill shape."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path

import torch

import vllm.v1.attention.ops.triton_unified_attention as attention
from vllm.v1.attention.ops.triton_unified_attention import unified_attention
from vllm.v1.kv_cache_interface import KVQuantMode


CANDIDATES = [
    (16, 32, 4, 3),
    (128, 32, 4, 1),
    (128, 32, 8, 1),
    (128, 64, 4, 1),
    (128, 64, 8, 1),
    (128, 64, 8, 2),
    (128, 64, 8, 3),
    (128, 128, 8, 1),
    (256, 32, 8, 1),
    (256, 64, 8, 1),
    (256, 128, 8, 1),
]

CANDIDATES_DECODE = [
    (16, 16, 4, 3),
    (8, 16, 4, 1),
    (8, 16, 4, 3),
    (8, 32, 4, 1),
    (8, 32, 4, 2),
    (8, 32, 4, 3),
    (8, 64, 4, 1),
    (8, 64, 4, 2),
    (8, 64, 8, 1),
    (16, 32, 4, 1),
    (16, 64, 8, 1),
]


def make_inputs(
    batch: int, query_len: int, kv_len: int, block_size: int
) -> dict[str, torch.Tensor | int]:
    device = torch.device("cuda")
    num_blocks_per_seq = math.ceil(kv_len / block_size)
    total_blocks = batch * num_blocks_per_seq
    query = torch.randn(
        (batch * query_len, 16, 128), device=device, dtype=torch.bfloat16
    )
    key = torch.randn(
        (total_blocks, block_size, 2, 128),
        device=device,
        dtype=torch.bfloat16,
    )
    value = torch.randn_like(key)
    output = torch.empty_like(query)
    query_lens = torch.full(
        (batch,), query_len, device=device, dtype=torch.int32
    )
    cu_query_lens = torch.cat(
        [
            torch.zeros((1,), device=device, dtype=torch.int32),
            torch.cumsum(query_lens, dim=0, dtype=torch.int32),
        ]
    )
    kv_lens = torch.full((batch,), kv_len, device=device, dtype=torch.int32)
    block_table = torch.arange(
        total_blocks, device=device, dtype=torch.int32
    ).reshape(batch, num_blocks_per_seq)
    inputs: dict[str, torch.Tensor | int | None] = {
        "q": query,
        "k": key,
        "v": value,
        "out": output,
        "cu_seqlens_q": cu_query_lens,
        "seqused_k": kv_lens,
        "max_seqlen_q": query_len,
        "max_seqlen_k": kv_len,
        "block_table": block_table,
    }
    if query_len == 1:
        seq_threshold = 64
        segments = 16
        inputs.update(
            {
                "seq_threshold_3D": seq_threshold,
                "num_par_softmax_segments": segments,
                "softmax_segm_output": torch.empty(
                    (seq_threshold, 16, segments, 128),
                    device=device,
                    dtype=torch.float32,
                ),
                "softmax_segm_max": torch.empty(
                    (seq_threshold, 16, segments),
                    device=device,
                    dtype=torch.float32,
                ),
                "softmax_segm_expsum": torch.empty(
                    (seq_threshold, 16, segments),
                    device=device,
                    dtype=torch.float32,
                ),
            }
        )
    else:
        inputs.update(
            {
                "seq_threshold_3D": 0,
                "num_par_softmax_segments": 16,
                "softmax_segm_output": None,
                "softmax_segm_max": None,
                "softmax_segm_expsum": None,
            }
        )
    return inputs


def invoke(inputs: dict[str, torch.Tensor | int]) -> None:
    unified_attention(
        q=inputs["q"],
        k=inputs["k"],
        v=inputs["v"],
        out=inputs["out"],
        cu_seqlens_q=inputs["cu_seqlens_q"],
        seqused_k=inputs["seqused_k"],
        max_seqlen_q=inputs["max_seqlen_q"],
        max_seqlen_k=inputs["max_seqlen_k"],
        softmax_scale=128**-0.5,
        causal=True,
        window_size=(-1, -1),
        block_table=inputs["block_table"],
        softcap=0,
        q_descale=None,
        k_descale=None,
        v_descale=None,
        seq_threshold_3D=inputs["seq_threshold_3D"],
        num_par_softmax_segments=inputs["num_par_softmax_segments"],
        softmax_segm_output=inputs["softmax_segm_output"],
        softmax_segm_max=inputs["softmax_segm_max"],
        softmax_segm_expsum=inputs["softmax_segm_expsum"],
        kv_quant_mode=KVQuantMode.NONE,
    )


def measure(
    inputs: dict[str, torch.Tensor | int], warmups: int, repeats: int
) -> list[float]:
    for _ in range(warmups):
        invoke(inputs)
    torch.cuda.synchronize()
    times = []
    for _ in range(repeats):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        invoke(inputs)
        end.record()
        end.synchronize()
        times.append(start.elapsed_time(end))
    return times


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--query-len", type=int, default=2048)
    parser.add_argument("--kv-len", type=int, default=16384)
    parser.add_argument("--block-size", type=int, default=16)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    inputs = make_inputs(args.batch, args.query_len, args.kv_len, args.block_size)
    reference = None
    rows = []
    candidates = CANDIDATES if args.query_len > 1 else CANDIDATES_DECODE
    for block_m, tile_size, warps, stages in candidates:
        row = {
            "block_m": block_m,
            "tile_size": tile_size,
            "warps": warps,
            "stages": stages,
            "batch": args.batch,
            "query_len": args.query_len,
            "kv_len": args.kv_len,
            "block_size": args.block_size,
            "median_ms": "",
            "min_ms": "",
            "max_abs_diff": "",
            "status": "ok",
            "error": "",
        }
        try:
            attention._BI_EXPERIMENT_OVERRIDE = (
                block_m,
                tile_size,
                warps,
                stages,
            )
            times = measure(inputs, args.warmups, args.repeats)
            if reference is None:
                reference = inputs["out"].clone()
                row["max_abs_diff"] = 0.0
            else:
                row["max_abs_diff"] = float(
                    (inputs["out"] - reference).abs().max().item()
                )
            row.update(
                {
                    "median_ms": statistics.median(times),
                    "min_ms": min(times),
                    "times_ms": times,
                }
            )
        except Exception as exc:
            row["status"] = "error"
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)
        print(json.dumps(row), flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "block_m",
        "tile_size",
        "warps",
        "stages",
        "batch",
        "query_len",
        "kv_len",
        "block_size",
        "median_ms",
        "min_ms",
        "max_abs_diff",
        "status",
        "error",
    ]
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


if __name__ == "__main__":
    main()
