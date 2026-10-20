# Official page verification

Verified from
<https://flagos.io/race-detail-season2?id=539vlt2p&lang=cn> on
2026-10-20 Asia/Shanghai.

## Fixed inputs

- Model: `MiniCPM5-2B`
- Framework: `vllm-plugin-FL`, branch `flagos-2026-s2`
- Operator library: `FlagGems`, tag `v5.3.5`
- 4K workload: `[4096, 1024, 64, 256]`
- 16K workload: `[16384, 1024, 64, 128]`
- Accuracy: `math_500` Level 3, at least `0.95`, reference `0.962`
- Official accuracy sampling configuration:
  `temperature=1.0`, `top_p=0.95`, `max_tokens=32768`
- Official accuracy endpoint argument:
  `http://127.0.0.1:9031/v1/chat/completions`
- Official dataset argument:
  `{"math_500":{"dataset_id":"/workspace/evalscope-datasets/math_500","subset_list":["Level 3"]}}`
- Serving arguments: exactly the command listed on the official page for the
  selected platform

## Allowed changes

- KV Cache and memory management, including dynamic batching.
- Computation and kernels, including fusion and kernel rewrites.
- Self-developed quantization integrated into the framework.
- Scheduling, metadata, buffers, host/device interaction, and other end-to-end
  execution overhead.

## Prohibited changes

- Enabling existing quantization or speculative decoding by changing
  hyperparameters.
- Tuning the benchmark script.
- Switching an operator without an actual operator implementation change.
- Deleting the framework's principal operator selection logic.
- Merging a newer FlagOS framework branch for performance.
- Changing the model or making behavior incomparable.

## Submission

- `vllm-plugin-FL` source and build scripts are required.
- FlagGems is optional when there are no operator changes and required when
  operator changes are submitted.
- `report.pdf` and `readme.md` are required.
- The final archive is named after the team.

## Official accuracy command

```bash
evalscope eval \
  --model minicpm \
  --api-url http://127.0.0.1:9031/v1/chat/completions \
  --api-key EMPTY \
  --eval-type openai_api \
  --datasets math_500 \
  --dataset-args '{"math_500":{"dataset_id":"/workspace/evalscope-datasets/math_500","subset_list":["Level 3"]}}' \
  --eval-batch-size 8 \
  --timeout 3600 \
  --generation-config '{"temperature":1.0,"top_p":0.95,"max_tokens":32768}' \
  --work-dir /workspace/evalscope-datasets/level3 \
  --ignore-errors
```

## Open questions

The live page still contains incomplete bounds:

```text
total tokens/s 限制 (baseline-1%~, )
ttft限制 ( , ~baseline+1%)
```

Use the conservative engineering gate in `compliance-checklist.md`, but do not
describe it as the exact official formula. Also confirm whether a submission
with only one hardware platform receives zero performance score for the other
platform.
