# First profiler analysis

These traces are diagnostic measurements. Their wall times include profiler
overhead and are not used as performance scores.

## 4K steady decode

Run: `b0-triton-4k-decode`

The trace contains four sampled decode iterations. The native profiler
reported:

| Kernel / operation | GPU time | Share of visible runtime kernels |
|---|---:|---:|
| `_topk_topp_kernel` | 21.204 ms | 71.68% |
| LM-head `linear_kernel` | 4.434 ms | 14.99% |
| `true_div_func_kernel_rank_2` | 1.272 ms | 4.30% |
| `true_div_func_kernel_rank_1` | 0.703 ms | 2.38% |
| softmax | 0.651 ms | 2.20% |
| Gumbel/exponential noise | 0.367 ms | 1.24% |
| argmax | 0.338 ms | 1.14% |
| bf16-to-fp32 copy | 0.346 ms | 1.17% |

The visible kernels total 29.58 ms. The transformer graph itself is executed
through captured CUDA graphs, so most model-layer kernels are not visible as
individual runtime events in this trace. The result is nevertheless decisive
for the post-logits path: top-p filtering dominates all visible device work.

Shape data shows 57-59 rows and a vocabulary of 130,560 for each decode step.
The filtering kernel performs many full-vocabulary bisection passes. This
creates a concrete candidate: fuse or replace top-p filtering and the sampler
tail with a bounded-pass histogram/zoom or threshold algorithm.

Profiler-instrumented CPU timings are inflated and are not treated as model
latency. The trace is used for call counts and relative device work.

## 16K prefill

Run: `b0-triton-16k-prefill`

Five diagnostic engine iterations produced 948 kernel events totaling
3.720 seconds of device time:

| Kernel / operation | GPU time | Share |
|---|---:|---:|
| `vllm::unified_attention_with_output` (`kernel_unified_attention`) | 3.4585 s | **92.96%** |
| `aten::mm` (`mm_kernel`) | 224.64 ms | 6.04% |
| Fused SiLU/multiply/slice | 11.54 ms | 0.31% |
| Fused residual RMSNorm | 6.83 ms | 0.18% |
| KV-cache reshape/write | 2.54 ms | 0.07% |

The profiled prefill chunk contains 2048 query tokens with 16 query heads,
2 KV heads, and head size 128. The generic attention kernel constitutes almost
the entire device timeline. This is direct evidence that 16K prefill attention
is the primary optimization target, not a static-code assumption.

The earlier engine timeline also shows that the 32 GiB cache admits roughly
30 simultaneous 16K sequences. Any candidate that changes cache capacity must
be compared at the same effective concurrency.

## Selected kernel tuning

A same-shape paged FlashAttention microbenchmark on the GPU produced:

- 4K-like decode (`batch=64`, `seq_len=4096`, GQA 16Q/2KV/head128):
  - original heuristic BM16/BN32/w4/s3: about 2.092 ms;
  - tuned BM8/BN32/w4/s1: about 1.092 ms;
  - 4K cache block sizes 16, 64, and 128 changed the result by less than 2%.
- 2048-token prefill chunk:
  - original BM128/BN32/w4/s3: about 2.658 ms;
  - tuned BM128/BN64/w8/s1: about 1.078 ms.

All tested candidates returned finite output and differed from the reference
configuration by at most about `0.0039` on random BF16 attention. The exact
GQA8 16Q/2KV GPU test suite also passed 14 tests.

These microbenchmark gains are kernel-level only. They do not establish an
end-to-end gain until the same service workload is compared.
