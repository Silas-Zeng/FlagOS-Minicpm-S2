<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #478 · Prefill i32 offset 组件筛查

- **尝试**：以实际scope准备两臂并执行既定组件门。
- **改动**：结果记录器异常；无数值/计时结果，保留原错误与恢复证据。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-i32-offset.md)。
- **怎么测**：BI-V150私有组件准备；A/B数值和计时未产生，环境恢复通过。
- **结果**：组件完成A/B编译与Q-fragment proof后，结果记录代码访问未定义属性并退出；未形成数值/计时。
- **是否保留**：保留记录器异常，不判候选数值或性能。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T01:02:43.657857+00:00",
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
  "status": "prefill_i32_component_result_recording_failed",
  "artifacts": "experiments/bundles/20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component",
  "conclusion": "i32组件A/B编译与Q-fragment proof后，在结果记录代码访问缺失属性而退出，未形成数值或计时。保留为记录器失败，不判候选正确性或性能。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component](../../../experiments/bundles/20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
