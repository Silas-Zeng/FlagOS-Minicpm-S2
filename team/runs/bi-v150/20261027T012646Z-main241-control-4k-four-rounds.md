<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T012646Z-main241-control-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #350 · 基线接续与容器环境复查

- **尝试**：同版本main594 4K首暖观察下降2.01%，只作两轮诊断；新main241独立16K四轮暖均4487.49。两种源码和实验目的分别保留，不混算。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/archive-receipt.json)；[result.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/result.json)；[archive-receipt.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/archive-receipt.json)；[result.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/result.json)；[comparison.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方四轮弃首，精确命令、CSV、源码/环境及收尾见原件。
- **结果**：main241/native14f/初始DB207f原官方4K四轮[5632.05, 5833.56, 6000.87, 5715.73] tok/s，弃首暖均5850.053333；1024请求全SUCCESS，实际Q32/原栈、源码/native不变、DB恢复及清理通过。旧main594暖均5847.666667，观察变化+0.0408%，基本持平，不宣称稳定提升；KV 5
- **是否保留**：保留本站main241完整4K控制，未取得105模型准确率资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T012646Z-main241-control-4k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T01:26:46+00:00",
  "profile_id": "baseline-environment",
  "phase": "official_control",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "main241_control_4k_complete",
  "artifacts": "experiments/official/20261027T012646Z-main241-control-4k-four-rounds",
  "conclusion": "main241/native14f/初始DB207f原官方4K四轮[5632.05, 5833.56, 6000.87, 5715.73] tok/s，弃首暖均5850.053333；1024请求全SUCCESS，实际Q32/原栈、源码/native不变、DB恢复及清理通过。旧main594暖均5847.666667，观察变化+0.0408%，基本持平，不宣称稳定提升；KV 548432→548288。本站main241两档吞吐控制现已补齐，完整105准确率仍未取得；不能将请求成功等同准确率通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T012646Z-main241-control-4k-four-rounds](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261027_092756.csv](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/benchmark_results/raw_runs_20261027_092756.csv)；[summary_20261027_092756.csv](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/benchmark_results/summary_20261027_092756.csv)；[result.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
