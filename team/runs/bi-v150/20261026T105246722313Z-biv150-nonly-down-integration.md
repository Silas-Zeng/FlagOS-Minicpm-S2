<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T105246722313Z-biv150-nonly-down-integration

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #328 · BF16 down N方向分组布局

- **尝试**：N128单层M64省10.55%、M32省3.63%；精确身份修复后的M64-only官方4K暖均5719.8133（观察+1.1145%），16K首暖4005.55（观察−2.7652%）后停。六轮1280 SUCCESS、旧prefill栈/新FX42闭合；KV516320、1008MiB常驻副本，保留混合结果，不合并/定基线/跑105。旧v1身份失配与大M两种负布局分别保留。
- **改动**：相关实现 [result.json](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/result.json)；[worker.py](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/archive-receipt.json)；[candidate.py](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/result.json)；[worker.py](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/result.json)；[worker.py](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/result.json)；[worker.py](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/result.json)；[2048-original_linear.ttgir](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/2048-original_linear.ttgir)；[2048-n256_linear.ttgir](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/2048-n256_linear.ttgir)；[archive-receipt.json](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/archive-receipt.json)；[raw_runs_20261026_192922.csv](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/benchmark_results/raw_runs_20261026_192922.csv)；[performance-stop-decision.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/performance-stop-decision.json)；[posthoc-after-stop.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/posthoc-after-stop.json)；[prefill-activation.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/prefill-activation.json)；[archive-receipt.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/archive-receipt.json)；[raw_runs_20261026_200712.csv](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/benchmark_results/raw_runs_20261026_200712.csv)；[performance-stop-decision.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/performance-stop-decision.json)；[posthoc-after-stop.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/posthoc-after-stop.json)；[prefill-activation.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/prefill-activation.json)；[archive-receipt.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/archive-receipt.json)；[2026-10-26-local-to-e2e-budget.md](../../../analysis/2026-10-26-local-to-e2e-budget.md)；本轮准确变体以原件源码清单为准。
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
