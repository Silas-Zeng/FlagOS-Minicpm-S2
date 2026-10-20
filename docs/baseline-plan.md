# Baseline and bottleneck analysis plan

## Objective

Establish a reproducible single-card baseline before changing code, then
identify bottlenecks that can contribute at least one percentage point to
end-to-end throughput.

## Official workloads

| Name | `[input_len, output_len, concurrency, num_prompts]` |
|---|---|
| 4K | `[4096,1024,64,256]` |
| 16K | `[16384,1024,64,128]` |

The primary metric is `total tokens/s`. Mean TTFT and benchmark duration are
secondary diagnostics.

The official script hard-codes `RUNS=4` and `SKIP_FIRST=1`. Each of the 4K and
16K cases therefore executes four times, reports all four raw rows, and
averages the final three rows into the summary. A full two-case baseline is
expected to take several hours on BI-V150 even before profiling.

## Measurements

1. Freeze and record model, source, package, driver, environment, launch
   command, and benchmark-script hashes.
2. Run an HTTP smoke request before either performance case.
3. Run the official benchmark without editing its script.
4. Preserve the original summary CSV and complete service/benchmark logs.
5. Repeat around the 1% decision boundary; never compare concurrent runs.
6. Capture a short profiler window for 4K and 16K after the unprofiled
   baseline completes.

## Stage decomposition

- request arrival and queue wait;
- batch construction and scheduling;
- prefill;
- decode and per-output-token cost;
- sampling and detokenization;
- host/device synchronization and data movement;
- idle gaps between batches.

## Kernel decomposition

Record the operators representing at least 85% to 90% of cumulative device
time, including invocation count, average duration, tensor shape, dtype,
memory traffic, launches, and synchronization.

## Acceptance gate

An optimization remains a candidate only if it:

- preserves operator-level correctness and model behavior;
- passes the official accuracy gate;
- improves a scenario by more than the 1% ambiguity window;
- does not regress the other workload beyond the confirmed tolerance;
- is enabled through code under the fixed official launch arguments;
- has an ablation showing that the measured gain comes from the claimed
  mechanism.
