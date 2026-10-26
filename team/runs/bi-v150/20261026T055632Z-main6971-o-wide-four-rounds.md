<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T055632Z-main6971-o-wide-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #308 · BI-V150特定形状GEMM

- **尝试**：检验O宽tile局部收益是否转为官方吞吐。
- **改动**：只接入O宽tile，保留其它主线优化。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原官方4K已测三轮、每轮256请求；按对应冷/暖轮比较，16K/105未跑。
- **结果**：O宽tile真实42层组件曾省20.33%；原官方4K冷/首暖/第三轮4894.19/5538.59/5568.49 tok/s，768 SUCCESS，第三轮低于对应5677.28，观察−1.9162%后主动停止。原result exit1/SIGTERM保持；06:12:52 UTC DB恢复、source/native不变及端口/设备清理通过。16K/105未跑，不是完整
- **是否保留**：停止，不合并、不定新基线；保留全部三轮及SIGTERM原件。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T055632Z-main6971-o-wide-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T05:56:32.681606+00:00",
  "profile_id": "shape-gemm",
  "phase": "BI-V150 O宽tile原官方4K早停",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "o_wide_model_negative_early_stop",
  "artifacts": "experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds",
  "conclusion": "O宽tile真实42层组件曾省20.33%；原官方4K冷/首暖/第三轮4894.19/5538.59/5568.49 tok/s，768 SUCCESS，第三轮低于对应5677.28，观察−1.9162%后主动停止。原result exit1/SIGTERM保持；06:12:52 UTC DB恢复、source/native不变及端口/设备清理通过。16K/105未跑，不是完整官方成绩或正确性失败；本轮未确认模型净收益、不合并、不定新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T055632Z-main6971-o-wide-four-rounds](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_135854.csv](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds/benchmark_results/raw_runs_20261026_135854.csv)；[result.json](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261026T055632Z-main6971-o-wide-four-rounds/exit-code)
- 相关说明：[2026-10-26-local-to-e2e-review](../../../analysis/2026-10-26-local-to-e2e-review.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
