<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T071618Z-main6971-lpt-early-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #316 · Prefill序列内CTA调序

- **尝试**：检验已测早期chunk调序的整模净影响。
- **改动**：新私有LPT kernel/Manager按几何选择，long原核保留；posthoc核实际私有Q-hoist选中。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-lpt.md)。
- **怎么测**：原官方4K四轮、16K两轮，输入4096/16384、输出1024、并发64，1280 SUCCESS；按负载及冷暖对应比较，KV548432对548336。
- **结果**：LPT早期chunk原官方4K四轮4863.05/5694.95/5694.17/5778.33 tok/s，弃首轮5722.4833，对main6971的5656.77观察+1.1617%；16K冷3757.10、首暖4111.36，对应4119.46观察−0.19663%后停止。六轮1280 SUCCESS，私有LPT Q-hoist实际selected已由posthoc回
- **是否保留**：保留混合结果候选；停止后续测试，无105/合并或新基线，不称整体负或稳定收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T071618Z-main6971-lpt-early-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T07:16:18.571262+00:00",
  "profile_id": "prefill-lpt",
  "phase": "LPT早期chunk原官方六轮筛选",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_lpt_official_mixed_partial_stop",
  "artifacts": "experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds",
  "conclusion": "LPT早期chunk原官方4K四轮4863.05/5694.95/5694.17/5778.33 tok/s，弃首轮5722.4833，对main6971的5656.77观察+1.1617%；16K冷3757.10、首暖4111.36，对应4119.46观察−0.19663%后停止。六轮1280 SUCCESS，私有LPT Q-hoist实际selected已由posthoc回执核实。KV548432对参考548336，非严格因果；保留混合结果候选，不称稳定整体收益或整体负。16K未满四轮、105未跑，不合并/升基线。07:57 DB/source/native及清理通过，原SIGTERM/exit1保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T071618Z-main6971-lpt-early-four-rounds](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_151843.csv](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/benchmark_results/raw_runs_20261026_151843.csv)；[summary_20261026_151843.csv](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/benchmark_results/summary_20261026_151843.csv)；[result.json](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/exit-code)
- 相关说明：[2026-10-26-local-to-e2e-review](../../../analysis/2026-10-26-local-to-e2e-review.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
