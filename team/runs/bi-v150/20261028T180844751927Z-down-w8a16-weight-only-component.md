<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T180844751927Z-down-w8a16-weight-only-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #451 · BI-V150特定形状GEMM

- **尝试**：比较真实M64 down生产MM-out与W8A16 K128组件的完整Graph。
- **改动**：候选采用权重分组量化与BF16 dot；A/B完整输出和ABBA计时。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：本条所列source/result/manifest原件完整打包并按SHA256分块；组件/CPU筛查与官方成绩分开。
- **结果**：完整Graph组件：A 0.0588357ms，B 0.6471999ms；五项门通过，候选约11倍慢，停止W8A16路线。
- **是否保留**：保留负结果；停止W8A16组件路线，不接模型。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T180844751927Z-down-w8a16-weight-only-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T18:08:44.751927+00:00",
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
  "status": "shape_gemm_w8a16_component_negative",
  "artifacts": "experiments/bundles/20261028T180844751927Z-down-w8a16-weight-only-component",
  "conclusion": "完整Graph组件：A 0.0588357ms，B 0.6471999ms；五项门通过，候选约11倍慢，停止W8A16路线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T180844751927Z-down-w8a16-weight-only-component](../../../experiments/bundles/20261028T180844751927Z-down-w8a16-weight-only-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T180844751927Z-down-w8a16-weight-only-component/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
