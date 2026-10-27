<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T031858174112Z-sampler-preprocess-stats-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #358 · 采样转换与首遍统计融合

- **尝试**：v2首组统计逐位门失败，停止；无性能计时，完整原件待回收。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component/archive-receipt.json)；[ssh-readback-summary.json](../../../experiments/framework/20261027T031858174112Z-sampler-preprocess-stats-component/ssh-readback-summary.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：仅已读回摘要在本地，完整原件仍在实验机；恢复SSH后回收，不重测。
- **结果**：采样融合v2仅修main241源码入口，真实head首组scaled/filtered/sampled IDs、global/per-request RNG、输入及独立CPU FP64转换均通过，但stats_bitwise=false，按预定门停止；timings为空，后续换值/Graph/性能未运行。不能称原main框架报错或已造成预测错误，也不接受为等价候选。03:19:
- **是否保留**：停止当前实现，无性能或官方资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T031858174112Z-sampler-preprocess-stats-component",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T03:18:58.174112+00:00",
  "profile_id": "sampler-preprocess-stats",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "sampler_stats_equality_failed_raw_pending",
  "artifacts": "experiments/framework/20261027T031858174112Z-sampler-preprocess-stats-component",
  "conclusion": "采样融合v2仅修main241源码入口，真实head首组scaled/filtered/sampled IDs、global/per-request RNG、输入及独立CPU FP64转换均通过，但stats_bitwise=false，按预定门停止；timings为空，后续换值/Graph/性能未运行。不能称原main框架报错或已造成预测错误，也不接受为等价候选。03:19:32 UTC收尾，DB恢复、source/native不变。结果已通过SSH读到；随后网关仅提供publickey且拒绝原密钥，完整原件暂留实验机，未伪造归档回执。停止本实现，不改容差/数学或继续变体。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T031858174112Z-sampler-preprocess-stats-component](../../../experiments/framework/20261027T031858174112Z-sampler-preprocess-stats-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
