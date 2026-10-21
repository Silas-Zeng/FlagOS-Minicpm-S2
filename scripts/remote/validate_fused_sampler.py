#!/usr/bin/env python3
"""Validate the fused BI-V150 top-p + Gumbel sampling tail."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import statistics

import torch

from vllm.v1.sample.ops.topk_topp_sampler import apply_top_k_top_p_pytorch

_MODULE_PATH = (
    Path(__file__).resolve().parent.parent / "runtime" / "biv150_top_p_triton.py"
)
_SPEC = importlib.util.spec_from_file_location(
    "biv150_top_p_triton", _MODULE_PATH
)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def elapsed(fn, iterations: int) -> float:
    for _ in range(5):
        fn()
    torch.cuda.synchronize()
    total = 0.0
    for _ in range(iterations):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        fn()
        end.record()
        end.synchronize()
        total += start.elapsed_time(end)
    return total / iterations


def main() -> None:
    torch.manual_seed(20261021)
    device = torch.device("cuda")
    vocab = 130560

    # All sampled tokens must belong to the exact top-p retained set.
    allowed_logits = torch.randn((4, vocab), device=device) * 2.0
    p = torch.full((4,), 0.95, device=device)
    masked = allowed_logits.clone()
    apply_top_k_top_p_pytorch(masked, None, p)
    allowed = torch.isfinite(masked)
    for _ in range(80):
        tokens = _MODULE.sample_top_p_hist_triton(allowed_logits, p)
        if not allowed.gather(1, tokens[:, None]).all():
            raise SystemExit("fused sampler returned a masked token")

    # Empirical distribution on an intentionally sparse row.
    sparse = torch.full((1, vocab), -float("inf"), device=device)
    sparse[0, :10] = torch.tensor(
        [8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0, -1.0],
        device=device,
    )
    p_one = torch.tensor([0.95], device=device)
    reference = sparse.clone()
    apply_top_k_top_p_pytorch(reference, None, p_one)
    expected = reference.softmax(dim=-1, dtype=torch.float32)[0]
    counts = torch.zeros(vocab, device=device, dtype=torch.float32)
    draws = 600
    for _ in range(draws):
        token = _MODULE.sample_top_p_hist_triton(sparse, p_one)
        counts[token] += 1
    observed = counts / draws
    tv_distance = 0.5 * (observed - expected).abs().sum()
    print("SPARSE_TV_DISTANCE", tv_distance.item())
    print("SPARSE_SUPPORT", torch.isfinite(reference).sum().item())
    if tv_distance.item() > 0.08:
        raise SystemExit("fused sampler distribution drifted")

    logits = torch.randn((64, vocab), device=device) * 2.0
    p_batch = torch.full((64,), 0.95, device=device)

    def reference_tail() -> None:
        work = logits.clone()
        _MODULE.apply_top_p_hist_triton(work, p_batch)
        probs = work.softmax(dim=-1, dtype=torch.float32)
        probs.div_(torch.empty_like(probs).exponential_()).argmax(dim=-1)

    def fused_tail() -> None:
        _MODULE.sample_top_p_hist_triton(logits, p_batch)

    reference_ms = elapsed(reference_tail, 30)
    fused_ms = elapsed(fused_tail, 30)
    print(
        "TAIL_TIMING",
        {
            "reference_ms": reference_ms,
            "fused_ms": fused_ms,
            "speedup": reference_ms / fused_ms,
        },
    )
    if fused_ms >= reference_ms:
        raise SystemExit("fused sampler is not faster")


if __name__ == "__main__":
    main()
