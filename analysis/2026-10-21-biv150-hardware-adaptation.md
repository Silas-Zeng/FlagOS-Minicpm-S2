# BI-V150 hardware adaptation notes

## Verified hardware facts

The vendor documentation describes BI-V150 as an ivcore11, 7 nm accelerator
with HBM2e, PCIe 4.0 x16, and a 350 W board power limit:

<https://moark.com/docs/compute/clusters_gpu/iluvatar/iluvatar_BI-V150_gpu>

Important adaptation details from that page:

- the native warp size is 64 threads, not the 32-thread CUDA convention;
- global-memory accesses should be 128-byte aligned;
- FP32, FP16, and BF16 inference are supported;
- INT/FP8 paths have special toolchain requirements and are not part of this
  candidate.

The rented instance exposes 32 GiB and 16 compute units. The vendor page
describes a 64 GiB full-card configuration, so the local 32 GiB slice is the
capacity constraint that matters for this competition run.

## vLLM defaults observed in the pinned build

- chunked prefill is enabled;
- virtual/async scheduling is enabled;
- prefix caching is enabled;
- default `max_num_batched_tokens` is 2,048;
- 35 decode CUDA-graph sizes are captured, up to 512 requests.

The source paths are:

```text
/usr/local/lib/python3.12/site-packages/vllm/config/scheduler.py
/usr/local/lib/python3.12/site-packages/vllm/v1/core/sched/scheduler.py
/usr/local/lib/python3.12/site-packages/vllm/v1/attention/backends/triton_attn.py
```

## Short non-operator screens

All candidates were tested with the same pair of concurrent smokes: 4K with
16 requests/16 output tokens and 16K with 8 requests/8 output tokens.

| Setting | 4K tok/s | 16K tok/s | Decision |
|---|---:|---:|---|
| Default (`block16`, batch2048, prefix on) | 5045.59 | 3554.45 | keep |
| KV block 64 | 3154.38 | 3400.29 | reject |
| batched tokens 4096 | 1192.89 | 1628.14 | reject |
| batched tokens 8192 | 887.23 | 1729.07 | reject |
| prefix cache off | 3170.73 | 3329.03 | reject |

These are paired integration measurements, not official four-run scores.

## Interpretation

The BI-V150 slice behaves like a relatively small 16-SM device with a large
KV-capacity problem. Giving the scheduler larger token batches reduces
interactivity and did not improve aggregate work; the stock 2,048-token
scheduler window is already a better match. The 128-byte alignment rule does
not imply that larger KV pages are faster: 64-token pages were slower in both
short workloads.

The 0% prefix-cache hit rate does not mean the cache should be disabled. The
paired smoke became slower after disabling it, so hashing/metadata savings did
not offset the loss of cache-path optimizations.

The remaining non-operator candidates are lower confidence:

- reduce captured graph sizes to the official maximum concurrency of 64;
  this primarily reduces startup and graph memory, not measured token work;
- investigate page-table/host-device metadata copies after a focused profile
  shows they are material;
- test alternate CPU thread caps only if host throttling appears in profiling.

No further parameter scans were run after the five paired screens above.
