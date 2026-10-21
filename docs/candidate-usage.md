# Candidate installation and verification

## Fixed base

The patch is based on:

```text
vllm-plugin-FL: flagos-2026-s2
base commit: 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0
vLLM: 0.24.0+empty
FlagGems: v5.3.5
```

Apply the submitted plugin patch:

```bash
git -C vllm-plugin-FL checkout 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0
git -C vllm-plugin-FL am /path/to/vllm-plugin-FL-biv150-performance.patch
pip install --no-build-isolation ./vllm-plugin-FL
```

The patch is idempotent and installs two shape-gated policies:

- generic `TRITON_ATTN` prefill:
  `BM128 / KV tile64 / 8 warps / 1 stage`;
- top-p-only sampling through a deterministic single-program,
  two-round weighted histogram kernel for the 130,560-token vocabulary.

The rejected A+B candidate (adding the faster decode tile policy) is retained
under `patches/candidates/` for comparison. It must not be used for the final
submission because its organizer accuracy result was 83.8%.

A fused top-p/Gumbel sampler is also retained as an independent candidate.
Its isolated tail is 2.38x faster, but its service-level short pair improved
16K while regressing 4K, so it is not enabled in the default patch. Its patch
is a delta that must be applied after the final plugin patch.

The attention policy only activates for:

```text
Iluvatar vendor
head size 128
16 query heads / 2 KV heads (GQA factor 8)
```

The sampler policy only activates for top-p-only, FP32 logits with the
MiniCPM5-2B vocabulary. All other paths retain the upstream implementation.

## Official serving command

```bash
export VLLM_PLUGINS=fl
vllm serve /workspace/MiniCPM5-2B \
  --port 9031 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --served-model-name minicpm \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072
```

## Accuracy

Use the exact organizer command recorded in
[`official-verification.md`](official-verification.md). The final run must
retain the specified endpoint, Level 3 subset, `temperature=1.0`,
`top_p=0.95`, and `max_tokens=32768`.

## Performance

Use the unmodified official benchmark:

```bash
cd /workspace
python3 /workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py \
  --model /workspace/MiniCPM5-2B \
  --served-model-name minicpm \
  --port 9031 \
  --test-cases '[[4096,1024,64,256],[16384,1024,64,128]]'
```

Do not reuse a short diagnostic'with the same seed' as a competition score:
prefix caching can reduce a warm run by more than 70%.
