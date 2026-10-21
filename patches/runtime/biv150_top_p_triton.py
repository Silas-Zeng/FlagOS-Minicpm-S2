# SPDX-License-Identifier: Apache-2.0
"""Bounded histogram-zoom top-p filtering for BI-V150.

The fixed-work histogram refinement replaces the upstream top-p-only path's
repeated full-vocabulary probability-sum bisection. It keeps the public
``apply_top_k_top_p_triton`` interface and changes only the top-p-only branch.
"""

from __future__ import annotations

import torch

from vllm.triton_utils import tl, triton

_MAX_SPLITS = 1
_NBINS = 256
_ZOOM_ROUNDS = 2
_LOGIT_RANGE = 20.0
_BLOCK = 4096
_SAMPLE_SPLITS = 8
_CACHE: dict[tuple[torch.device, int, int], "_TopPWorkspace"] = {}
_RNG_STEP = 0


@triton.jit
def _row_stats_partial(
    LOGITS,
    MAX_PART,
    SUM_PART,
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
    row_sum = 0.0
    for tile in range(TILES_PER_SPLIT):
        idx = start + tile * BLOCK + offs
        values = tl.load(
            LOGITS + row * stride_row + idx,
            mask=idx < VOCAB_SIZE,
            other=float("-inf"),
        )
        tile_max = tl.max(values, axis=0)
        new_max = tl.maximum(row_max, tile_max)
        safe_new_max = tl.where(new_max == float("-inf"), 0.0, new_max)
        old_scale = tl.where(
            row_max == float("-inf"),
            0.0,
            tl.exp(row_max - safe_new_max),
        )
        row_sum = row_sum * old_scale + tl.sum(
            tl.exp(values - safe_new_max), axis=0
        )
        row_max = new_max
    tl.store(MAX_PART + row * MAX_SPLITS + split, row_max)
    tl.store(SUM_PART + row * MAX_SPLITS + split, row_sum)


@triton.jit
def _row_max_reduce(
    MAX_PART,
    SUM_PART,
    MAX_ROW,
    Z_ROW,
    PREFIX_MASS,
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
    safe_max = tl.where(row_max == float("-inf"), 0.0, row_max)
    partial_sums = tl.load(
        SUM_PART + row * MAX_SPLITS + offs,
        mask=offs < NUM_SPLITS,
        other=0.0,
    )
    row_sum = tl.sum(partial_sums * tl.exp(values - safe_max), axis=0)
    has_finite = row_max != float("-inf")
    tl.store(MAX_ROW + row, row_max)
    tl.store(Z_ROW + row, row_sum)
    tl.store(PREFIX_MASS + row, 0.0)
    tl.store(LO + row, tl.where(has_finite, row_max - RANGE, 0.0))
    tl.store(HI + row, tl.where(has_finite, row_max, 1.0))


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
    safe_max = tl.where(row_max == float("-inf"), 0.0, row_max)
    lo = tl.load(LO + row)
    hi = tl.load(HI + row)
    scale = NBINS / (hi - lo)
    start = split * TILES_PER_SPLIT * BLOCK
    for tile in range(TILES_PER_SPLIT):
        idx = start + tile * BLOCK + offs
        valid = idx < VOCAB_SIZE
        values = tl.load(
            LOGITS + row * stride_row + idx,
            mask=valid,
            other=float("-inf"),
        )
        bins = ((values - lo) * scale).to(tl.int32)
        bins = tl.minimum(tl.maximum(bins, 0), NBINS - 1)
        weights = tl.exp(values - safe_max)
        active = (
            valid
            & (row_max != float("-inf"))
            & (values >= lo)
            & (values <= hi)
        )
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
    FINAL: tl.constexpr,
):
    row = tl.program_id(0)
    offs = tl.arange(0, NBINS)
    reversed_mass = tl.load(HIST + row * NBINS + (NBINS - 1 - offs))
    cumulative = tl.cumsum(reversed_mass, axis=0)
    p = tl.load(P + row).to(tl.float32)
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
        values = tl.load(
            LOGITS + row * stride_row + idx,
            mask=valid,
            other=float("-inf"),
        )
        if p >= 1.0:
            keep = valid
        elif p <= 0.0:
            keep = valid & (values == row_max)
        else:
            keep = valid & (values >= tau)
        tl.store(
            LOGITS + row * stride_row + idx,
            tl.where(keep, values, MASK_VALUE),
            mask=valid,
        )


@triton.jit
def _sample_partial(
    LOGITS,
    MAX_ROW,
    P,
    TAU,
    PART_VALUES,
    PART_INDICES,
    stride_row,
    seed,
    step,
    VOCAB_SIZE: tl.constexpr,
    NUM_SPLITS: tl.constexpr,
    TILES_PER_SPLIT: tl.constexpr,
    VOCAB_PADDED: tl.constexpr,
    BLOCK: tl.constexpr,
):
    row = tl.program_id(0)
    split = tl.program_id(1)
    offs = tl.arange(0, BLOCK)
    p = tl.load(P + row)
    tau = tl.load(TAU + row)
    row_max = tl.load(MAX_ROW + row)
    start = split * TILES_PER_SPLIT * BLOCK
    best = float("-inf")
    best_idx = 0
    row_seed = seed + row

    for tile in range(TILES_PER_SPLIT):
        idx = start + tile * BLOCK + offs
        valid = idx < VOCAB_SIZE
        values = tl.load(
            LOGITS + row * stride_row + idx,
            mask=valid,
            other=float("-inf"),
        )
        if p >= 1.0:
            keep = valid
        elif p <= 0.0:
            keep = valid & (values == row_max)
        else:
            keep = valid & (values >= tau)

        uniform = tl.rand(
            row_seed,
            step * VOCAB_PADDED + idx.to(tl.int32),
        )
        uniform = tl.minimum(tl.maximum(uniform, 1e-20), 1.0 - 1e-7)
        gumbel = -tl.log(-tl.log(uniform))
        score = tl.where(keep, values + gumbel, float("-inf"))
        tile_best = tl.max(score, axis=0)
        tile_idx = tl.argmax(score, axis=0)
        take = tile_best > best
        best_idx = tl.where(take, start + tile * BLOCK + tile_idx, best_idx)
        best = tl.maximum(best, tile_best)

    tl.store(PART_VALUES + row * NUM_SPLITS + split, best)
    tl.store(PART_INDICES + row * NUM_SPLITS + split, best_idx)


@triton.jit
def _sample_reduce(
    PART_VALUES,
    PART_INDICES,
    OUT,
    NUM_SPLITS: tl.constexpr,
    MAX_SPLITS: tl.constexpr,
):
    row = tl.program_id(0)
    offs = tl.arange(0, MAX_SPLITS)
    active = offs < NUM_SPLITS
    values = tl.load(
        PART_VALUES + row * MAX_SPLITS + offs,
        mask=active,
        other=float("-inf"),
    )
    indices = tl.load(
        PART_INDICES + row * MAX_SPLITS + offs,
        mask=active,
        other=0,
    )
    best_split = tl.argmax(values, axis=0)
    token = tl.sum(tl.where(offs == best_split, indices, 0), axis=0)
    tl.store(OUT + row, token)


class _TopPWorkspace:
    def __init__(self, batch_size: int, vocab_size: int, device: torch.device):
        self.batch_size = batch_size
        self.vocab_size = vocab_size
        self.tiles_per_split = triton.cdiv(
            triton.cdiv(vocab_size, _BLOCK), _MAX_SPLITS
        )
        fp32 = {"device": device, "dtype": torch.float32}
        self.max_part = torch.empty(batch_size, _MAX_SPLITS, **fp32)
        self.sum_part = torch.empty(batch_size, _MAX_SPLITS, **fp32)
        self.max_row = torch.empty(batch_size, **fp32)
        self.z_row = torch.empty(batch_size, **fp32)
        self.prefix_mass = torch.empty(batch_size, **fp32)
        self.lo = torch.empty(batch_size, **fp32)
        self.hi = torch.empty(batch_size, **fp32)
        self.tau = torch.empty(batch_size, **fp32)
        self.hist = torch.empty(batch_size, _NBINS, **fp32)
        self.sample_tiles_per_split = triton.cdiv(
            triton.cdiv(vocab_size, _BLOCK), _SAMPLE_SPLITS
        )
        self.sample_vocab_padded = (
            self.sample_tiles_per_split * _SAMPLE_SPLITS * _BLOCK
        )
        self.part_values = torch.empty(
            batch_size, _SAMPLE_SPLITS, **fp32
        )
        self.part_indices = torch.empty(
            batch_size,
            _SAMPLE_SPLITS,
            device=device,
            dtype=torch.int32,
        )
        self.sample_out = torch.empty(
            batch_size, device=device, dtype=torch.int64
        )


def _get_workspace(
    batch_size: int, vocab_size: int, device: torch.device
) -> _TopPWorkspace:
    key = (device, batch_size, vocab_size)
    workspace = _CACHE.get(key)
    if workspace is None:
        workspace = _TopPWorkspace(batch_size, vocab_size, device)
        _CACHE[key] = workspace
    return workspace


def _compute_top_p_tau(
    logits: torch.Tensor,
    p: torch.Tensor,
) -> tuple[_TopPWorkspace, int]:
    assert logits.ndim == 2
    assert logits.dtype == torch.float32
    assert logits.stride(1) == 1
    assert p.ndim == 1 and p.shape[0] == logits.shape[0]
    if logits.shape[0] == 0:
        raise ValueError("empty logits")

    batch_size, vocab_size = logits.shape
    workspace = _get_workspace(batch_size, vocab_size, logits.device)
    grid = (batch_size, _MAX_SPLITS)

    _row_stats_partial[grid](
        logits,
        workspace.max_part,
        workspace.sum_part,
        logits.stride(0),
        VOCAB_SIZE=vocab_size,
        NUM_SPLITS=_MAX_SPLITS,
        MAX_SPLITS=_MAX_SPLITS,
        TILES_PER_SPLIT=workspace.tiles_per_split,
        BLOCK=_BLOCK,
        num_warps=8,
    )
    _row_max_reduce[(batch_size,)](
        workspace.max_part,
        workspace.sum_part,
        workspace.max_row,
        workspace.z_row,
        workspace.prefix_mass,
        workspace.lo,
        workspace.hi,
        NUM_SPLITS=_MAX_SPLITS,
        MAX_SPLITS=_MAX_SPLITS,
        RANGE=_LOGIT_RANGE,
        num_warps=1,
    )
    for round_no in range(_ZOOM_ROUNDS, 0, -1):
        workspace.hist.zero_()
        _weighted_hist[grid](
            logits,
            workspace.max_row,
            workspace.lo,
            workspace.hi,
            workspace.hist,
            logits.stride(0),
            VOCAB_SIZE=vocab_size,
            NUM_SPLITS=_MAX_SPLITS,
            TILES_PER_SPLIT=workspace.tiles_per_split,
            NBINS=_NBINS,
            BLOCK=_BLOCK,
            num_warps=8,
        )
        _hist_walk[(batch_size,)](
            workspace.hist,
            p,
            workspace.z_row,
            workspace.prefix_mass,
            workspace.lo,
            workspace.hi,
            workspace.tau,
            NBINS=_NBINS,
            FINAL=round_no == 1,
            num_warps=1,
        )

    return workspace, vocab_size


def apply_top_p_hist_triton(
    logits: torch.Tensor,
    p: torch.Tensor,
    mask_value: float = float("-inf"),
) -> torch.Tensor:
    """Apply top-p masking with bounded histogram refinement."""
    if logits.shape[0] == 0:
        return logits
    workspace, vocab_size = _compute_top_p_tau(logits, p)
    grid = (logits.shape[0], _MAX_SPLITS)
    _apply_mask[grid](
        logits,
        workspace.max_row,
        p,
        workspace.tau,
        logits.stride(0),
        VOCAB_SIZE=vocab_size,
        NUM_SPLITS=_MAX_SPLITS,
        TILES_PER_SPLIT=workspace.tiles_per_split,
        MASK_VALUE=mask_value,
        BLOCK=_BLOCK,
        num_warps=8,
    )
    return logits


def sample_top_p_hist_triton(
    logits: torch.Tensor,
    p: torch.Tensor,
    seed: int = 0,
) -> torch.Tensor:
    """Fuse top-p thresholding and Gumbel-Max sampling."""
    global _RNG_STEP
    if logits.shape[0] == 0:
        return torch.empty(0, device=logits.device, dtype=torch.int64)

    workspace, vocab_size = _compute_top_p_tau(logits, p)
    grid = (logits.shape[0], _SAMPLE_SPLITS)
    step = _RNG_STEP
    _RNG_STEP += 1
    _sample_partial[grid](
        logits,
        workspace.max_row,
        p,
        workspace.tau,
        workspace.part_values,
        workspace.part_indices,
        logits.stride(0),
        seed,
        step,
        VOCAB_SIZE=vocab_size,
        NUM_SPLITS=_SAMPLE_SPLITS,
        TILES_PER_SPLIT=workspace.sample_tiles_per_split,
        VOCAB_PADDED=workspace.sample_vocab_padded,
        BLOCK=_BLOCK,
        num_warps=8,
    )
    _sample_reduce[(logits.shape[0],)](
        workspace.part_values,
        workspace.part_indices,
        workspace.sample_out,
        NUM_SPLITS=_SAMPLE_SPLITS,
        MAX_SPLITS=_SAMPLE_SPLITS,
        num_warps=1,
    )
    return workspace.sample_out
