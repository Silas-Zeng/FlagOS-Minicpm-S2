# Scripts

Scripts under `remote/` are executed inside the FlagOS container.

## Baseline

- `bootstrap.sh`: capture the environment fingerprint.
- `start_official_baseline.sh`: start a detached official-argument server.
- `wait_ready.sh`: wait for the model API.
- `run_smoke.sh`: issue the official smoke request.
- `launch_official_benchmark.sh`: launch the full official benchmark in a
  detached process that survives SSH disconnection.
- `run_official_benchmark_job.sh`: wrapper that records start time, exit code,
  and finish time.
- `run_official_benchmark.sh`: run the unmodified official benchmark.
- `run_diagnostic_load.sh`: run one short diagnostic load with an optional
  explicit input seed.
- `run_short_repeats.sh`: run short loads with a distinct seed per repetition
  so prefix-cache reuse cannot masquerade as a performance gain.
- `run_math500_level3.sh`: evaluate the official Level 3 math subset through
  `evalscope` with zero temperature.
- `monitor_gpu.sh`: sample `ixsmi` utilization, memory, temperature, power, and
  clocks.

## Profiling

- `start_profile_server.sh`: diagnostic server with native vLLM torch
  profiler.
- `capture_profile_prefill.sh`: capture the first useful prefill iterations.
- `capture_profile_decode.sh`: wait for steady decode, capture a short window,
  then terminate only the diagnostic client.
- `profile_control.sh`: call vLLM's `/start_profile` and `/stop_profile`.
- `bench_attention_configs.py`: compare paged FlashAttention tile settings and
  verify output against the selected default configuration.
- `bench_triton_unified_attention.py`: scan generic `TRITON_ATTN` launch
  policies for the exact MiniCPM prefill shape.
- `bench_top_p_candidates.py` and `validate_biv150_top_p.py`: compare and gate
  histogram top-p kernels, including distribution and boundary cases.
- `bench_memory.py` and `bench_decode_gemm.py`: hardware-floor microbenchmarks.

## Result interpretation

The local `../scripts/analyze_*.py` programs produce Markdown/CSV summaries from
raw artifacts. They do not modify measurements.
