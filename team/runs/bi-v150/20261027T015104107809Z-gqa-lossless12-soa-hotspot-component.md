<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T015104107809Z-gqa-lossless12-soa-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #352 · 无损KV位编码与页内布局

- **尝试**：SoA完整组件慢355.51%，正确性通过；停止实现，保留真实位样本。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/archive-receipt.json)；[kv-bit-stats.json](../../../experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/kv-bit-stats.json)；[result.json](../../../experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/result.json)；[archive-receipt.json](../../../experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component/archive-receipt.json)；[archive-receipt.json](../../../experiments/framework/20261027T015640083939Z-gqa-lossless12-soa-hotspot-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原始结果、精确命令、环境、编译产物及收尾见原件。
- **结果**：无损KV页内SoA首包：整数提升32位后直接bitcast BF16被编译器拒绝，未获得GPU数值或计时结论。保留冻结包及失败日志；下一包只显式收为uint16再bitcast，不改框架/数学/容差。DB恢复和清理通过。
- **是否保留**：首包编译失败，保留；单行类型修正另run验证。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T015104107809Z-gqa-lossless12-soa-hotspot-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T015104107809Z",
  "profile_id": "kv-lossless",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "kv_soa_compile_failure",
  "artifacts": "experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component",
  "conclusion": "无损KV页内SoA首包：整数提升32位后直接bitcast BF16被编译器拒绝，未获得GPU数值或计时结论。保留冻结包及失败日志；下一包只显式收为uint16再bitcast，不改框架/数学/容差。DB恢复和清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T015104107809Z-gqa-lossless12-soa-hotspot-component](../../../experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
