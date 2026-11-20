<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T200454Z-down-gemm-direct-launch-official16k-driver-pin-preparation-failed

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #457 · BI-V150特定形状GEMM

- **尝试**：准备同候选的原官方16K入口并验证driver身份门。
- **改动**：运行owner准备入口；case_driver SHA未与owner pin一致，值未改也未实际开始benchmark。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原始文件按清单SHA核验并完整打包；性能组件、官方成绩与入口准备失败分开。
- **结果**：BI-V150入口的CPU准备阶段：保留driver pin失败原件，未启动GPU或benchmark；不生成16K性能结论。
- **是否保留**：保留入口准备失败原件；与后续冻结修正版本及16K实测分开记录。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T200454Z-down-gemm-direct-launch-official16k-driver-pin-preparation-failed",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T20:04:54+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_16k_preparation",
  "device": "CPU",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "",
  "status": "shape_gemm_direct_launch_official16k_driver_pin_preparation_failed",
  "artifacts": "experiments/bundles/20261028T200454Z-down-gemm-direct-launch-official16k-driver-pin-preparation-failed",
  "conclusion": "BI-V150入口的CPU准备阶段：保留driver pin失败原件，未启动GPU或benchmark；不生成16K性能结论。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T200454Z-down-gemm-direct-launch-official16k-driver-pin-preparation-failed](../../../experiments/bundles/20261028T200454Z-down-gemm-direct-launch-official16k-driver-pin-preparation-failed)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T200454Z-down-gemm-direct-launch-official16k-driver-pin-preparation-failed/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T200454Z-down-gemm-direct-launch-official16k-driver-pin-preparation-failed/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
