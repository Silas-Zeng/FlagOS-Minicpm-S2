<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #475 · Prefill i32 offset 组件筛查

- **尝试**：在不放宽生产身份门的前提下诊断i32 offset/Q-fragment编译机制。
- **改动**：两臂编译与CPU proof通过，但A selected identity仍不匹配；不授GPU/生产资格。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-i32-offset.md)。
- **怎么测**：normal identity未匹配；仅CPU编译/静态proof，无运行或吞吐数据。
- **结果**：i32-offset v6仅作CPU机制诊断：两臂normal/Q-fragment编译及proof通过，但A生产selected hash仍不匹配。资源观察A SGPR104/VGPR113/spill4，B SGPR85/VGPR112/spill0，shared 65536B。
- **是否保留**：机制proof不是数值或性能结果；明确不授生产、GPU或官方资格，保留证据并停止。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T00:12:04.223339+00:00",
  "profile_id": "prefill-i32-offset",
  "phase": "cpu_compile",
  "device": "CPU",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "prefill_i32_v6_cpu_mechanism_diagnostic",
  "artifacts": "experiments/bundles/20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic",
  "conclusion": "i32-offset v6 CPU机制诊断完成：两臂normal与Q-fragment编译及proof通过；A生产selected hash仍不匹配，故明确不授生产/GPU/官方资格。资源记录见原件；无数值或吞吐结果。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic](../../../experiments/bundles/20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
