# BI-V150 MiniCPM5-2B: generic attention and top-p candidates

Status: candidate passes microbenchmarks, end-to-end smoke tests, and the
official `math_500` Level 3 gate. Full official performance repetitions were
stopped by user direction after short validation had established the retained
direction.

All measurements in this note use the one visible BI-V150 on the rented
instance. GPU jobs were serialized.

## 1. Top-p sampler

The official model generation configuration resolves to:

```text
do_sample = true
temperature = 1.0
top_p = 0.95
top_k disabled
```

The upstream Qrita-style top-p-only kernel performs repeated bounded searches
over the 130,560-token vocabulary. In the candidate decode profile, the old
`_topk_topp_kernel` accounted for 5.301 ms per sampled decode iteration.

The replacement uses one split-parallel online `max + sum(exp)` pass followed
by two 256-bin weighted histogram zoom passes and one mask pass. The first
histogram narrows the threshold to a logit bin; the second uses the accumulated
mass above that bin to locate a conservative threshold. It never over-trims
mass in the tested distribution matrix.

### Kernel timing, `[64, 130560]` FP32

| Kernel path | Median |
|---|---:|
| Upstream top-p-only Triton kernel | 6.39 ms |
| Histogram candidate, two rounds, deterministic single split | 0.459 ms |
| Speedup | 13.9x |

The service profile confirms that the real shape is comparable:

| Candidate kernel | Calls | Total | Per call |
|---|---:|---:|---:|
| `_weighted_hist` | 8 | 1.108 ms | 0.138 ms |
| `_apply_mask` | 4 | 0.295 ms | 0.074 ms |
| `_row_stats_partial` | 4 | 0.291 ms | 0.073 ms |
| `_hist_walk` | 8 | 0.061 ms | 0.008 ms |
| `_row_max_reduce` | 4 | 0.020 ms | 0.005 ms |

The earlier four-split diagnostic reduced aggregate sampler filtering to
approximately 0.444 ms per decode iteration, versus 5.301 ms upstream. That
variant exposed floating-point atomic-order changes at batch 16/64, so the
submitted policy uses one program per row. The deterministic candidate remains
below 0.46 ms in the 64-row microbenchmark.

### Correctness gate

The matrix covered logit scales 0.5, 2.0, and 5.0 and top-p values 0.0, 0.5,
0.9, 0.95, 0.99, and 1.0, plus duplicate maxima and an all-`-inf` row.

- No expected probability mass was dropped in any passing case.
- At `top_p=0.95`, the maximum additional retained mass was `7.24e-5`.
- The worst case across all tested top-p values retained an additional
  `3.30e-4` probability mass; it retained no missing mass.
- Duplicate maxima at `top_p=0` both survived.
- An all-masked row remained all masked.
- With the final single-split kernel, the retained set was byte-identical
  across 20 repeated calls for batches 1, 8, 16, and 64 at logit scales 0.5,
  2.0, and 5.0.

## 2. Generic TRITON_ATTN prefill

The active path is vLLM's generic `unified_attention`, not FlagGems attention.
For MiniCPM5-2B prefill, the kernel shape is 16 query heads, 2 KV heads,
head size 128, and GQA factor 8.

The upstream launch heuristic selects `BLOCK_M=16`, KV tile 32, 4 warps, and
3 stages. A sweep found `BLOCK_M=128`, KV tile 64, 8 warps, and 1 stage.

### `[query=2048, kv=16384, block=16, batch=1]`

| Configuration | Median | Difference from reference |
|---|---:|---:|
| BM16 / tile32 / 4w / 3s | 75.43 ms | reference |
| BM128 / tile32 / 4w / 1s | 18.66 ms | 0 |
| BM128 / tile32 / 8w / 1s | 12.13 ms | 0 |
| **BM128 / tile64 / 8w / 1s** | **10.66 ms** | **4.88e-4** |
| BM128 / tile64 / 8w / 2s | 10.98 ms | 4.88e-4 |
| BM256 / tile128 / 8w / 1s | 13.27 ms | 4.88e-4 |

Best candidate: 7.08x faster.

### `[query=16384, kv=16384, block=16, batch=1]`

| Configuration | Median |
|---|---:|
| BM16 / tile32 / 4w / 3s | 318.24 ms |
| BM128 / tile32 / 8w / 1s | 50.43 ms |
| **BM128 / tile64 / 8w / 1s** | **44.70 ms** |
| BM128 / tile64 / 8w / 2s | 45.32 ms |
| BM256 / tile128 / 8w / 1s | 56.58 ms |

Best candidate: 7.12x faster. Maximum BF16 output difference from the
reference launch is `3.91e-3`.

### `[batch=8, query=2048, kv=16384, block=16]`

| Configuration | Median |
|---|---:|
| BM16 / tile32 / 4w / 3s | 593.18 ms |
| BM128 / tile64 / 8w / 1s | 83.37 ms |

Best candidate: 7.12x faster at batch 8.

### Decode experiment (rejected)

The real decode path uses 3D segmented softmax. For MiniCPM's GQA factor 8
and two KV heads, the launch threshold selects the 3D kernel at batch 64.

