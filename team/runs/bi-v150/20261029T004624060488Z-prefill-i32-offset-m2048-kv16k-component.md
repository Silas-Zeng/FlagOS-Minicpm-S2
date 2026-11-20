<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #477 · Prefill i32 offset 组件筛查

- **尝试**：修复依赖接线后捕获组件scope并执行原固定scope断言。
- **改动**：断言不符后停止；无A/B数值/性能结果，不据此判候选。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-i32-offset.md)。
- **怎么测**：BI-V150私有单层组件；未形成A/B结果，source/native/GQA/DB恢复。
- **结果**：组件在scope断言停止；worker预设配置与当时selected compile scope不符，未进入A/B、数值或计时。
- **是否保留**：保留scope/harness失败，不判候选正确性或性能。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T00:46:24.060488+00:00",
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
  "status": "prefill_i32_component_scope_assertion_failed",
  "artifacts": "experiments/bundles/20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component",
  "conclusion": "i32组件在实际调用scope断言处停止；当时worker预设BM256/BQ32与selected配置不符，未进入A/B、数值或计时。保留为scope/harness失败，不判候选数值。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component](../../../experiments/bundles/20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
