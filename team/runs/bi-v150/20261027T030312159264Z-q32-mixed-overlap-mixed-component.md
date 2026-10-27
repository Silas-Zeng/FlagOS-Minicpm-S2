<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T030312159264Z-q32-mixed-overlap-mixed-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #356 · 当前Q32与GQA混合双流

- **尝试**：完整GPU耗时负，不进入生产，不扫形状或流优先级。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：完整原件、精确命令、环境与收尾证据已回收。
- **结果**：main241真实D63/P1985/KV4096，Q32 grid63×2，GQA自然S4/grid63×2×4。A串行、B原93c双流，完整writer+两路Attention/reducer+fork/join/event/record_stream/collect均计入。32calls ABBA Event 2.071281075478→2.185644984245ms
- **是否保留**：完整GPU耗时负，不进入生产，不扫形状或流优先级。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T030312159264Z-q32-mixed-overlap-mixed-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T030312159264Z",
  "profile_id": "q32-mixed-overlap",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "q32_mixed_overlap_negative",
  "artifacts": "experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component",
  "conclusion": "main241真实D63/P1985/KV4096，Q32 grid63×2，GQA自然S4/grid63×2×4。A串行、B原93c双流，完整writer+两路Attention/reducer+fork/join/event/record_stream/collect均计入。32calls ABBA Event 2.071281075478→2.185644984245ms，慢5.521409%；wall 2.222790375→2.211624625ms，省0.502330%，不一致且B两块波动大，无净收益。九项正确性检查全过，selected68/fallback1/pending最终0/峰值9；源码/native不变，DB恢复和清理通过。停止本实现，不证明实际共驻，不进生产。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T030312159264Z-q32-mixed-overlap-mixed-component](../../../experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
