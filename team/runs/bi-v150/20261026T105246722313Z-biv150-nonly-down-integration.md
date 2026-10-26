<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T105246722313Z-biv150-nonly-down-integration

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #328 · BF16 down N方向分组布局

- **尝试**：同一N128 BF16无损格式：M64单层省10.5534%，新M32单层省约3.63%；M2048为适应格式BN256→128后慢约61.60%，停止该大M候选。42真实权重GPU helper/opaque/Graph接线门通过，但不是完整模型安装链或官方成绩。原W/P双份1008MiB及KV容量代价未消除；不叠加各M收益。
- **改动**：相关实现 [result.json](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/result.json)；[worker.py](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/archive-receipt.json)；[candidate.py](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/result.json)；[worker.py](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/result.json)；[worker.py](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/result.json)；[worker.py](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：实际42层BF16 down权重独立调用GPU _after_loading helper及新opaque，保留原W与层buffer；不计时、不运行完整Llama安装链。
- **结果**：42真实权重helper/opaque、pack逐位、FP64、换值Graph及M32回退通过；不是完整Llama加载链，无计时或官方资格。
- **是否保留**：保留新增helper/opaque/Graph接线证据；完整模型加载链和官方净性能不继承，原W/P双份容量成本未消除。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T105246722313Z-biv150-nonly-down-integration",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T10:52:46.722313+00:00",
  "profile_id": "bf16-nonly-down-integration",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "nonly_down_integration_component_pass",
  "artifacts": "experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration",
  "conclusion": "42层真实down权重的GPU _after_loading helper/新opaque接线门通过：pack全位反解、原W保留、1056964608B nonpersistent buffer、42层完整输出逐位及独立FP64样本、两种同址换X Graph和M32原路回退通过。未调用完整Llama install-chain，无吞吐计时、官方或105资格；1008MiB常驻副本及KV容量代价仍需模型验证。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T105246722313Z-biv150-nonly-down-integration](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/worker.log)；[gpu.csv](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/gpu.csv)；[exit-code](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
