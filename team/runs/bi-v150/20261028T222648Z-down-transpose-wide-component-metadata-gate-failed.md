<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T222648Z-down-transpose-wide-component-metadata-gate-failed

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #467 · BI-V150特定形状GEMM

- **尝试**：准备42层M64 down宽转置组件测量。
- **改动**：worker错误要求metadata.use_sme=15，而原A/B均为7；不是kernel配置变更，未开始数值/计时。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：组件准备失败；原A/B的metadata.use_sme均为7，worker误要求15。
- **结果**：组件计时前metadata断言失败：原A/B实际metadata.use_sme均为7，worker错误要求值为15；没有数值或计时结果。
- **是否保留**：保留worker metadata期望值门错误；无数值或计时结论。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T222648Z-down-transpose-wide-component-metadata-gate-failed",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T22:26:48.495445+00:00",
  "profile_id": "shape-gemm",
  "phase": "component_prepare",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "shape_gemm_transpose_wide_metadata_gate_failed",
  "artifacts": "experiments/bundles/20261028T222648Z-down-transpose-wide-component-metadata-gate-failed",
  "conclusion": "组件计时前metadata断言失败：原A/B实际metadata.use_sme均为7，worker错误要求值为15；没有数值或计时结果。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T222648Z-down-transpose-wide-component-metadata-gate-failed](../../../experiments/bundles/20261028T222648Z-down-transpose-wide-component-metadata-gate-failed)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T222648Z-down-transpose-wide-component-metadata-gate-failed/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T222648Z-down-transpose-wide-component-metadata-gate-failed/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
