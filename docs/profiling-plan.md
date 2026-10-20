# Profiling plan

## Purpose

Separate performance measurement from profiling. Official benchmark runs must
remain unmodified and must not include profiler overhead. Profiling uses a
separate service process with the same model, dtype, cache size, scheduler
settings, and compilation mode, plus vLLM's diagnostic `profiler-config`.

## Trace design

### Prefill

- Start the server with the official BI-V150 arguments plus the torch profiler
  configuration.
- Start profiling before the diagnostic load.
- Submit 64 concurrent requests at the target input length with a short output
  length.
- Capture five worker iterations. The first iterations contain chunked prefill
  work; output-length evaluation is not used as a performance result.

### Decode

- Submit exactly as many requests as the observed active concurrency so no
  queued requests are left.
- Wait until the engine log shows zero prompt throughput and steady running
  requests.
- Start profiling only after that point.
- Submit enough output tokens that the workload remains active during trace
  collection.
- For 4K, target concurrency is 64. For 16K, use the measured active request
  count, which is expected to be lower because the visible 32 GiB KV cache
  cannot hold 64 full 16K contexts.

## Trace settings

- Activities: CPU and CUDA/CoreX.
- Record tensor shapes and dtypes.
- Disable Python stack collection to limit trace size.
- Disable memory-event collection for timing traces; use separate allocation
  snapshots where needed.
- Limit automatic capture to five worker iterations.
- Persist the exact server command and profiler JSON in each trace directory.

## Primary tooling

- `start_profiled_server.sh` starts the profiler-enabled diagnostic server.
- `profile_control.sh start|stop|wait` controls the two official profiler
  HTTP endpoints.
- `profile_workload.py` sends exact-length token prompts without changing the
  official benchmark.
- `capture_profile_prefill.sh` and `capture_profile_decode.sh` are higher-level
  alternatives for repeatable phase capture.
- `stop_managed_server.sh` verifies the PID belongs to the expected MiniCPM
  vLLM process before sending SIGTERM.

## Derived evidence

For each phase, report:

- top kernels by cumulative device time and share;
- call count, mean and maximum duration;
- tensor shapes and dtypes;
- top CPU operators by self time;
- synchronization calls and launch-bound gaps;
- GEMM, attention, KV update, normalization, activation, rotary, sampling, and
  data-movement groups;
- cumulative-share and Amdahl ceilings for candidate optimizations.

## Safety and validity

- Profiler-enabled runs are never compared numerically with unprofiled runs.
- CPU and device timelines overlap, so their percentages must not be added.
- A trace is accepted only if the model, revision, workload shape, batch size,
  and compilation mode are recorded.
- The final serving command must not require `--profiler-config` or any new
  runtime option.
