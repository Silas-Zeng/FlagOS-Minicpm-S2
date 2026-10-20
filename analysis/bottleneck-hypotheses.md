# Bottleneck hypotheses and falsification tests

These are hypotheses, not conclusions. Each must be promoted or rejected using
the listed measurement.

| Priority | Hypothesis | Required evidence | Falsifier |
|---:|---|---|---|
| H1 | Decode is limited by small-M linear kernels reading the 4.7 GiB model | Decode trace: BF16 GEMM is the dominant kernel group; observed SM/device utilization and cost remain poor as M varies from 1 to 64 | GEMM is a small time share, or its cost scales linearly with achieved arithmetic throughput |
| H2 | Chunked prefill repeatedly displaces decode and creates long queues | Engine timeline shows alternating mixed/decode segments; TTFT tail and aggregate throughput respond to admission/chunk scheduling | Mixed and decode-only phases have the same per-token device efficiency |
| H3 | Paged GQA Attention is a major 16K bottleneck | Decode trace: FlashAttention/KV kernels dominate; split-KV/tile sweep shows a material gain | Attention remains a small share after KV length grows |
| H4 | Full decode graphs reduce launch overhead but host gaps remain | CPU/device trace shows long host gaps or synchronization between graph segments | Device timeline is continuously occupied during steady decode |
| H5 | Normalization, activation, and rotary kernels add avoidable launches and memory traffic | Trace shows a material combined share with many small launches | Combined device time is below the 1% end-to-end scoring floor |
| H6 | KV block size 16 and page-table formatting are suboptimal on BI-V150 | Compare block sizes and paged-attention tile parameters at fixed sequence lengths | No stable gain beyond run-to-run variance |
| H7 | Prefix-cache bookkeeping costs more than its 0.2% observed hit rate on this random workload | Trace/benchmark A/B with an implementation-level bypass | No repeatable gain or the bypass harms realistic reuse |
| H8 | Sampler compilation disablement creates a serial bottleneck | Decode trace and sampler microbenchmark | Sampler is negligible or its compiled path is slower/incorrect |

## Decision model

For a kernel or phase occupying fraction `f` of end-to-end time, an
optimization of that phase by fraction `s` has an Amdahl upper bound of
`f * s`. The competition gives no score to an end-to-end gain within 1%.
Candidate work should therefore start with phases where a plausible 20% local
gain can exceed the 1% global floor.

## Minimum shape set

- 4K prefill: aggregate approximately 28K to 32K query tokens.
- 4K decode: 64 active sequences with KV length near 4K.
- 16K prefill: aggregate approximately 28K to 32K query tokens.
- 16K decode: the measured steady active count, with KV length near 16K.

All kernel comparisons must use BF16 inputs, 16 query heads, 2 KV heads, head
dimension 128, and block size 16 unless the experiment explicitly studies a
layout change.
