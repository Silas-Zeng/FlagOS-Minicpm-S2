<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T145940Z-official-4k-control-on-merged-base

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #142 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：4096 / 1024 / 64 / 256。
- **结果**：合并基 87ed537 上、官方仪表（benchmark_throughput_serve.py 未改动，test-cases=[[4096,1024,64,256]]）、按用户要求两轮，kernel 显式关闭（VLLM_FL_BIV150_GQA_DECODE=0，marker installed False），GPU KV 521936
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T145940Z-official-4k-control-on-merged-base",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T14:59:40+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "official_4k_internal_two_rounds",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d3844f15677ebc657f93fb52536e7c1620c7c974",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "complete_two_rounds_control",
  "artifacts": "experiments/operator/20261022T145940Z-official-4k-control-on-merged-base",
  "conclusion": "合并基 87ed537 上、官方仪表（benchmark_throughput_serve.py 未改动，test-cases=[[4096,1024,64,256]]）、按用户要求两轮，kernel 显式关闭（VLLM_FL_BIV150_GQA_DECODE=0，marker installed False），GPU KV 521936。逐轮：第 1 轮 3678.51 tok/s（duration 356.32 s、TTFT 6320.60 ms、TPOT 80.38 ms），第 2 轮 3738.62（350.59 s、TTFT 4749.28、TPOT 80.53）。这是本实例上“团队合并基线、无本 kernel”的官方仪表水平，与队友官方 4K 3683.65 一致。注意它比缩放暖探针的控制（3787.49、TPOT 68.69）慢：探针 64 prompts 的总 token 量低于 KV 容量，不触发淘汰，而官方 256 prompts 必然触发。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T145940Z-official-4k-control-on-merged-base](../../../experiments/operator/20261022T145940Z-official-4k-control-on-merged-base)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
