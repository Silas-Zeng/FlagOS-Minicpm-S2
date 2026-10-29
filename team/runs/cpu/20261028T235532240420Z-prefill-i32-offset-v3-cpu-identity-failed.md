<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #473 · Prefill i32 offset 组件筛查

- **尝试**：修正attrs解码后重试同一CPU编译身份门。
- **改动**：A normal identity未重现171100 selected hash，B未编译；旧guard与目标BM256/BQ32/page16不符。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-i32-offset.md)。
- **怎么测**：仅CPU、CUDA API未调用；运行在B编译前退出。目标BM256/BQ32/page16，旧guard为BM128/BQ16/page32。
- **结果**：i32-offset v3 CPU-only在A normal kernel身份门停止：未复现171100 selected normal hash，B候选未编译。静态guard仍是BM128/BQ16/page32，不适用于实际目标BM256/BQ32/page16。
- **是否保留**：保留A身份门失败；不放宽normal identity，也不据此判断候选数学或性能。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T23:55:32.240420+00:00",
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
  "status": "prefill_i32_v3_normal_identity_mismatch",
  "artifacts": "experiments/bundles/20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed",
  "conclusion": "i32-offset v3 CPU-only在A normal身份门停止，B未编译；静态guard的BM128/BQ16/page32范围与实际目标BM256/BQ32/page16不符。无CUDA调用或性能结论。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed](../../../experiments/bundles/20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
