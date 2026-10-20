#!/usr/bin/env python3
"""Microbenchmark histogram-zoom top-p candidates on the active accelerator."""

from __future__ import annotations

import argparse
import statistics
import time

import torch
import triton
import triton.language as tl

from vllm.v1.sample.ops.topk_topp_sampler import apply_top_k_top_p_pytorch
from vllm.v1.sample.ops.topk_topp_triton import apply_top_k_top_p_triton


MAX_SPLITS = 32


@triton.jit
def _row_max_partial(
    LOGITS,
    MAX_PART,
    stride_row,
    VOCAB_SIZE: tl.constexpr,
    NUM_SPLITS: tl.constexpr,
    MAX_SPLITS: tl.constexpr,
    TILES_PER_SPLIT: tl.constexpr,
    BLOCK: tl.constexpr,
):
    row = tl.program_id(0)
    split = tl.program_id(1)
    offs = tl.arange(0, BLOCK)
    start = split * TILES_PER_SPLIT * BLOCK
    row_max = float("-inf")
    for tile in range(TILES_PER_SPLIT):
        idx = start + tile * BLOCK + offs
        logits = tl.load(
            LOGITS + row * stride_row + idx,
            mask=idx < VOCAB_SIZE,
            other=float("-inf"),
        )
        row_max = tl.maximum(row_max, tl.max(logits, axis=0))
    tl.store(MAX_PART + row * MAX_SPLITS + split, row_max)


@triton.jit
def _row_max_reduce(
    MAX_PART,
    MAX_ROW,
    LO,
    HI,
    NUM_SPLITS: tl.constexpr,
    MAX_SPLITS: tl.constexpr,
    RANGE: tl.constexpr,
):
    row = tl.program_id(0)
    offs = tl.arange(0, MAX_SPLITS)
    values = tl.load(
        MAX_PART + row * MAX_SPLITS + offs,
        mask=offs < NUM_SPLITS,
        other=float("-inf"),
    )
    row_max = tl.max(values, axis=0)
    tl.store(MAX_ROW + row, row_max)
    tl.store(LO + row, row_max - RANGE)
    tl.store(HI + row, row_max)


@triton.jit
def _weighted_hist(
    LOGITS,
    MAX_ROW,
    LO,
    HI,
    HIST,
    stride_row,
    VOCAB_SIZE: tl.constexpr,
    NUM_SPLITS: tl.constexpr,
    TILES_PER_SPLIT: tl.constexpr,
    NBINS: tl.constexpr,
    BLOCK: tl.constexpr,
):
    row = tl.program_id(0)
    split = tl.program_id(1)
    offs = tl.arange(0, BLOCK)
    row_max = tl.load(MAX_ROW + row)
    lo = tl.load(LO + row)
    hi = tl.load(HI + row)
    scale = NBINS / (hi - lo)
    start = split * TILES_PER_SPLIT * BLOCK
    for tile in range(TILES_PER_SPLIT):
        idx = start + tile * BLOCK + offs
        valid = idx < VOCAB_SIZE
        logits = tl.load(
            LOGITS + row * stride_row + idx,
            mask=valid,
            other=float("-inf"),
        )
        bins = ((logits - lo) * scale).to(tl.int32)
        bins = tl.minimum(tl.maximum(bins, 0), NBINS - 1)
        weights = tl.exp(logits - row_max)
        active = valid & (logits >= lo) & (logits <= hi)
        tl.atomic_add(HIST + row * NBINS + bins, weights, mask=active)


@triton.jit
def _hist_walk(
    HIST,
    P,
    Z_ROW,
    PREFIX_MASS,
    LO,
    HI,
    TAU,
    NBINS: tl.constexpr,
    FIRST: tl.constexpr,
    FINAL: tl.constexpr,
):
    row = tl.program_id(0)
    offs = tl.arange(0, NBINS)
    reversed_mass = tl.load(HIST + row * NBINS + (NBINS - 1 - offs))
    cumulative = tl.cumsum(reversed_mass, axis=0)
    p = tl.load(P + row).to(tl.float32)
    if FIRST:
        total_mass = tl.sum(reversed_mass, axis=0)
        tl.store(Z_ROW + row, total_mass)
        previous_mass = 0.0
    else:
        total_mass = tl.load(Z_ROW + row)
        previous_mass = tl.load(PREFIX_MASS + row)
    target = p * total_mass
    reached = (previous_mass + cumulative) >= target
    crossing = tl.argmax(reached.to(tl.int32), axis=0)
    selected_prefix = tl.where(
        crossing > 0,
        tl.sum(
            tl.where(offs == tl.maximum(crossing - 1, 0), cumulative, 0.0),
            axis=0,
        ),
        0.0,
    )
    tl.store(PREFIX_MASS + row, previous_mass + selected_prefix)
    bin_id = NBINS - 1 - crossing
    if FINAL:
        bin_id = tl.maximum(bin_id - 1, 0)
    lo = tl.load(LO + row)
    hi = tl.load(HI + row)
    width = (hi - lo) / NBINS
    lower = lo + bin_id * width
    upper = lower + width
    if FINAL:
        tl.store(TAU + row, lower)
    else:
        tl.store(LO + row, lower)
        tl.store(HI + row, upper)


