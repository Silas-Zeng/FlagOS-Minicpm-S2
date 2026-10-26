<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T092809453391Z-biv150-packed-down-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #322 · BF16 down权重微块布局

- **尝试**：真实F.linear同配置的BF16位重排；首次停在SME假设，v2保留全部正确性后通过8项，但M2030完整Graph慢71.89%，停止。
- **改动**：相关实现 [source](../../../experiments/framework/20261026T090924033923Z-biv150-packed-down-component/source)；[source](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/source)；[result.json](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/result.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实layer0权重、合成M2030激活；原F.linear同配置/完整Graph16call ABBA，无profiler。不含eager CPU分配或加载pack，不是官方成绩。
- **结果**：v2仅将SME机制要求改诊断，candidate字节不变；8项数值/FP64/Graph/side检查通过。M2030完整GEMM Graph ABBA原F.linear0.564831406→packed0.970907092ms，慢71.89%，停止M2048/权重环/模型。DB/source/清理成功。
- **是否保留**：停止该布局，不合并、不定基线；局部负结果保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T092809453391Z-biv150-packed-down-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T09:28:09.453391+00:00",
  "profile_id": "bf16-packed-down",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "packed_layout_negative_component",
  "artifacts": "experiments/framework/20261026T092809453391Z-biv150-packed-down-component",
  "conclusion": "v2仅将SME机制要求改诊断，candidate字节不变；8项数值/FP64/Graph/side检查通过。M2030完整GEMM Graph ABBA原F.linear0.564831406→packed0.970907092ms，慢71.89%，停止M2048/权重环/模型。DB/source/清理成功。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T092809453391Z-biv150-packed-down-component](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
