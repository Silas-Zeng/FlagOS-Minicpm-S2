<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T185611249396Z-down-bm32bn32-tile-handles-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #454 · BI-V150特定形状GEMM

- **尝试**：检验M64 down采用BM32/BN32/BK128是否减少完整组件时间。
- **改动**：只改tile分块，原数学与生产callback保留；完整Graph计入结果。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：本条所列source/result/manifest原件完整打包并按SHA256分块；组件/CPU筛查与官方成绩分开。
- **结果**：五项数值门通过；A 0.0598722361ms、B 0.0920051672ms，B慢53.669168%；compile/RNG/清理门通过，停止不扫矩阵。
- **是否保留**：停止该固定点，不接官方或扩扫矩阵。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T185611249396Z-down-bm32bn32-tile-handles-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T18:56:11.249396+00:00",
  "profile_id": "shape-gemm",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "shape_gemm_bm32bn32_component_negative",
  "artifacts": "experiments/bundles/20261028T185611249396Z-down-bm32bn32-tile-handles-component",
  "conclusion": "五项数值门通过；A 0.0598722361ms、B 0.0920051672ms，B慢53.669168%；compile/RNG/清理门通过，停止不扫矩阵。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T185611249396Z-down-bm32bn32-tile-handles-component](../../../experiments/bundles/20261028T185611249396Z-down-bm32bn32-tile-handles-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T185611249396Z-down-bm32bn32-tile-handles-component/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
