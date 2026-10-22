<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T193500Z-team-main-warm-probe-gqa

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #125 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 1024 / 64 / 64。
- **结果**：相对 #124 得 +33.6%（4K）与 +24.9%（16K），两臂均用“丢第一轮取中位”同一口径，比值由 CSV 原始行直接相除
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T193500Z-team-main-warm-probe-gqa",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T19:35:00+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "warm_probe_4k_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "3be29805d9277b5b22b921dc6b7b48f7bd55cd54",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_matched_pair_candidate",
  "artifacts": "experiments/operator/20261022T193500Z-team-main-warm-probe-gqa",
  "conclusion": "同一实例、同一 prompt、同一公共基 87ed537，只开启本 kernel。缩放暖探针 4K 四个 repeat 4625.12 / 5058.23 / 5058.62 / 5055.46，丢第一轮取中位 = 5058.23 tok/s（全部中位 5056.84），TPOT 48.16 ms；16K 三个 repeat 3234.27 / 3234.10 / 3234.26，中位 3234.26，TPOT 56.38 ms。相对 #124 得 +33.6%（4K）与 +24.9%（16K），两臂均用“丢第一轮取中位”同一口径，比值由 CSV 原始行直接相除。markers 记录 installed True、rows 8、page_size 16、backend_rebound True，FIRST_WIDTH 显示 batch 64 时 builder 16 段实际切为 2 段（target_programs 256）。该收益是在已含 #9 w2s1 pin 的基线上测得的边际效果：本 kernel 不走 kernel_unified_attention 的启动路径，#9 的 warps/stages 对被接管的调用不叠加，两项收益不得相加。"
}
```

</details>

## 登记 #132 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 16。
- **结果**：相对 #124 得 +33.6%（4K）与 +24.9%（16K），两臂均用“丢第一轮取中位”同一口径，比值由 CSV 原始行直接相除
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T193500Z-team-main-warm-probe-gqa",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T19:35:00+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "warm_probe_16k_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "3be29805d9277b5b22b921dc6b7b48f7bd55cd54",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "16",
  "profiler": "false",
  "status": "complete_matched_pair_candidate",
  "artifacts": "experiments/operator/20261022T193500Z-team-main-warm-probe-gqa",
  "conclusion": "同一实例、同一 prompt、同一公共基 87ed537，只开启本 kernel。缩放暖探针 4K 四个 repeat 4625.12 / 5058.23 / 5058.62 / 5055.46，丢第一轮取中位 = 5058.23 tok/s（全部中位 5056.84），TPOT 48.16 ms；16K 三个 repeat 3234.27 / 3234.10 / 3234.26，中位 3234.26，TPOT 56.38 ms。相对 #124 得 +33.6%（4K）与 +24.9%（16K），两臂均用“丢第一轮取中位”同一口径，比值由 CSV 原始行直接相除。markers 记录 installed True、rows 8、page_size 16、backend_rebound True，FIRST_WIDTH 显示 batch 64 时 builder 16 段实际切为 2 段（target_programs 256）。该收益是在已含 #9 w2s1 pin 的基线上测得的边际效果：本 kernel 不走 kernel_unified_attention 的启动路径，#9 的 warps/stages 对被接管的调用不叠加，两项收益不得相加。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T193500Z-team-main-warm-probe-gqa](../../../experiments/operator/20261022T193500Z-team-main-warm-probe-gqa)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