@triton.jit
def _apply_mask(
    LOGITS,
    MAX_ROW,
    P,
    TAU,
    stride_row,
    VOCAB_SIZE: tl.constexpr,
    NUM_SPLITS: tl.constexpr,
    TILES_PER_SPLIT: tl.constexpr,
    MASK_VALUE: tl.constexpr,
    BLOCK: tl.constexpr,
):
    row = tl.program_id(0)
    split = tl.program_id(1)
    offs = tl.arange(0, BLOCK)
    p = tl.load(P + row)
    tau = tl.load(TAU + row)
    row_max = tl.load(MAX_ROW + row)
    start = split * TILES_PER_SPLIT * BLOCK
    for tile in range(TILES_PER_SPLIT):
        idx = start + tile * BLOCK + offs
        valid = idx < VOCAB_SIZE
        logits = tl.load(
            LOGITS + row * stride_row + idx,
            mask=valid,
            other=float("-inf"),
        )
        if p >= 1.0:
            keep = valid
        elif p <= 0.0:
            keep = valid & (logits == row_max)
        else:
            keep = valid & (logits >= tau)
        out = tl.where(keep, logits, MASK_VALUE)
        tl.store(LOGITS + row * stride_row + idx, out, mask=valid)


class HistogramTopP:
    def __init__(
        self,
        batch_size: int,
        vocab_size: int,
        device: torch.device,
        *,
        num_splits: int,
        block: int,
        bins: int,
        rounds: int,
    ) -> None:
        self.batch_size = batch_size
        self.vocab_size = vocab_size
        self.device = device
        self.num_splits = min(num_splits, MAX_SPLITS)
        self.block = block
        self.bins = bins
        self.rounds = rounds
        tiles_total = triton.cdiv(vocab_size, block)
        self.tiles_per_split = triton.cdiv(tiles_total, self.num_splits)
        fp32 = dict(device=device, dtype=torch.float32)
        self.max_part = torch.empty(batch_size, MAX_SPLITS, **fp32)
        self.max_row = torch.empty(batch_size, **fp32)
        self.z_row = torch.empty(batch_size, **fp32)
        self.prefix_mass = torch.empty(batch_size, **fp32)
        self.lo = torch.empty(batch_size, **fp32)
        self.hi = torch.empty(batch_size, **fp32)
        self.tau = torch.empty(batch_size, **fp32)
        self.hist = torch.empty(batch_size, bins, **fp32)

    def __call__(
        self,
        logits: torch.Tensor,
        p: torch.Tensor,
        mask_value: float = float("-inf"),
    ) -> torch.Tensor:
        grid = (self.batch_size, self.num_splits)
        _row_max_partial[grid](
            logits,
            self.max_part,
            logits.stride(0),
            VOCAB_SIZE=self.vocab_size,
            NUM_SPLITS=self.num_splits,
            TILES_PER_SPLIT=self.tiles_per_split,
            MAX_SPLITS=MAX_SPLITS,
            BLOCK=self.block,
            num_warps=8,
        )
        _row_max_reduce[(self.batch_size,)](
            self.max_part,
            self.max_row,
            self.lo,
            self.hi,
            NUM_SPLITS=self.num_splits,
            MAX_SPLITS=MAX_SPLITS,
            RANGE=20.0,
            num_warps=1,
        )
        for round_no in range(self.rounds, 0, -1):
            self.hist.zero_()
            _weighted_hist[grid](
                logits,
                self.max_row,
                self.lo,
                self.hi,
                self.hist,
                logits.stride(0),
                VOCAB_SIZE=self.vocab_size,
                NUM_SPLITS=self.num_splits,
                TILES_PER_SPLIT=self.tiles_per_split,
                NBINS=self.bins,
                BLOCK=self.block,
                num_warps=8,
            )
            _hist_walk[(self.batch_size,)](
                self.hist,
                p,
                self.z_row,
                self.prefix_mass,
                self.lo,
                self.hi,
                self.tau,
                NBINS=self.bins,
                FIRST=round_no == self.rounds,
                FINAL=round_no == 1,
                num_warps=1,
            )
        _apply_mask[grid](
            logits,
            self.max_row,
            p,
            self.tau,
            logits.stride(0),
            VOCAB_SIZE=self.vocab_size,
            NUM_SPLITS=self.num_splits,
            TILES_PER_SPLIT=self.tiles_per_split,
            MASK_VALUE=mask_value,
            BLOCK=self.block,
            num_warps=8,
        )
        return logits


