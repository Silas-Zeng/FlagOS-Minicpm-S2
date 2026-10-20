# Measurement log

The primary timestamp is UTC. The parenthesized value is Asia/Shanghai
(UTC+8), the timezone used for experiment planning.

## 2026-10-21

- `2026-10-20 16:11 UTC (2026-10-21 00:11 +08:00)`: SSH verified against the
  FlagOS instance.
- `16:12 UTC (00:12 +08:00)`: `ixsmi` verified one Iluvatar BI-V150 with
  32,768 MiB memory.
- `16:15 UTC (00:15 +08:00)`: environment snapshot written under
  `/workspace/experiments/minicpm-s2/environment/20261020T161500Z`.
- `16:16 UTC (00:16 +08:00)`: official service reached `/v1/models`; full decode CUDA graphs
  captured; KV cache capacity reported as 521,936 tokens.
- `16:17 UTC (00:17 +08:00)`: official smoke request returned a valid response.
- `16:18 UTC (00:18 +08:00)`: unmodified official 4K/16K benchmark started in run directory
  `/workspace/experiments/minicpm-s2/baseline/20261020T161824Z`.
- `16:19 UTC (00:19 +08:00)`: GPU sampling began into the same run directory.
- `16:23 UTC (00:23 +08:00)`: confirmed the official benchmark hard-codes four runs per case and
  skips the first run when averaging.
- `16:30 UTC (00:30 +08:00)`: 4K run 1 still active; GPU was approximately 99% compute busy,
  28.7 GiB allocated, 50 C, with low GPU power draw relative to its cap.
- `16:34 UTC (00:34 +08:00)`: 4K run 1 completed with 256 successful requests,
  0 failures, `total tok/s=1702.13`, `output tok/s=340.43`,
  `Mean TTFT=13664.92 ms`, and benchmark duration `770.05 s`.
- `16:38 UTC (00:38 +08:00)`: container limits confirmed as 20 GiB memory and
  a six-CPU platform allocation. The host exposes more CPUs and memory to the
  container namespace; final reports should use the subscription limits, not
  host totals.

## Initial observations

- The container has one card, not two.
- The visible accelerator reports 32,768 MiB rather than the 64 GB full-card
  specification. The score comparison must retain this environment fact.
- The official framework revision is correct even though the local checkout is
  named `main`.
- Full decode graph capture consumes a substantial portion of the 32 GiB card:
  the running service holds about 28.7 GiB.
- Baseline measurement duration is dominated by four repetitions per workload.
- The first 4K run took 19.1% longer and delivered 16.1% lower total throughput
  than the public page reference (`2028.01 total tok/s`, `646.31 s`). This is
  one raw run and must not be presented as the official four-run baseline.
- During the measured 4K workload, sampled GPU compute utilization was usually
  93% to 100%, while board power was approximately 199 W to 211 W for the
  32,768 MiB BI-V150 instance. This makes a pure idle/queueing explanation
  unlikely and motivates kernel-level tracing.
