<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T095708239358Z-gqa-for-span-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #324 · GQA动态for与二维span

- **尝试**：根据main6971真实Graph热点，保持原page16/数学顺序/reducer，仅改变循环形式与合法跨度；N64/S2八类门通过，但完整组件慢75.05%，停止。
- **改动**：相关实现 [kernel.diff](../../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/source/kernel.diff)；[results.json](../../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/results.json)；[ir-candidate](../../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/ir-candidate)；本轮准确变体以原件源码清单为准。
- **怎么测**：实际N64/B64/S2及replay32长度多重集，合成Q/KV；page16、原FP64/特殊值/换值Graph/side门，完整producer＋原reducer16-call ABBA。
- **结果**：原page16/FP顺序的动态for＋二维span，N64/S2用真实4K观测长度多重集、合成激活。8类原数值/FP64/Graph/写入门通过，完整producer＋原reducer Event0.541187257→0.947350353ms，慢75.0504%，wall慢74.0019%。停止，不进模型。source/DB/native及9031清理通过；mask14→6
- **是否保留**：停止本候选，不扩形状或模型，不合并；复用原负结果，不重跑。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T095708239358Z-gqa-for-span-hotspot-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T09:57:08.239358+00:00",
  "profile_id": "gqa-for-span",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_for_span_negative_component",
  "artifacts": "experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component",
  "conclusion": "原page16/FP顺序的动态for＋二维span，N64/S2用真实4K观测长度多重集、合成激活。8类原数值/FP64/Graph/写入门通过，完整producer＋原reducer Event0.541187257→0.947350353ms，慢75.0504%，wall慢74.0019%。停止，不进模型。source/DB/native及9031清理通过；mask14→62不是SME启用证明。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T095708239358Z-gqa-for-span-hotspot-component](../../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
