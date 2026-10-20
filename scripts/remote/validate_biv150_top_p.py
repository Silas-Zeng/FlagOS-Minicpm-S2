#!/usr/bin/env python3
"""Correctness and timing gate for the BI-V150 histogram top-p kernel."""

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
apply_top_p_hist_triton = _MODULE.apply_top_p_hist_triton


def compare(
    raw: torch.Tensor, expected: torch.Tensor, actual: torch.Tensor
) -> dict[str, float]:
    expected_keep = torch.isfinite(expected)
    actual_keep = torch.isfinite(actual)
    missing = expected_keep & ~actual_keep
    extra = actual_keep & ~expected_keep
    probs = raw.softmax(dim=-1, dtype=torch.float32)
    return {
        "missing_tokens": missing.sum(dim=1).float().max().item(),
        "extra_tokens": extra.sum(dim=1).float().max().item(),
        "missing_mass": (probs * missing).sum(dim=1).max().item(),
        "extra_mass": (probs * extra).sum(dim=1).max().item(),
    }


def timed_call(logits: torch.Tensor, p: torch.Tensor, repeats: int) -> float:
    for _ in range(5):
        apply_top_p_hist_triton(logits.clone(), p)
    torch.cuda.synchronize()
    total_ms = 0.0
    for _ in range(repeats):
        work = logits.clone()
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        apply_top_p_hist_triton(work, p)
        end.record()
        end.synchronize()
        total_ms += start.elapsed_time(end)
    return total_ms / repeats


def main() -> None:
    torch.manual_seed(20261021)
    device = torch.device("cuda")
    failures = []

    for scale in (0.5, 2.0, 5.0):
        raw = torch.randn((16, 130560), device=device) * scale
        for p_value in (0.0, 0.5, 0.9, 0.95, 0.99, 1.0):
            p = torch.full(
                (raw.shape[0],), p_value, device=device, dtype=torch.float32
            )
            expected = raw.clone()
            apply_top_k_top_p_pytorch(expected, None, p)
            actual = raw.clone()
            apply_top_p_hist_triton(actual, p)
            torch.cuda.synchronize()
            metrics = compare(raw, expected, actual)
            result = {"scale": scale, "top_p": p_value, **metrics}
            print("CORRECTNESS", result)
            if metrics["missing_tokens"]:
                probs = raw.softmax(dim=-1, dtype=torch.float32)
                row = int(
                    ((probs * (torch.isfinite(expected) & ~torch.isfinite(actual)))
                    .sum(dim=1)
                    .argmax()
                    .item())
                )
                workspace = _MODULE._get_workspace(
                    raw.shape[0], raw.shape[1], raw.device
                )
                expected_threshold = expected[row][
                    torch.isfinite(expected[row])
                ].min()
                actual_threshold = actual[row][
                    torch.isfinite(actual[row])
                ].min()
                print(
                    "BOUNDARY_DEBUG",
                    {
                        "row": row,
                        "tau": workspace.tau[row].item(),
                        "lo": workspace.lo[row].item(),
                        "hi": workspace.hi[row].item(),
                        "expected_threshold": expected_threshold.item(),
                        "actual_threshold": actual_threshold.item(),
                        "expected_kept_mass": (
                            probs[row] * torch.isfinite(expected[row])
                        ).sum().item(),
                        "actual_kept_mass": (
                            probs[row] * torch.isfinite(actual[row])
                        ).sum().item(),
                    },
                )
            if metrics["missing_mass"] > 1e-8 or metrics["extra_mass"] > 5e-4:
                failures.append(result)

    duplicate = torch.full((1, 130560), -10.0, device=device)
    duplicate[0, 123] = 5.0
    duplicate[0, 999] = 5.0
    p_zero = torch.zeros((1,), device=device)
    apply_top_p_hist_triton(duplicate, p_zero)
    kept = torch.isfinite(duplicate).nonzero().tolist()
    print("DUPLICATE_P0_INDICES", kept)
    if kept != [[0, 123], [0, 999]]:
        failures.append({"case": "duplicate_p0", "kept": kept})

    all_masked = torch.full((1, 130560), float("-inf"), device=device)
    p_half = torch.full((1,), 0.5, device=device)
    apply_top_p_hist_triton(all_masked, p_half)
    print("ALL_MASKED_FINITE_COUNT", torch.isfinite(all_masked).sum().item())
    if torch.isfinite(all_masked).any():
        failures.append({"case": "all_masked"})

    logits = torch.randn((64, 130560), device=device) * 2.0
    p = torch.full((64,), 0.95, device=device)
    timings = [timed_call(logits, p, 30) for _ in range(3)]
    print("TIMING_MS_MEDIAN", statistics.median(timings), timings)

    if failures:
        raise SystemExit(f"validation failed: {failures}")


if __name__ == "__main__":
    main()
