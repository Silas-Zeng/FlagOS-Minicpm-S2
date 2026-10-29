<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #476 · Prefill i32 offset 组件筛查

- **尝试**：尝试启动i32单层attention组件。
- **改动**：EngineArgs因未提供native GQA依赖而退出；没有A/B数值或性能结果。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-i32-offset.md)。
- **怎么测**：BI-V150私有组件入口；source tree f1658b69，原native与DB恢复。
- **结果**：入口没有传固定GQA依赖，EngineArgs初始化时报缺少native GQA库；未进入A/B、数值或计时。
- **是否保留**：保留依赖接线失败，不称候选数值/性能失败。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T00:32:47.313980+00:00",
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
  "status": "prefill_i32_component_gqa_dependency_missing",
  "artifacts": "experiments/bundles/20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component",
  "conclusion": "i32组件因入口未传固定GQA依赖而在EngineArgs初始化阶段退出；未进入A/B、数值或计时。保留为依赖接线失败，不是候选正确性或性能结果。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component](../../../experiments/bundles/20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
