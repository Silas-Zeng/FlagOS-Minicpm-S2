# Experiment queue

One BI-V150 device is available. Items marked `device` are serialized.

| Order | Status | Type | Experiment | Success condition |
|---:|---|---|---|---|
| 1 | partial | device | Official unmodified 4K/16K baseline, four runs per case | 4K complete; 16K two stable rows |
| 2 | complete | device | Capture prefill and steady-decode torch traces | Exact shapes and useful iterations captured |
| 3 | complete | CPU | Aggregate trace by kernel/operator/phase | Top kernels identified |
| 4 | rejected | device | Sweep FlagGems FA2 tile and KV block-size candidates | FlagGems remained slower end to end |
| 5 | accepted | device | Tune generic Triton attention launch policy | 7.1x prefill kernel gain; accuracy gate passed |
| 6 | complete | device | BF16 decode GEMM and memory-bandwidth microbenchmarks | Hardware floor recorded |
| 7 | accepted | device | Rewrite top-p-only sampler | 13.9x kernel gain; deterministic gate passed |
| 8 | partial | device | Run smoke, parity, 4K/16K diagnostics | Accuracy 96.2%; long official repetitions stopped by user request |
| 9 | rejected | device | Non-operator short screens | block64, batched-token 8192, no-prefix all slower |
| 10 | pending | CPU/device | Produce clean reproduction evidence and report material | Commands and artifacts are self-contained |

## Guardrails

- Stop the baseline server with `stop_managed_server.sh` only after the
  benchmark process has exited and its CSV/logs are sealed.
- Run `check_ready_for_experiment.sh` before any new GPU process.
- Profiler-enabled service arguments are diagnostic only.
- Do not claim a win from one run or from a profiler-enabled measurement.
