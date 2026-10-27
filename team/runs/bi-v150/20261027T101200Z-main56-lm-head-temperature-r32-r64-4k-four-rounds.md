<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #369 · LM-head温度epilogue融合

- **尝试**：新8d1a同源原官方4K/16K各四轮，暖均5971.44/4529.79 tok/s，对各自A观察+1.1634%/+0.0710%；两档KV不同，非严格因果或稳定收益，不定新基线。原105为103/105 valid/pass，但head32/64和Q32未覆盖，分支准确率未证。旧31094098与局部组件结果另列，不相加。

同融合基线上的R32 BN256扩展已完成：十门过，但完整ABBA Event慢2.6150%、wall快5.7801%，按nonpositive停止，不影响原BN64融合生产结果。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原四轮弃首；809源8d1a，KV548288对A548432；365原件逐SHA。
- **结果**：新8d1a官方4K暖均5971.44对A5902.77，观察+1.1634%；1024成功，R32/R64实际消费。KV不同。
- **是否保留**：保留单组正观察；非严格因果或稳定收益，不定新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T10:12:00+00:00",
  "profile_id": "lm-head-temperature",
  "phase": "official_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "lm_head_temperature_r32_r64_4k_complete_kv_mismatch",
  "artifacts": "experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds",
  "conclusion": "新8d1a R32+R64 head温度epilogue809源，原官方4K四轮[5721.52, 5751.06, 6060.06, 6103.2] tok/s，弃首暖均5971.440000对A 5902.770000，单组观察+1.163352%；1024请求SUCCESS，实际R32/R64 SELECTED/SAMPLED、原stack/provider、source/native不变、DB恢复及清理通过。main56/native14f与共同初始DB，KV548288对A548432，不报严格因果或稳定收益、不定新基线；首次回执不证明命中占比。同8d1a完整16K观察+0.070988%（KV不同），同源105为103/105 valid/pass，但head32/64与Q32未覆盖，不授这些分支准确率资格。365原件逐SHA回收，旧31094098分开。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261027_181310.csv](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/benchmark_results/raw_runs_20261027_181310.csv)；[summary_20261027_181310.csv](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/benchmark_results/summary_20261027_181310.csv)；[result.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
