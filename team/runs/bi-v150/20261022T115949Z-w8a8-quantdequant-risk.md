<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T115949Z-w8a8-quantdequant-risk

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #129 · int8 与 W8A8 决策测量

- **尝试**：真实形状上的 int8 GEMM、W8A16、_int_mm+融合 epilogue 及 QDQ 精度模拟；负结果与候选并存，不混用证据级别。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：准确率门；输入 / 输出 / 并发 / 请求数：0 / 0 / 8 / 24。
- **结果**：teacher-forcing PPL（同脚本 --sweep scheme，105 篇 Level-3、22528 token）对 per-channel 与分组 32/64/128、含或不含激活量化都落在 bf16 的 ±0.15% 内，无法作为筛选指标
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T115949Z-w8a8-quantdequant-risk",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T11:59:49+00:00",
  "profile_id": "int8_decision",
  "phase": "accuracy_offline_greedy",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "0",
  "output_len": "0",
  "concurrency": "8",
  "num_prompts": "24",
  "profiler": "false",
  "status": "complete_offline_accuracy_screen",
  "artifacts": "experiments/operator/20261022T115949Z-w8a8-quantdequant-risk",
  "conclusion": "真实 checkpoint 的 294 个线性层做 QDQ（fp32 量化-反量化、bf16 矩阵乘；与 int32 累加等价但多一次 bf16 取整，偏保守），24 道 Level-3 greedy、1024 新 token、batch 8、单次加载逐臂还原权重。gold：bf16 14、只量化权重 13、W8A8 per-channel+per-token 11、权重分组 128 为 12（每臂都有 7 题在 1024 token 内没写完答案，所以 gold 不是最终精度）。与 bf16 的最终答案一致率：只量化权重 0.95833（1 题翻转）、W8A8 0.875（3 题）、分组 128 0.91667（2 题）；前 64 token 逐位一致率 0.754 / 0.566 / 0.564。损伤来自激活量化而非权重粒度。teacher-forcing PPL（同脚本 --sweep scheme，105 篇 Level-3、22528 token）对 per-channel 与分组 32/64/128、含或不含激活量化都落在 bf16 的 ±0.15% 内，无法作为筛选指标。不保留为精度结论，只作为下一轮缓解实验依据。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T115949Z-w8a8-quantdequant-risk](../../../experiments/operator/20261022T115949Z-w8a8-quantdequant-risk)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
