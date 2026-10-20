# External evidence and transferability

This note separates public claims from reproduced measurements.

## Official and first-party references

- FlagOS race page:
  <https://flagos.io/race-detail-season2?id=539vlt2p&lang=cn>
- BI-V150 adaptation PR, including the 32 GiB device and CoreX 4.5.0
  environment:
  <https://github.com/flagos-ai/vllm-plugin-FL/pull/310>
- Official operator-profile workflow:
  <https://github.com/Silas-Zeng/vllm-plugin-FL/tree/main/tools/operator_profile>
- Iluvatar BI-V150 vendor description:
  <https://moark.com/docs/compute/clusters_gpu/iluvatar/iluvatar_BI-V150_gpu>

## Public related project

<https://github.com/SOLECA794/minicpm5-2b-infer-opt-flagos>

The project identifies the same default-off FlagGems attention adapter and
proposes measuring it before making a performance claim. Its illustrative
optimized CSV is not a reproducible measurement from this device and is not
used as evidence.

## Independently verified here

- The instance exposes one BI-V150 with 32,768 MiB.
- CoreX is 4.5.0; the active FlagTree Triton version is 3.6.0.
- The source commit is the official `flagos-2026-s2` commit `13eb9be`.
- FlagGems is tag `v5.3.5`, commit `4df52d91`.
- `VLLM_FL_USE_FLAGGEMS_ATTN` defaults to false, so the baseline resolves to
  `TRITON_ATTN`.
- Official FLASH_ATTN-2 adapter code and paged KV implementation are present.
- The current 32 GiB KV cache capacity is 521,936 tokens. At 16K per request,
  the scheduler admits about 30-31 requests despite client concurrency 64.

## Transferable candidates

1. Tune the FlagGems paged attention kernel for 16Q/2KV/head-dim 128 on
   BI-V150 and use that optimized implementation to replace the generic path.
2. Evaluate larger paged-cache blocks to reduce block-table and indexing
   overhead, while preserving the fixed serving arguments.
3. Profile sampling; the plugin disables sampler compilation on Iluvatar even
   though this image reports Triton 3.6.0 and a working target.
4. Fuse RoPE with KV-cache writes or fused residual RMSNorm only if profiles
   show sufficient end-to-end share.

## Claims not accepted as proven

- That attention alone explains every gap between BI-V150 and C500.
- That a FlagGems attention switch improves either workload on this image.
- That the optimum tile is the current BM8 candidate.
- That block-size or sampler changes improve end-to-end throughput.
- Any synthetic or illustrative result in a third-party repository.
