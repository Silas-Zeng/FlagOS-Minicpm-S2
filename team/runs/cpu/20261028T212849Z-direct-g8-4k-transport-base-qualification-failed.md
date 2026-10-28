<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T212849Z-direct-g8-4k-transport-base-qualification-failed

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #462 · BI-V150特定形状GEMM

- **尝试**：验证Direct-G8官方4K候选冻结source运输身份。
- **改动**：CPU暂存完成815文件后，qualification错误地把341运输基底与f165性能基线比较；GPU未启动。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原始成员、清单与压缩分块按SHA256核验；入口资格失败与完整官方负结果分开。
- **结果**：CPU准备中qualification混淆341运输基底与f165性能基线；source stage已构造815/tree3d，GPU未启动。保留准备错误原件，无性能/数值结论。
- **是否保留**：保留准备失败原件；运输基底与测量基线分开记录。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T212849Z-direct-g8-4k-transport-base-qualification-failed",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T21:28:49+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_4k_entry_preparation_failed",
  "device": "CPU",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "",
  "status": "shape_gemm_direct_g8_transport_base_qualification_failed",
  "artifacts": "experiments/bundles/20261028T212849Z-direct-g8-4k-transport-base-qualification-failed",
  "conclusion": "CPU准备中qualification混淆341运输基底与f165性能基线；source stage已构造815/tree3d，GPU未启动。保留准备错误原件，无性能/数值结论。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T212849Z-direct-g8-4k-transport-base-qualification-failed](../../../experiments/bundles/20261028T212849Z-direct-g8-4k-transport-base-qualification-failed)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T212849Z-direct-g8-4k-transport-base-qualification-failed/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T212849Z-direct-g8-4k-transport-base-qualification-failed/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
