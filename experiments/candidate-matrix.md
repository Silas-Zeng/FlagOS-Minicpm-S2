# Candidate experiment matrix

Only one accelerator job may run at a time. Every performance comparison uses
the same clean service launch arguments, warmup policy, input generator, and
output length. The optimization must be enabled by code for final scoring; an
environment variable is acceptable only for a diagnostic A/B.

## Gates

For each candidate:

1. Start the model and complete the official smoke request.
2. Compare a representative kernel output against the original implementation.
3. Run a short paired 4K and 16K load.
4. Compare repeated end-to-end results on the same device.
5. Run the full official three-run average only after the short result is
   positive and correctness is intact.
6. Run `math_500` Level 3 before final selection.

## Matrix

| ID | Backend / change | Purpose | Status |
|---|---|---|---|
| B0 | Generic `TRITON_ATTN`, official clean service | Local baseline | running |
| B1 | Profile of B0, 4K steady decode | Locate decode kernels and CPU gaps | pending |
| B2 | Profile of B0, 16K prefill | Locate long-prefill kernels | pending |
| A1 | Existing FlagGems FA2, default heuristic | Determine backend-level gain | pending |
| A2 | FlagGems FA2, packed-GQA8 decode `BM=8/BN=32/w4/s3` | Remove masked half tile | prepared |
| A3 | FlagGems FA2, vary stage/warp/block N | Tune BIV150 kernel | pending |
| F1 | Conditional sampler compile restoration | Reduce per-token sampled host overhead | pending |
| F2 | Iluvatar cache block size 64 or 128 | Reduce block-table/index overhead | pending |
| F3 | RoPE plus KV-cache write fusion | Reduce decode launches and traffic | only if profile justifies |
| F4 | Fused residual RMSNorm | Reduce norm/memory traffic | only if profile justifies |

## Interpretation

- A backend switch by itself is not a final optimization. A2/A3 must provide a
  real FlagGems kernel/config change and an ablation against A1.
- Block-size and sampler changes are independent variables and must not be
  combined until each has a result.
- A candidate below the 1% ambiguity window is retained as a negative result,
  not described as a win.
- Results from profiling instrumentation are never mixed with timing runs.