| Shape | Upstream BM16 / tile16 / 4w / 3s | Candidate BM16 / tile32 / 4w / 1s | Speedup |
|---|---:|---:|---:|
| batch64, kv4096 | 1.705 ms | 1.128 ms | 1.51x |
| batch30, kv16384 | 3.021 ms | 1.955 ms | 1.55x |

The 16K decode candidate's maximum BF16 output difference is `1.46e-3`.

This kernel-level gain was not accepted end to end. The exact organizer
`math_500 Level 3` run fell to **83.8%** and average output length increased
from about 3,345 to 10,996 tokens. The decode launch policy is therefore not in
the final default patch. It remains available as
`patches/candidates/vllm-plugin-FL-biv150-a-plus-b-rejected.patch` for A/B
comparison.

The selected prefill policy is limited to:

```text
vendor == iluvatar
head_size == 128
num_queries_per_kv == 8
```

Decode remains on the upstream policy.

## 3. End-to-end candidate results

### 16K diagnostic

Workload: 16,384 input tokens, 64 output tokens, concurrency 64, 64 prompts.

| Candidate combination | Duration | Total tok/s | Mean TTFT |
|---|---:|---:|---:|
| Histogram top-p only, earlier full-prefill service | 253.46 s | 4153.15 | 126.16 s |
| Attention + top-p from submitted-source patch path | 228.29 s | 4611.14 | 113.42 s |

This is a diagnostic shape, not the official 128-prompt/1024-output case.
Earlier baseline 16K official runs produced roughly 858-862 total tok/s and
mean TTFT around 637 s for 128 prompts and 128 output tokens. That comparison
is directional because prompt count and output length differ.

### 4K diagnostic

Workload: 4,096 input tokens, 256 output tokens, concurrency 64, 64 prompts,
seed 20261021.

| Candidate | Duration | Total tok/s | Mean TTFT | Mean TPOT |
|---|---:|---:|---:|---:|
| Top-p only | 138.00 s | 2018.34 | 38.68 s | 321.99 ms |
| Attention + top-p | 118.73 s | 2345.80 | 15.15 s | 333.18 ms |

The combined candidate improves total throughput by 16.2% and duration by
14.1% versus the same-seed short top-p-only run. Different service instances
were used, so this is a paired diagnostic rather than an official score.

### Accuracy

The exact organizer command scored **96.2%** on all 105 Level 3 samples with
the retained prefill-attention and deterministic top-p patch, starting from
the submitted plugin source path. This exceeds the required 0.95 threshold.

## 4. Rejected or invalid measurements

Non-operator settings were screened with the same pair of concurrent short
smokes: 4K with 16 requests and 16 output tokens, and 16K with 8 requests and
8 output tokens. These absolute numbers are integration measurements, not
official throughput scores, but each candidate is directly paired with the
default service.

| Setting | 4K tok/s | 16K tok/s | Decision |
|---|---:|---:|---|
| Default: block16, batched tokens 2048, prefix cache on | 5045.59 | 3554.45 | reference |
| KV block size 64 | 3154.38 | 3400.29 | reject |
| `max_num_batched_tokens=4096` | 1192.89 | 1628.14 | reject |
| `max_num_batched_tokens=8192` | 887.23 | 1729.07 | reject |
| Prefix cache disabled | 3170.73 | 3329.03 | reject |
| Sampler `torch.compile` enabled | 3131.36 | 3330.25 | reject |
| Same, warm compile cache | 3144.42 | 3535.92 | reject |

- The larger KV block has worse short-test throughput on both shapes.
- Raising the scheduler token cap to 8192 causes a severe regression with the
  two mixed concurrent clients; the device's 16-SM capacity makes the default
  2,048-token chunk more effective.
- The random benchmark reports 0% prefix-cache hits, but disabling the cache
  still performed worse in the paired smoke, so it remains enabled.
- An initial `math_500` run used zero temperature, a 2,048-token limit, and
  `/v1` instead of the organizer's explicit chat-completions endpoint. It
  produced 72.4%, but is retained only as a protocol-mismatch record and is not
  used as a candidate accuracy result.
- FlagGems paged FA2 remained slower than generic Triton end to end even after
  its own tile tuning and was not selected.
- Reusing the same diagnostic seed warmed the prefix cache and reduced a
  nominal 167 s run to 44 s. Those warm-cache runs are excluded from
  comparisons.
- A prior 16K/32-prompt run with the upstream attention launch stalled for
  hours at high GPU utilization. The optimized path completed the 64-prompt
  diagnostic without stalling.

## 5. Source integration

The submitted plugin adds:

- `vllm_fl/patches/biv150_top_p_triton.py`
- `vllm_fl/patches/biv150_runtime.py`
- an idempotent call from the Iluvatar backend module.

Starting from restored upstream vLLM files and setting `PYTHONPATH` to the
plugin worktree, the plugin:

1. monkey-patches top-p-only dispatch to the new Triton module;
2. applies the fixed vLLM 0.24 source hook for generic attention launch policy;
3. refreshes the imported `TRITON_ATTN` function reference;
4. records an idempotency marker in the patchable attention source.

The source-patched service started successfully and completed an 8-request
smoke with zero failures.
