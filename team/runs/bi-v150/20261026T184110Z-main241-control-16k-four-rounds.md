<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T184110Z-main241-control-16k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #348 · 基线接续与容器环境复查

- **尝试**：同版本main594 4K首暖观察下降2.01%，只作两轮诊断；新main241独立16K四轮暖均4487.49。两种源码和实验目的分别保留，不混算。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/archive-receipt.json)；[result.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/result.json)；[archive-receipt.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/archive-receipt.json)；[result.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/result.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：源码、精确命令、原始CSV/日志及清理见本轮原件。
- **结果**：新团队main241/native14f/初始DB207f原官方16K四轮3791.43/4489.43/4487.31/4485.73 tok/s，弃首暖均4487.49，512请求全部成功；对旧main594暖均4192.49观察+7.0364%；KV容量548288→548432多144tokens，非严格等KV单项因果。实际Q32与原优化栈通过，source/nativ
- **是否保留**：保留新main同口径16K控制；4K和105资格独立。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T184110Z-main241-control-16k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-26T18:41:10+00:00",
  "profile_id": "baseline-environment",
  "phase": "official_control",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "false",
  "status": "main241_control_16k_complete",
  "artifacts": "experiments/official/20261026T184110Z-main241-control-16k-four-rounds",
  "conclusion": "新团队main241/native14f/初始DB207f原官方16K四轮3791.43/4489.43/4487.31/4485.73 tok/s，弃首暖均4487.49，512请求全部成功；对旧main594暖均4192.49观察+7.0364%；KV容量548288→548432多144tokens，非严格等KV单项因果。实际Q32与原优化栈通过，source/native/DB恢复及清理成功。本次仅16K正式四轮，未取得本站新main4K或105资格；不冒用队友native5cbb成绩。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T184110Z-main241-control-16k-four-rounds](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261027_024320.csv](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/benchmark_results/raw_runs_20261027_024320.csv)；[summary_20261027_024320.csv](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/benchmark_results/summary_20261027_024320.csv)；[result.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
