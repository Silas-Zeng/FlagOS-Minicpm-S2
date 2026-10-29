<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T230703857834Z-native-gqa-grid-order-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #469 · BI-V150特定形状GEMM

- **尝试**：比较native GQA原CTA顺序与单一grid-order置换的N64/S2组件耗时。
- **改动**：真实production macro1与同run候选32-call ABBA；九类正确性/Graph/side/RNG门通过，event慢0.2253%，wall慢0.0941%，停止。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：BI-V150、同run production macro1对单一CTA/grid置换，32-call ABBA；非模型或官方性能测量。
- **结果**：32-call ABBA：event 0.409491345→0.410414010 ms，候选慢0.2253%；wall 0.412703422→0.413091609 ms，慢0.0941%。9类数值/Graph/side/输入RNG门通过，按负结果停止；非模型准确率或官方成绩。
- **是否保留**：保留小幅负结果并停止该grid-order候选；不外推模型/官方成绩。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T230703857834Z-native-gqa-grid-order-hotspot-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T23:07:03.857834+00:00",
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
  "status": "shape_gemm_native_gqa_grid_order_negative",
  "artifacts": "experiments/bundles/20261028T230703857834Z-native-gqa-grid-order-hotspot-component",
  "conclusion": "32-call ABBA：event 0.409491345→0.410414010 ms，候选慢0.2253%；wall 0.412703422→0.413091609 ms，慢0.0941%。9类数值/Graph/side/输入RNG门通过，按负结果停止；非模型准确率或官方成绩。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T230703857834Z-native-gqa-grid-order-hotspot-component](../../../experiments/bundles/20261028T230703857834Z-native-gqa-grid-order-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T230703857834Z-native-gqa-grid-order-hotspot-component/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T230703857834Z-native-gqa-grid-order-hotspot-component/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
