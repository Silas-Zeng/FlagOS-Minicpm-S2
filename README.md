# FlagOS S2 MiniCPM5-2B throughput optimization

This repository is the reproducible experiment record for the FlagOS Season 2,
Track 2 task. It is intentionally separate from any existing source repository.

## Current environment

- Date established: 2026-10-21 (Asia/Shanghai)
- Platform: Iluvatar BI-V150
- Visible accelerator count: 1
- Device memory: 32,768 MiB
- Runtime: CoreX 4.5.0
- Model: `/workspace/MiniCPM5-2B`
- Framework: `/workspace/vllm-plugin-FL`
- Operator library: `/workspace/FlagGems` at tag `v5.3.5`

The instance currently exposes one GPU. All device experiments therefore use a
single experiment queue. Source analysis and test preparation can still run in
parallel.

## Rules baseline

- Use only MiniCPM5-2B.
- Use `vllm-plugin-FL` branch `flagos-2026-s2` and FlagGems `v5.3.5`.
- Keep the official `vllm serve` arguments unchanged.
- Do not tune the benchmark script or use benchmark-specific shortcuts.
- Do not enable pre-existing quantization or speculative decoding by changing
  hyperparameters.
- Every optimization reported in the final report must be present and enabled
  in the submitted code.
- `math_500` Level 3 accuracy must be at least 0.95.
- Final ranking uses reproducibility by the organizers.

## Layout

- `docs/`: rules, environment records, experiment methodology.
- `scripts/`: local and remote automation.
- `experiments/`: baseline and optimization evidence.
- `analysis/`: profiler summaries and bottleneck conclusions.

Raw device results are first written to
`/workspace/experiments/minicpm-s2/` on the FlagOS instance and then summarized
here. Large profiler traces should remain outside Git and be referenced by
path, hash, and summary.
