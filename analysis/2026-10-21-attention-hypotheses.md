# Attention backend hypothesis register

## Verified code facts

The official `vllm-plugin-FL` commit used by the baseline contains both:

- a generic vLLM Triton attention route returned by default; and
- an optional FlagGems FlashAttention-2 adapter controlled by
  `VLLM_FL_USE_FLAGGEMS_ATTN`, default `"0"`.

Relevant source:

- `vllm_fl/dispatch/backends/flaggems/flaggems.py`
- `vllm_fl/dispatch/backends/flaggems/impl/attention.py`
- `vllm_fl/dispatch/backends/vendor/iluvatar/iluvatar.py`

The baseline service did not print the FlagGems backend opt-in message and the
source default is disabled. Therefore the baseline is not using the existing
FlagGems FlashAttention-2 adapter.

The installed FlagGems package has `use_c_extension=False`, so the optional
FlagGems path is the pure Triton `flash_varlen_fwd_kernel`, not the C++
extension. PyTorch reports 16 SMs and 16 MiB of L2 for this device instance.

Current Iluvatar heuristic settings are:

| Logical tile | BLOCK_M | BLOCK_N | warps | stages |
|---|---:|---:|---:|---:|
| `mha_block_16` | 16 | 32 | 4 | 3 |
| `mha_block_32` | 32 | 32 | 4 | 3 |
| `mha_block_64` | 64 | 32 | 4 | 3 |
| `mha_block_128` | 128 | 32 | 4 | 3 |

For single-token decode with 16 query heads and 2 KV heads, FlagGems swaps the
eight query groups into the sequence dimension. The resulting maximum query
length is eight, while the heuristic selects a 16-row tile. The microbenchmark
therefore also tests an 8-row tile, along with block sizes 32, 64, and 128.

The default paged-cache block size is 16. A 16K context therefore uses 1,024
page-table entries per sequence. Tests will compare cache block sizes 16, 32,
and 64; a smaller table may reduce decode overhead, but it is retained only if
the end-to-end service remains correct and repeatably faster.

## Hypothesis

The generic Triton attention path is a major contributor to both:

- the long 16K prefill/TTFT tail, whose published TianShu mean is 599 seconds;
- the 4K decode tail, whose local mean TPOT is about 160-173 ms.

This hypothesis is not yet a measured root cause. A profiler trace must quantify
the generic attention kernel share before attributing the full gap to it.

## Experiment sequence

1. Profile the unchanged baseline and aggregate kernels by prefill and decode.
2. Run a same-service microbenchmark for FlagGems FA2 tile candidates.
3. Enable the existing FlagGems path only as a diagnostic comparison.
4. If it wins, add an actual BI-V150-specific kernel/configuration optimization
   in FlagGems and enable the optimized path through submitted code, not a new
   final-serving environment variable.
5. Validate output parity, repeated performance, TTFT, and the official
   accuracy evaluation.

## First microbenchmark matrix

| Phase | Batch | Sequence length | Cache block size | Purpose |
|---|---:|---:|---:|---|
| Prefill | 8 | 4096 | 16, 32, 64 | Match approximately 32K aggregate query tokens |
| Prefill | 2 | 16384 | 16, 32, 64 | Same query-token volume with 4x context |
| Decode | 64 | 4096 | 16, 32, 64 | Official 4K active concurrency |
| Decode | 32 | 16384 | 16, 32, 64 | Near the measured KV-capacity-limited active count |

## Compliance boundary

Merely flipping an environment variable from the generic backend to the
existing FlagGems backend is not sufficient for the final submission. The
competition forbids switching an operator without an operator optimization.
The final change must include an auditable implementation or kernel tuning
improvement in FlagGems and an ablation against the existing operator.

## External evidence

A public related project reports the same default-off code path and proposes
the same validation sequence:

- <https://github.com/SOLECA794/minicpm5-2b-infer-opt-flagos>

That project explicitly labels its performance attribution as
`PLAUSIBLE`, not proven. We treat it as a lead, not as ground truth.
