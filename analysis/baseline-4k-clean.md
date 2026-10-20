# Official benchmark analysis

Generated from the unmodified official summary/raw CSV files.

The official script uses `RUNS=4` and `SKIP_FIRST=1`; variation below is
calculated from the final three raw runs.

## Summary

| Case | Total tok/s | Output tok/s | Mean TTFT ms | Mean TPOT ms | Duration s |
|---|---:|---:|---:|---:|---:|
| 4096/1024 c64 | 1875.62 | 375.12 | 12313.75 | 156.74 | 699.05 |

## Mean-request latency approximation

Estimated request latency is `Mean TTFT + (output_len - 1) * Mean TPOT`.
This removes batch queuing from the denominator and is a diagnostic proxy,
not a replacement for an engine timeline.

| Case | Estimated request ms | TTFT share | Decode share |
|---|---:|---:|---:|
| 4096/1024 c64 | 172658.77 | 7.13% | 92.87% |

## Run-to-run variation

| Case | Valid runs | CV total tok/s | CV TTFT | CV TPOT |
|---|---:|---:|---:|---:|
| 4096/1024 c64 | 3 | 1.82% | 0.43% | 1.15% |

## Interpretation limits

- TTFT includes queuing and does not isolate prefill kernel time.
- The latency approximation is based on mean values and does not model
  continuous batching overlap.
- Kernel-level conclusions require a separate profiler trace.
