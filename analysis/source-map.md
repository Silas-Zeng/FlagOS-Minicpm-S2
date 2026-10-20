# Source map for optimization work

All paths below refer to the pinned source revisions recorded under
`docs/environment-2026-10-21.md`.

## Model

- `/workspace/MiniCPM5-2B/config.json`
- Architecture: Llama-style dense decoder.
- Hidden size 2048, 42 layers, 16 query heads, 2 KV heads, head dimension
  128, intermediate size 6144, BF16.
- Query-to-KV head ratio: 8:1.

## vLLM plugin

- `vllm_fl/platform.py`
  - Sets the default paged-cache block size to 16 for this platform path.
  - Registers `vllm_fl.worker.worker.WorkerFL`.
- `vllm_fl/worker/worker.py`
  - Lazy torch/CUDA profiler creation.
  - `profile()` controls the HTTP profiler endpoints.
  - Iluvatar sampler compilation is explicitly unwrapped.
- `vllm_fl/dispatch/config/iluvatar.yaml`
  - Declared priority: FlagGems, Iluvatar vendor, reference.
- `vllm_fl/dispatch/backends/flaggems/flaggems.py`
  - `VLLM_FL_USE_FLAGGEMS_ATTN` defaults to false.
  - When false, attention resolves to vLLM `TRITON_ATTN`.
- `vllm_fl/dispatch/backends/flaggems/impl/attention.py`
  - Optional `AttentionFLBackend`.
  - Calls FlagGems `reshape_and_cache_flash` and
    `flash_attn_varlen_func`.
- `vllm_fl/dispatch/backends/vendor/iluvatar/iluvatar.py`
  - Vendor path also returns vLLM `TRITON_ATTN`.
  - Contains Triton compatibility patches and sampler compile disablement.

## FlagGems

- `src/flag_gems/ops/attention.py`
  - Generic full-attention kernels and `flash_attn_varlen_func`.
- `src/flag_gems/ops/flash_api.py`
  - Pure Triton paged/varlen attention dispatcher.
  - Single-token GQA swaps eight query groups into the sequence dimension.
  - Selects fixed `mha_block_*` heuristic configurations.
- `src/flag_gems/ops/flash_kernel.py`
  - `flash_varlen_fwd_kernel`; no autotune decorator on this kernel.
- `src/flag_gems/fused/reshape_and_cache_flash.py`
  - Paged KV write kernel.
- `src/flag_gems/runtime/backend/_iluvatar/heuristics_config_utils.py`
  - Current paged-attention configurations use `BLOCK_N=32`, four warps,
    three stages, and `BLOCK_M` from 16 through 128.
- `src/flag_gems/runtime/backend/_iluvatar/tune_configs.yaml`
  - Generic attention autotune candidates; not automatically proof that the
    paged varlen kernel is autotuned.

## Primary code-level hypothesis

The installed FlagGems Attention path is not active in the baseline because
the plugin opt-in defaults off. This is a verified code fact. Its performance
impact is unverified until the same-service A/B and trace analysis complete.
