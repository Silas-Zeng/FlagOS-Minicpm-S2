<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #355 · 纯BF16页内V布局

- **尝试**：完整组件慢1.33%，停止当前实现。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原始结果、编译产物、命令与环境已回收，实际occupancy/事务未测。
- **结果**：纯BF16页内V转置：K保持NHD，V改dim×slot；原GQA只改两处V维度寻址，并实作对应writer，未压缩或增持久容量。位型、8项数值/Graph及writer换值/换slot/负slot门通过，有限输入跨臂逐位一致。完整writer+GQA+reducer Graph ABBA Event 0.544616460800→0.551862716675ms，慢1.330
- **是否保留**：停止当前实现，不进生产。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T024300270939Z",
  "profile_id": "kv-vtranspose",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "kv_vtranspose_component_negative",
  "artifacts": "experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component",
  "conclusion": "纯BF16页内V转置：K保持NHD，V改dim×slot；原GQA只改两处V维度寻址，并实作对应writer，未压缩或增持久容量。位型、8项数值/Graph及writer换值/换slot/负slot门通过，有限输入跨臂逐位一致。完整writer+GQA+reducer Graph ABBA Event 0.544616460800→0.551862716675ms，慢1.330525%；wall慢1.184494%。静态bytepermute减少但寄存器增多，未测实际occupancy/HBM，不作因果归因。性能负，停止当前实现，不扫参、不接prefill/模型；组件正确不等于官方资格。源码/native不变、DB恢复和清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component](../../../experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
