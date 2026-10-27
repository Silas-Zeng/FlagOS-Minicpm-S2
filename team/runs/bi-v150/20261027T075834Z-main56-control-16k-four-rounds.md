<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T075834Z-main56-control-16k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #363 · 基线接续与容器环境复查

- **尝试**：本站main56/native14f两档原官方控制：4K暖均5902.77、KV548432；16K暖均4526.57、KV548384，分别1024/512成功，原栈与清理通过。两档独立服务，未继承105或候选收益；旧main241成绩按旧源单列。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/archive-receipt.json)；[result.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/result.json)；[archive-receipt.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/archive-receipt.json)；[result.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/result.json)；[comparison.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T021016Z-main241-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T021016Z-main241-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T021016Z-main241-native14f-math500/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T052425Z-main56-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T052425Z-main56-control-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方四轮弃首；同版本候选须引用本run。
- **结果**：main56/native14f原官方16K暖均4526.57 tok/s，512成功、KV548384、原栈/清理通过。
- **是否保留**：保留本次16K控制；4K与105资格分开。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T075834Z-main56-control-16k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T07:58:34+00:00",
  "profile_id": "baseline-environment",
  "phase": "official_control",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "false",
  "status": "main56_control_16k_complete",
  "artifacts": "experiments/official/20261027T075834Z-main56-control-16k-four-rounds",
  "conclusion": "main56/native14f原官方16K四轮[4108.26, 4528.51, 4526.31, 4524.9] tok/s，弃首暖均4526.573333，512请求全SUCCESS；源码807/native不变、DB恢复、原Graph/native/prefill/provider及清理通过。实际KV548384。保留为本次同版本16K候选控制，4K控制单列，不继承105准确率或任何候选收益。311份原件逐SHA回收。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T075834Z-main56-control-16k-four-rounds](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261027_155948.csv](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/benchmark_results/raw_runs_20261027_155948.csv)；[summary_20261027_155948.csv](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/benchmark_results/summary_20261027_155948.csv)；[result.json](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
