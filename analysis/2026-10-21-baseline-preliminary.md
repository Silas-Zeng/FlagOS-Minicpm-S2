# Preliminary 4K baseline analysis

Status: first warm-up run only. The official script skips this row when
computing its summary, so it must not be presented as the final baseline.

## Result

| Metric | Local run 1 | Published TianShu reference | Difference |
|---|---:|---:|---:|
| Successful requests | 256 | 256 | 0 |
| Benchmark duration | 770.05 s | 646.31 s | +19.15% |
| Total tok/s | 1702.13 | 2028.01 | -16.07% |
| Output tok/s | 340.43 | 405.60 | -16.07% |
| Mean TTFT | 13,664.92 ms | 11,573.53 ms | +18.07% |

The ratio between total and output throughput is approximately five, matching
the 4:1 input-to-output token ratio of the official case. This confirms that
`total tokens/s` includes both prompt and generated tokens.

## Engine phases

The service log was sampled once per 10 seconds. Within the first run:

- 39 samples had prompt work, with mean prompt throughput 2688.44 tok/s.
- 39 samples had only decode work, with mean generation throughput 531.50 tok/s.
- Four workload waves were visible, corresponding to 256 prompts at client
  concurrency 64.
- The last decode tail lasted approximately 160 seconds while concurrency fell
  toward zero, contributing materially to the low aggregate throughput.

These samples demonstrate overlap between prompt processing and decode during
the first part of each wave, followed by a decode-only tail. They are wall-clock
categories, not additive GPU kernel times.

## GPU telemetry

Across the first run and the beginning of the next run:

- mean GPU utilization: 78.55%;
- median GPU utilization: 98%;
- mean allocated memory: 28,688 MiB of 32,768 MiB;
- mean GPU power: 82.7 W, median 91 W;
- mean board power: 194.4 W of a 350 W board cap;
- temperature remained near 46-51 C.

The device is usually compute-busy during a wave, but the sub-100 W GPU draw at
high reported utilization suggests serialized/tail work rather than saturation
of the whole board. The 3.2 GiB free-memory margin limits aggressive cache
expansion.

## Immediate hypotheses

1. Decode dominates per-request latency: the measured mean TPOT is 167.32 ms
   before including the first token.
2. TTFT has a severe tail: median is 3.38 s but p99 is 79.44 s. Scheduling,
   chunked prefill, and wave formation need timeline inspection.
3. The final 64-request wave has a long trailing decode period. Optimizing
   decode kernels and reducing small-kernel/launch overhead should improve the
   4K aggregate.
4. The 16K case still needs its own trace; its 16:1 token ratio and long
   sequence length are expected to shift the bottleneck toward prefill
   attention.

## Evidence

- `experiments/20261020T161824Z/raw-runs-progress.csv`
- `experiments/20261020T161824Z/server-progress.log`
- `experiments/20261020T161824Z/engine-run1.csv`
- `experiments/20261020T161824Z/gpu-progress.csv`

The progress files are snapshots captured while the benchmark was still
running. Final sealed copies will replace them after all four repetitions.