def _benchmark(fn, source: torch.Tensor, warmup: int, iterations: int) -> float:
    for _ in range(warmup):
        fn(source.clone())
    torch.cuda.synchronize()
    buffers = [source.clone() for _ in range(iterations)]
    torch.cuda.synchronize()
    samples = []
    for buffer in buffers:
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        fn(buffer)
        end.record()
        end.synchronize()
        samples.append(start.elapsed_time(end))
    return statistics.median(samples)


def _compare_masks(
    raw_logits: torch.Tensor,
    reference: torch.Tensor,
    candidate: torch.Tensor,
    vocab_size: int,
) -> dict[str, float]:
    ref_keep = torch.isfinite(reference)
    cand_keep = torch.isfinite(candidate)
    missing = ref_keep & ~cand_keep
    extra = cand_keep & ~ref_keep
    probs = raw_logits.softmax(dim=-1, dtype=torch.float32)
    return {
        "missing_tokens": missing.sum(dim=1).float().mean().item(),
        "extra_tokens": extra.sum(dim=1).float().mean().item(),
        "missing_mass": (probs * missing).sum(dim=1).mean().item(),
        "extra_mass": (probs * extra).sum(dim=1).mean().item(),
        "candidate_kept_mass": (probs * cand_keep).sum(dim=1).mean().item(),
        "vocab_size": float(vocab_size),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--vocab", type=int, default=130560)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--iterations", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20261021)
    parser.add_argument("--splits", type=int, nargs="+", default=[1, 2, 4, 8])
    parser.add_argument("--blocks", type=int, nargs="+", default=[2048, 4096, 8192])
    parser.add_argument("--rounds", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--bins", type=int, nargs="+", default=[256])
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    device = torch.device("cuda")
    logits = torch.randn((args.batch, args.vocab), device=device) * 2.0
    p = torch.full((args.batch,), 0.95, device=device, dtype=torch.float32)

    reference = logits.clone()
    apply_top_k_top_p_pytorch(reference, None, p)
    upstream = logits.clone()
    apply_top_k_top_p_triton(upstream, None, p)

    print(
        "upstream_vs_pytorch",
        _compare_masks(logits, reference, upstream, args.vocab),
    )
    baseline_ms = _benchmark(
        lambda work: apply_top_k_top_p_triton(work, None, p),
        logits,
        args.warmup,
        args.iterations,
    )
    print("BASELINE_MS", baseline_ms)

    for num_splits in args.splits:
        for block in args.blocks:
            for rounds in args.rounds:
                for bins in args.bins:
                    candidate_fn = HistogramTopP(
                        args.batch,
                        args.vocab,
                        device,
                        num_splits=num_splits,
                        block=block,
                        bins=bins,
                        rounds=rounds,
                    )
                    candidate = logits.clone()
                    candidate_fn(candidate, p)
                    torch.cuda.synchronize()
                    comparison = _compare_masks(
                        logits, reference, candidate, args.vocab
                    )
                    if args.debug:
                        row = 0
                        exact_threshold = reference[row][
                            torch.isfinite(reference[row])
                        ].min()
                        print(
                            "DEBUG_ROW0",
                            {
                                "max": candidate_fn.max_row[row].item(),
                                "z": candidate_fn.z_row[row].item(),
                                "prefix": candidate_fn.prefix_mass[row].item(),
                                "lo": candidate_fn.lo[row].item(),
                                "hi": candidate_fn.hi[row].item(),
                                "tau": candidate_fn.tau[row].item(),
                                "exact": exact_threshold.item(),
                            },
                        )
                    elapsed_ms = _benchmark(
                        lambda work: candidate_fn(work, p),
                        logits,
                        args.warmup,
                        args.iterations,
                    )
                    print(
                        "CANDIDATE",
                        {
                            "splits": num_splits,
                            "block": block,
                            "rounds": rounds,
                            "bins": bins,
                            "ms": elapsed_ms,
                            **comparison,
                        },
                    )


if __name__ == "__main__":
    main()
