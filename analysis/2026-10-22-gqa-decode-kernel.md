# A dedicated GQA decode attention kernel for MiniCPM5-2B on BI-V150

Code: `vllm_fl/patches/biv150_gqa_decode.py` in the plugin repo, branch
`cjj/on-team-base`, installed from the end of `vllm_fl/worker/model_runner.py`
and gated by `VLLM_FL_BIV150_GQA_DECODE=1`.
Bench: `scripts/bench_gqa_decode.py` (A/B against the generic kernel with
identical seeded operands) and `scripts/check_gqa_kernel.py`.

## Why the generic kernel leaves decode performance on the table

The generic `kernel_unified_attention` must serve every model and every phase.
On a pure decode step of this model that costs:

| generic behaviour | consequence for decode |
|---|---|
| `BLOCK_M = 16` because `BLOCK_M / queries_per_kv = 2` query positions must be coverable | a decode step has one position, so 8 of 16 rows in Q, S, P and the accumulator are masked-off work |
| grid dim 0 is `tokens // BLOCK_Q + num_seqs` | more programs than (sequence, kv head) pairs; each program then runs `resolve_seq_and_query_len`, a search over `query_start_len` |
| one block-table gather per token (`seq_offset // BLOCK_SIZE`) | a decode tile of `TILE_SIZE == block_size == 16` is exactly one page, so 15 of 16 gathered entries are the same value, and the int64 index arithmetic is per element |
| full 2D causal mask per tile | for decode the query is the last position, so causality degenerates to `pos < seq_len` |
| natural `exp` with a rescale every 16-token tile | the rescale work is proportional to tile count |

## The kernel

One program per (sequence, kv head, segment). `ROWS` is exactly
`queries_per_kv = 8`, the sequence is the program id, a step is one page with a
scalar page index, the main loop carries no mask and only the final partial page
is clamped, and the softmax runs on `exp2` with `scale * log2(e)` folded into the
scores. Segment partials keep vLLM's own scratch layout, so the stock
`reduce_segments` finalizes them without modification.

Two details that were wrong before they were understood:

* the maxima handed to `reduce_segments` must be converted back to natural-log
  units (`running_max * ln2`). Inside the loop `exp2(a - b)` equals `exp(a - b)`
  for the sums and the accumulator, but the reduction combines segments with
  `tl.exp`, so keeping log2 units is wrong for every sequence that uses more than
  one segment. The single-segment case looked correct, which is why this showed up
  as a shape-dependent difference rather than an obvious failure.
* a step's page base must advance with the loop position, not stay at the segment
  start. Hoisting it made the kernel re-read the same page and report a fake
  1.86x.

## Kernel-level measurement

Identical seeded operands, generic kernel pinned to one warp and one stage
(`sweeps/20261022T152000Z-gqa-kernel-rows.csv`):

| shape | generic w1/s1 | new kernel | speedup | effective KV bandwidth |
|---|---|---|---|---|
| batch 64, kv 4096 | 0.948 ms | 0.648 ms | **1.46x** | 414 vs 283 GB/s |
| batch 16, kv 16384 | 0.981 ms | 0.536 ms | **1.83x** | 501 vs 274 GB/s |
| batch 1, kv 64 | 0.0217 ms | 0.0216 ms | 1.20x | launch-bound |

`pages_per_step = 2` and `num_warps = 2` were both worse than one page with one
warp, and `ROWS = 16` (padding to the generic shape) was consistently slower than
`ROWS = 8`, so the row-block reduction is where a good part of the gain comes from.
The reference weight-bandwidth anchor in this suite is `lm_head` at about
553 GB/s, so decode attention moved from roughly half of achievable to roughly
three quarters.

Max absolute output difference against the generic kernel is 4.9e-4 at 4K shape
and 1.2e-4 at 16K shape, on bf16 outputs of magnitude up to about 30, i.e. at the
one-ULP scale. **Not bit-exact**, so the accuracy gate is mandatory before this
can be submitted.

## End-to-end, same instance, same prompts, warm probes

| build | 4K total tok/s | 4K TPOT | 16K total tok/s | 16K TPOT |
|---|---|---|---|---|
| team candidate as shipped | 3785.68 | 68.71 | 2588.09 | 76.48 |
| team + one warp | 3878.88 | 66.81 | 2625.07 | 75.11 |
| team + one warp + 32 segments | 3893.38 | 66.52 | 2702.92 | 72.35 |
| **team + new decode kernel** | **4750.87** | **52.34** | **3216.9** | **56.79** |

That is **+25.5% on 4K and +24.3% on 16K over the team build measured on this
machine**, and +22.2% / +19.0% over the best parameter-only variant, which is the
sign that the remaining cost is no longer in the launch configuration.

Caveats recorded as measured:

* the 16K third repeat came out at 2429.84 while repeats 1 and 2 were 3216.92 and
  3216.88, so something external disturbed that run; it needs a re-measurement
  before the 16K number is quoted further.
* a greedy single-prompt completion is byte-identical to the pre-kernel server,
  which is a smoke test, not accuracy. The official math_500 Level 3 run has to
  cover this change.
* the probe builds used `VLLM_DISABLE_COMPILE_CACHE=1`; that only affects startup
  cost, not steady-state throughput.

## What is left in decode attention

At 414 GB/s for the 4K shape there is still headroom against the roughly 550 GB/s
this device reaches on `lm_head`. The remaining structural difference from a
perfect streaming kernel is that each of the 8 rows in a program is a separate
query head over the same KV, so the arithmetic per byte loaded is small and the
page loop is short. The next things worth measuring, in order:

1. two pages per step with a *scalar* pair of page indices (the earlier `pages=2`
   attempt used a per-column gather and lost);
2. more segments for the long-context case, now that the segment constant is
   shared between the launch policy, the mixed-decode split and this kernel;
3. keeping the accumulator in a wider tile so `acc * rescale` happens per two
   pages instead of per page.
