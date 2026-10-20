# BI-V150 official baseline: 2026-10-21

Status: **in progress**. The official benchmark is still running the four
repetitions required for each workload.

## Run identity

- Device run directory:
  `/workspace/experiments/minicpm-s2/baseline/20261020T161824Z`
- Started: `2026-10-20 16:18 UTC` (`2026-10-21 00:18 +08:00`)
- vLLM plugin commit:
  `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`
- FlagGems: `v5.3.5`, commit
  `4df52d9168ac55c1c1061cefb4638c570292d896`
- Device: one Iluvatar BI-V150, 32,768 MiB visible memory
- Workloads: official 4K `[4096,1024,64,256]` and 16K
  `[16384,1024,64,128]`

## Completed raw results

These values are raw repetitions, not the final three-run average.

| Workload | Raw run | Successful | Failed | Total tok/s | Output tok/s | Mean TTFT ms | Duration s |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4K | 1 | 256 | 0 | 1702.13 | 340.43 | 13664.92 | 770.05 |

## Preliminary evidence

- The first 4K raw run is 16.1% below the page's 4K reference throughput and
  19.1% slower in wall time. This is not yet a scoring conclusion because the
  first run is excluded from the official average and this platform exposes
  32 GiB.
- The second raw run is also 0 failures, with `1676.28 total tok/s`,
  `335.26 output tok/s`, `12781.48 ms` Mean TTFT, and `781.92 s` duration.
  The two runs differ by about 1.5% in total throughput.
- `Mean TTFT` is 13.7 seconds, while `Median TTFT` is 3.38 seconds. The large
  difference and `P99 TTFT` of 79.4 seconds show substantial queuing and
  head-of-line effects under the synchronized burst of 256 prompts.
- `Mean TPOT` is 167.32 ms. The aggregate generated-token rate corresponds to
  roughly 5.3 decode steps per second at 64 active sequences.
- GPU compute utilization samples are mostly 93% to 100%, so the current
  evidence does not support a simple "GPU idle because the scheduler is
  waiting" hypothesis. A torch trace is still required to separate memory,
  instruction, small-kernel, and synchronization costs.
- Board power samples are roughly 57% to 60% of the 350 W full-card cap. The
  visible device is a 32 GiB instance, so this must be interpreted with the
  actual partition policy.

## Engine timeline snapshot

The service-log snapshot collected during the first two 4K runs contains 198
engine samples. Of these, 92 are pure-decode windows and 103 contain prompt
work. Decode throughput normally rises to roughly 630-705 generated tok/s at
64 running requests. When the scheduler admits a batch of new 4K prompts,
decode throughput repeatedly drops to roughly 85-100 tok/s while prompt
throughput reaches roughly 2.4-3.3k tok/s. This alternating pattern indicates
that prefill admission materially interrupts active decode rather than being
fully hidden behind it.

GPU telemetry over the same broad interval contains 290 samples:

- compute utilization: mean 82.7%, p50 98%, p99 100%;
- board power: mean 186.8 W, p50 203 W, p99 214 W, maximum 215 W;
- allocated memory: constant 28,688 MiB of 32,768 MiB;
- active-GPU sample fraction: 85.2%.

The mean utilization includes model initialization, inter-run gaps, and
tail-drain periods. The p50 and p99 therefore provide better evidence than the
mean alone: while work is running, the GPU is usually busy but draws materially
less than the full 350 W board limit.

## Next evidence required

1. Finish all four raw runs for both workloads.
2. Import the original raw and summary CSV files plus service logs.
3. Capture a profiler-enabled diagnostic run with the same model, dtype,
   batch/token shapes, and official serving parameters.
4. Produce separate prefill and decode kernel rankings.
5. Measure candidate kernels against the original implementation before
   changing the serving path.
