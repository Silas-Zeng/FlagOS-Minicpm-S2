# Preliminary clean 16K baseline

Status: first clean repetition only. The official summary excludes this run.

| Metric | Local clean run 1 | Public TianShu reference | Difference |
|---|---:|---:|---:|
| Successful requests | 128 | 128 | 0 |
| Benchmark duration | 2596.73 s | 2434.82 s | +6.65% |
| Total tok/s | 858.09 | 915.15 | -6.23% |
| Output tok/s | 50.48 | 53.83 | -6.22% |
| Mean TTFT | 639267.43 ms | 599262.03 ms | +6.68% |
| Mean TPOT | 520.68 ms | not published | - |

The local 16K total/output throughput is about 2.3 times lower than the clean
4K baseline, while mean TPOT grows from 156.74 ms at 4K to 520.68 ms at 16K.

The first run admitted roughly 30-31 active requests despite client concurrency
64. The remaining 33-34 requests waited for KV-cache capacity. This is a
structural difference from the 4K workload and must remain fixed during local
A/B experiments.

This single result is not yet the official three-run baseline. It establishes
that the largest observed end-to-end tail is in 16K TTFT and decode, not merely
in generic queue setup.
