<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T191500Z-team-main-warm-probe-control

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #124 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 1024 / 64 / 64。
- **结果**：KV 相差 96 tokens（521840 对 521936，0.018%）
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T191500Z-team-main-warm-probe-control",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T19:15:00+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "warm_probe_4k_control",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "87ed53719126208eaa9ba1cab698b14a5693eb5d",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_matched_pair_control",
  "artifacts": "experiments/operator/20261022T191500Z-team-main-warm-probe-control",
  "conclusion": "公共基线 = 团队 main 87ed537（#1–#11 已合并），本 kernel 由 VLLM_FL_BIV150_GQA_DECODE 关闭，install-markers.txt 记录 installed False，GPU KV 521840 tokens。仪表是 scripts/probe_bench.py 的缩放暖探针（不是官方四轮），4K case 4096x1024x64x64 共 4 个 repeat：3533.66 / 3798.15 / 3784.87 / 3787.49，丢第一轮取中位 = 3787.49 tok/s（全四轮中位 3786.18），TPOT 68.69 ms；16K case 16384x1024x64x16 共 3 个 repeat：2590.06 / 2589.05 / 2589.32，中位 2589.32，TPOT 76.41 ms。原件为本目录两份 CSV。与候选臂的唯一差别是这一个补丁与这一个 env；KV 相差 96 tokens（521840 对 521936，0.018%）。"
}
```

</details>

## 登记 #131 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 16。
- **结果**：KV 相差 96 tokens（521840 对 521936，0.018%）
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T191500Z-team-main-warm-probe-control",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T19:15:00+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "warm_probe_16k_control",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "87ed53719126208eaa9ba1cab698b14a5693eb5d",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "16",
  "profiler": "false",
  "status": "complete_matched_pair_control",
  "artifacts": "experiments/operator/20261022T191500Z-team-main-warm-probe-control",
  "conclusion": "公共基线 = 团队 main 87ed537（#1–#11 已合并），本 kernel 由 VLLM_FL_BIV150_GQA_DECODE 关闭，install-markers.txt 记录 installed False，GPU KV 521840 tokens。仪表是 scripts/probe_bench.py 的缩放暖探针（不是官方四轮），4K case 4096x1024x64x64 共 4 个 repeat：3533.66 / 3798.15 / 3784.87 / 3787.49，丢第一轮取中位 = 3787.49 tok/s（全四轮中位 3786.18），TPOT 68.69 ms；16K case 16384x1024x64x16 共 3 个 repeat：2590.06 / 2589.05 / 2589.32，中位 2589.32，TPOT 76.41 ms。原件为本目录两份 CSV。与候选臂的唯一差别是这一个补丁与这一个 env；KV 相差 96 tokens（521840 对 521936，0.018%）。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T191500Z-team-main-warm-probe-control](../../../experiments/operator/20261022T191500Z-team-main-warm-probe-control)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
