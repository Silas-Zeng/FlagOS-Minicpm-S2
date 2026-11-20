<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T044032Z-main6971-qkv-wide-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #300 · BI-V150特定形状GEMM

- **尝试**：检验真实模型中的完整净收益。
- **改动**：独立候选精确形状接入；组件收益不继承为模型收益。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原官方脚本/参数不变；已测暖轮与原基线同负载/轮次比较，KV差异明示。
- **结果**：QKV 42层组件省4.18%，但模型4K四轮4881.10/5496.38/5332.94/5705.54，弃首轮暖均5511.62，对main6971已测5656.77观察−2.56595%；16K冷3751.32、首暖4104.55，对对应基线4119.46观察−0.36194%。六轮1280 SUCCESS；用户要求低于基线就不跑，05:25 UTC停止剩余16K并完成
- **是否保留**：已低于可比基线，停止后续；不跑105、不提收益PR、不定新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T044032Z-main6971-qkv-wide-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T04:40:32+00:00",
  "profile_id": "shape-gemm",
  "phase": "BI-V150 QKV宽tile模型负结果早停",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "shape_gemm_model_negative_early_stop",
  "artifacts": "experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds",
  "conclusion": "QKV 42层组件省4.18%，但模型4K四轮4881.10/5496.38/5332.94/5705.54，弃首轮暖均5511.62，对main6971已测5656.77观察−2.56595%；16K冷3751.32、首暖4104.55，对对应基线4119.46观察−0.36194%。六轮1280 SUCCESS；用户要求低于基线就不跑，05:25 UTC停止剩余16K并完成清理。DB207f恢复、source/native不变、GPU/9031释放；KV548432对548336，不称严格因果、完整官方或正确性失败。不跑105、不提收益PR、不定新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T044032Z-main6971-qkv-wide-four-rounds](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_124251.csv](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds/benchmark_results/raw_runs_20261026_124251.csv)；[summary_20261026_124251.csv](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds/benchmark_results/summary_20261026_124251.csv)；[result.json](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261026T044032Z-main6971-qkv-wide-four-rounds/exit-code)
- 相关说明：[2026-10-26-local-to-e2e-review](../../../analysis/2026-10-26-local-to-e2e-review.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
