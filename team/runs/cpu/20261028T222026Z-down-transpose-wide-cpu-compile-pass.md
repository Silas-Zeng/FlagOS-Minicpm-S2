<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T222026Z-down-transpose-wide-cpu-compile-pass

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #466 · BI-V150特定形状GEMM

- **尝试**：对固定宽转置tile做CPU-only编译和ASM检查。
- **改动**：BM128/BN64/BK128；仅编译筛查，无设备性能结论。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：CPU-only编译检查，BM128/BN64/BK128。
- **结果**：BM128/BN64/BK128宽转置tile CPU编译和ASM筛查通过；无数值、GPU或性能结论。
- **是否保留**：仅保留编译筛查；不授予数值、组件或生产资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T222026Z-down-transpose-wide-cpu-compile-pass",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T22:20:26+00:00",
  "profile_id": "shape-gemm",
  "phase": "cpu_compile",
  "device": "CPU",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "shape_gemm_transpose_wide_cpu_compile_pass",
  "artifacts": "experiments/bundles/20261028T222026Z-down-transpose-wide-cpu-compile-pass",
  "conclusion": "BM128/BN64/BK128宽转置tile CPU编译和ASM筛查通过；无数值、GPU或性能结论。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T222026Z-down-transpose-wide-cpu-compile-pass](../../../experiments/bundles/20261028T222026Z-down-transpose-wide-cpu-compile-pass)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T222026Z-down-transpose-wide-cpu-compile-pass/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T222026Z-down-transpose-wide-cpu-compile-pass/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
