<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T175144741472Z-biv150-down-groupm4-provided-linear-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #445 · BI-V150特定形状GEMM

- **尝试**：用真实42层权重与两种BF16图案验证down GROUP_M4组件。
- **改动**：自研JIT内核将CTA分组映射GROUP_M8改为GROUP_M4；生产provided-linear callback、tile与数学主体保持受测版本。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：本条所列source/result/manifest原件完整打包并按SHA256分块；组件/CPU筛查与官方成绩分开。
- **结果**：自研JIT CTA分组映射由GROUP_M8改为GROUP_M4；Pattern0/1分别省0.960829%/0.892794%，仅真实42层权重组件局部信号；84有限输出逐元素相等及FP64/Graph/side/RNG门通过，不宣称bitwise、模型或官方收益。
- **是否保留**：保留为待官方接线候选；不外推为模型或官方收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T175144741472Z-biv150-down-groupm4-provided-linear-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T17:51:44.741472+00:00",
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
  "status": "shape_gemm_groupm4_component_positive",
  "artifacts": "experiments/bundles/20261028T175144741472Z-biv150-down-groupm4-provided-linear-component",
  "conclusion": "自研JIT CTA分组映射由GROUP_M8改为GROUP_M4；Pattern0/1分别省0.960829%/0.892794%，仅真实42层权重组件局部信号；84有限输出逐元素相等及FP64/Graph/side/RNG门通过，不宣称bitwise、模型或官方收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T175144741472Z-biv150-down-groupm4-provided-linear-component](../../../experiments/bundles/20261028T175144741472Z-biv150-down-groupm4-provided-linear-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T175144741472Z-biv150-down-groupm4-provided-linear-component/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
