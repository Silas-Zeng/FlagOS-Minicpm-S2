<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #479 · Prefill i32 offset 组件筛查

- **尝试**：同ABI对比原kernel与i32相对offset kernel，单shape ABBA。
- **改动**：正确性门通过（FP64采样），Event慢10.63%、wall慢10.21%；停止候选，不进生产。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-i32-offset.md)。
- **怎么测**：BI-V150私有单shape attention组件；完整输出/Graph等门及ABBA通过，FP64仅采样；不代表完整模型或官方吞吐。
- **结果**：M2048/KV16384单层组件正确性门通过（FP64采样）；ABBA Event 8.347575→9.235266ms（+10.63%），wall 8.441216→9.303357ms（+10.21%）。
- **是否保留**：保留正确性与负性能证据，停止i32候选，不接入生产或官方。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T01:09:50.054874+00:00",
  "profile_id": "prefill-i32-offset",
  "phase": "component_abba",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b3b87d2a1c13448bd8c6bc24e8045c0458b8b9dd",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "prefill_i32_component_negative",
  "artifacts": "experiments/bundles/20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component",
  "conclusion": "i32相对offset候选在单层M2048/KV16384组件通过既定数值门，但ABBA慢于baseline：Event每调用8.347575→9.235266ms（+10.63%），wall 8.441216→9.303357ms（+10.21%）。负向停止，不接入生产。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component](../../../experiments/bundles/20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
