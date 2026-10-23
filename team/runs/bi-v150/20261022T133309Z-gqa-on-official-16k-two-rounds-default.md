<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T133309Z-gqa-on-official-16k-two-rounds-default

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #134 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 128。
- **结果**：对 #126 控制臂同口径稳态 2734.40 为 +23.3%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T133309Z-gqa-on-official-16k-two-rounds-default",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T13:33:09+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "official_16k_internal_two_rounds",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "53635f29b38c172f8a74f327ba67955c47963ab5",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "false",
  "status": "complete_two_rounds_default_on",
  "artifacts": "experiments/operator/20261022T133309Z-gqa-on-official-16k-two-rounds-default",
  "conclusion": "默认开启门验证：只用官方命令（仅 VLLM_PLUGINS=fl，无任何 VLLM_FL_*）启动，manifest 记录 BIV150_GQA_DECODE_INSTALL installed True、rows 8、page_size 16、backend_rebound True、GPU KV 521936 tokens。同一官方仪表、两轮：第 1 轮 3341.90（duration 666.75 s）、第 2 轮 3371.88 total tok/s；逐轮 TTFT 157971.44 / 155019.71 ms（两轮均值 156495.58），逐轮 TPOT 133.06 / 133.06 ms。对 #126 控制臂同口径稳态 2734.40 为 +23.3%。这与 #125 缩放暖探针的 +24.9% 一致，与更早快照的官方四轮 3364.03 同量级。证据级别：官方仪表、两轮。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T133309Z-gqa-on-official-16k-two-rounds-default](../../../experiments/operator/20261022T133309Z-gqa-on-official-16k-two-rounds-default)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
