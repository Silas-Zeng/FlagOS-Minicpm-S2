<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T053835Z-main6971-down-small-split8-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #303 · BI-V150特定形状GEMM

- **尝试**：检验真实模型中的完整净收益。
- **改动**：独立候选精确形状接入；组件收益不继承为模型收益。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原官方脚本/参数不变；已测暖轮与原基线同负载/轮次比较，KV差异明示。
- **结果**：M1–8 down SplitK8真实42层组件省32–35%，生产路由/Graph已过；原官方4K冷4889.20、首暖5513.95 tok/s，对main6971/PR60对应5533.03观察−0.34484%。512 SUCCESS后按用户低于基线就停，05:50:26 UTC清理完成；16K/105不跑，不是完整官方或正确性失败。DB207f恢复、source/na
- **是否保留**：已低于可比基线，停止后续；不跑105、不提收益PR、不定新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T053835Z-main6971-down-small-split8-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T05:38:35+00:00",
  "profile_id": "shape-gemm",
  "phase": "BI-V150 down小M SplitK8原官方首暖筛选",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "shape_gemm_model_negative_early_stop",
  "artifacts": "experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds",
  "conclusion": "M1–8 down SplitK8真实42层组件省32–35%，生产路由/Graph已过；原官方4K冷4889.20、首暖5513.95 tok/s，对main6971/PR60对应5533.03观察−0.34484%。512 SUCCESS后按用户低于基线就停，05:50:26 UTC清理完成；16K/105不跑，不是完整官方或正确性失败。DB207f恢复、source/native不变；不定新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T053835Z-main6971-down-small-split8-four-rounds](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_134055.csv](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds/benchmark_results/raw_runs_20261026_134055.csv)；[result.json](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261026T053835Z-main6971-down-small-split8-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
