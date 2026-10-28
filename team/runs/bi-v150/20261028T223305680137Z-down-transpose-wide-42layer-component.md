<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T223305680137Z-down-transpose-wide-42layer-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #468 · BI-V150特定形状GEMM

- **尝试**：检验宽转置tile对M64 down完整42层组件耗时的影响。
- **改动**：固定BM128/BN64/BK128、w32/s2、CTA1；真实权重与生产数学不变，两组输入做完整ABBA。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：M64 down固定宽转置tile、42层真实权重；两组输入、ABBA完整，实际metadata.use_sme为7/7，恢复清理通过。
- **结果**：42层真实权重、两组输入、ABBA完整；数值/Graph/side通过，B Event均值3.184987ms对A 2.324920ms慢36.9934%，停止此实现；非官方/105/合并/新基线。
- **是否保留**：停止该实现；不进官方/105，不合并或更新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T223305680137Z-down-transpose-wide-42layer-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T22:33:05.680137+00:00",
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
  "status": "shape_gemm_transpose_wide_component_negative",
  "artifacts": "experiments/bundles/20261028T223305680137Z-down-transpose-wide-42layer-component",
  "conclusion": "42层真实权重、两组输入、ABBA完整；数值/Graph/side通过，B Event均值3.184987ms对A 2.324920ms慢36.9934%，停止此实现；非官方/105/合并/新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T223305680137Z-down-transpose-wide-42layer-component](../../../experiments/bundles/20261028T223305680137Z-down-transpose-wide-42layer-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T223305680137Z-down-transpose-wide-42layer-component/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T223305680137Z-down-transpose-wide-42layer-component/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
