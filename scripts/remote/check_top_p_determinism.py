#!/usr/bin/env python3
"""Check repeated histogram top-p calls produce the same retained set."""

from __future__ import annotations

import torch

from vllm_fl.patches.biv150_top_p_triton import apply_top_p_hist_triton


def main() -> None:
    torch.manual_seed(20261021)
    device = torch.device("cuda")
    failures = []
    for batch in (1, 8, 16, 64):
        for scale in (0.5, 2.0, 5.0):
            raw = torch.randn((batch, 130560), device=device) * scale
            p = torch.full((batch,), 0.95, device=device)
            reference = None
            identical = True
            for _ in range(20):
                candidate = raw.clone()
                apply_top_p_hist_triton(candidate, p)
                mask = torch.isfinite(candidate)
                if reference is None:
                    reference = mask
                elif not torch.equal(reference, mask):
                    identical = False
            result = {
                "batch": batch,
                "scale": scale,
                "identical_across_20_calls": identical,
            }
            print(result, flush=True)
            if not identical:
                failures.append(result)
    if failures:
        raise SystemExit(f"non-deterministic top-p masks: {failures}")


if __name__ == "__main__":
    main()
