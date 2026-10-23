<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T151533Z-official-4k-default-on-merged-base

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #143 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：4096 / 1024 / 64 / 256。
- **结果**：稳态对 #新控制行 3738.62 为 **+31.2%**，首轮对首轮 +30.5%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T151533Z-official-4k-default-on-merged-base",
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
  "status": "complete_two_rounds_default_on",
  "artifacts": "experiments/operator/20261022T151533Z-official-4k-default-on-merged-base",
  "conclusion": "同一实例、同一官方仪表、同一公共基，只把 kernel 交给默认开启（不带任何 VLLM_FL_*），GPU KV 521936（与控制臂相同）。逐轮：4801.28 tok/s（272.99 s、TTFT 6195.02、TPOT 60.25）与 4906.39（267.15 s、TTFT 4641.95、TPOT 60.35）。稳态对 #新控制行 3738.62 为 **+31.2%**，首轮对首轮 +30.5%；TTFT 4641.95 对 4749.28（-2.3%）、TPOT 60.35 对 80.53（-25.1%）。与更早快照的官方四轮 4809.36 同水平（差 2.0%）。这是本 kernel 在 4K 上最可信的因果证据：同机、同仪表、同 KV、只差一个开关。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T151533Z-official-4k-default-on-merged-base](../../../experiments/operator/20261022T151533Z-official-4k-default-on-merged-base)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
