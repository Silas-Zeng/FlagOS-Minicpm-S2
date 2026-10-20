# Experiment queue

One BI-V150 device is available. Items marked `device` are serialized.

| Order | Status | Type | Experiment | Success condition |
|---:|---|---|---|---|
| 1 | running | device | Official unmodified 4K/16K baseline, four runs per case | Complete original raw CSV and service log |
| 2 | prepared | device | Capture prefill and steady-decode torch traces | Trace includes exact shapes and at least five useful iterations |
| 3 | prepared | CPU | Aggregate trace by kernel/operator/phase | Top kernels explain at least 85% and 90% cumulative device time |
| 4 | prepared | device | Sweep FlagGems FA2 tile and KV block-size candidates | Repeatable local gain; all output parity checks pass |
| 5 | prepared | device | Compare generic Triton attention with diagnosed FlagGems path | Faster on the same shape and no correctness regression |
| 6 | prepared | device | BF16 decode GEMM and memory-bandwidth microbenchmarks | Establish whether small-M GEMM or HBM is the actual ceiling |
| 7 | pending | device | Implement the best legal kernel or layout optimization | End-to-end gain exceeds the 1% ambiguity window |
| 8 | pending | device | Run smoke, parity, 4K/16K A/B, then full official benchmark | Accuracy and performance gates pass |
| 9 | pending | CPU/device | Produce clean reproduction evidence and report material | Commands and artifacts are self-contained |

## Guardrails

- Stop the baseline server with `stop_managed_server.sh` only after the
  benchmark process has exited and its CSV/logs are sealed.
- Run `check_ready_for_experiment.sh` before any new GPU process.
- Profiler-enabled service arguments are diagnostic only.
- Do not claim a win from one run or from a profiler-enabled measurement.
