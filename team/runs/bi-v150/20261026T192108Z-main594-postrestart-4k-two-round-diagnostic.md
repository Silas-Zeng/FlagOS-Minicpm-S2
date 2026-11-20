<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T192108Z-main594-postrestart-4k-two-round-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #347 · 基线接续与容器环境复查

- **尝试**：本站main56/native14f两档原官方控制：4K暖均5902.77、KV548432；16K暖均4526.57、KV548384，分别1024/512成功，原栈与清理通过。两档独立服务，未继承105或候选收益；旧main241成绩按旧源单列。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/archive-receipt.json)；[result.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/result.json)；[archive-receipt.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/archive-receipt.json)；[result.json](../../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/result.json)；[comparison.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T021016Z-main241-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T021016Z-main241-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T021016Z-main241-native14f-math500/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T052425Z-main56-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T052425Z-main56-control-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T075834Z-main56-control-16k-four-rounds/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：源码、精确命令、原始CSV/日志及清理见本轮原件。
- **结果**：原main594/native14f/初始DB207f重启后4K两轮诊断：冷5612.30对4909.31（+14.32%），首暖5726.40对5843.85（−2.0098%），512请求全部成功。旧三暖5767.56–5931.59，本轮首暖比旧最小低0.714%；源码/DB/native与时钟相同，KV容量548432→548384少48tokens，不能称完全同环境。
- **是否保留**：保留原件；不补大测，不更新正式四轮基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T192108Z-main594-postrestart-4k-two-round-diagnostic",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-26T19:21:08+00:00",
  "profile_id": "baseline-environment",
  "phase": "diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "594ae2a9d17aadc4587ad54ade2b34e17f4af990",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "postrestart_4k_two_rounds",
  "artifacts": "experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic",
  "conclusion": "原main594/native14f/初始DB207f重启后4K两轮诊断：冷5612.30对4909.31（+14.32%），首暖5726.40对5843.85（−2.0098%），512请求全部成功。旧三暖5767.56–5931.59，本轮首暖比旧最小低0.714%；源码/DB/native与时钟相同，KV容量548432→548384少48tokens，不能称完全同环境。观察到小幅暖轮下移，不能由一个首暖证明持续回退或容器启停因果；不替换完整四轮基线、不追加大测。旧M64跨容器负比较不能全归因于方法。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T192108Z-main594-postrestart-4k-two-round-diagnostic](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic)
- 原命令：[benchmark-command.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/benchmark-command.json)；[command.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/manifest.json)；[source-sha256.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic-control/source-sha256.json)
- 原始结果：[raw_runs_diagnostic_20261027_032219.csv](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/benchmark_results/raw_runs_diagnostic_20261027_032219.csv)；[result.json](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/server.log)；[gpu.csv](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/gpu.csv)；[exit-code](../../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
