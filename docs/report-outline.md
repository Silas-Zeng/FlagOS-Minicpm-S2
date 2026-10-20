# Technical report outline

## 1. Task and constraints

- Model, framework revisions, accelerator, and fixed serving command.
- 4K and 16K workloads; total-token throughput as the primary metric.
- TTFT and `math_500` Level 3 gates.
- Separation of public reference values from locally measured baselines.

## 2. Reproducible environment

- Host and accelerator fingerprint.
- Software and package versions.
- Source commits, model hash, benchmark-script hash.
- One-card versus two-card availability and the actual 32 GiB device partition.
- Detached execution method and why foreground-session loss invalidated the
  first run.

## 3. Baseline results

- Four raw repetitions per workload and the official three-run average.
- Throughput, TTFT, TPOT, duration, success rate, and run-to-run variation.
- Per-run CUDA graph capture, KV-cache capacity, and peak memory.
- Local baseline versus the public reference, without treating them as directly
  interchangeable hardware states.

## 4. Bottleneck analysis

- End-to-end engine timeline: mixed prefill/decode, decode-only, capacity wait,
  and idle tail.
- GPU utilization, memory, temperature, power, and clocks.
- Prefill and decode operator/kernel rankings with cumulative shares.
- Host/device gaps, synchronization, and small-kernel counts.
- Amdahl ceiling for each candidate.

## 5. Optimization design

- The flagged observation, causal evidence, and rejected alternatives.
- Exact source change and the general property it improves.
- Why the optimization is not merely routing to another pre-existing operator.
- Numerical correctness argument and fallback behavior.

## 6. Ablation

- B0: original Triton attention.
- A1: unmodified FlagGems FA2.
- A2: tuned BI-V150 GQA8 kernel.
- Optional independent changes for cache layout or sampler behavior.
- Same-card, same-command comparisons with repeated measurements.

## 7. Final validation

- Official 4K and 16K results.
- TTFT and throughput acceptance checks.
- `math_500` Level 3 result.
- Two-card reproducibility, where applicable.
- Clean rebuild and reproduction instructions.

## 8. Limitations and conclusion

- Public-threshold ambiguities.
- Differences between this 32 GiB instance and other official partitions.
- Negative results and rejected configurations.
- Final contribution summary and applicability.
