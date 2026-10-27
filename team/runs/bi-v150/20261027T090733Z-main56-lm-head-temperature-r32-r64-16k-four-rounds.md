<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #367 · LM-head温度epilogue融合

- **尝试**：原main56+受测8d1a五文件已通过中文PR84合并，main dac1b8fb。4K同KV时间相近对照暖均5923.116667→5971.44 tok/s，单组观察+0.8158%；事后首暖−1.3314%、两A漂移+0.3447%，不称稳定幅度或新官方基线。16K暖均4529.79对4526.57（观察+0.0710%），KV不同；同源105为103/105 valid/pass，但head32/64及Q32未覆盖，组件数学资格另列。BN256扩展Event负，停止且不含在PR84。旧R64-only结果不与新组合相加。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方四轮弃首；809源8d1a，KV548432对A548384。
- **结果**：新8d1a R32+R64原官方16K暖均4529.79对A4526.57 tok/s，观察+0.0710%；512成功、R32实际消费/清理通过。KV不同。
- **是否保留**：保留完整16K微小正观察；KV不匹配，非严格因果或稳定收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T09:07:33+00:00",
  "profile_id": "lm-head-temperature",
  "phase": "official_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "false",
  "status": "lm_head_temperature_r32_r64_16k_complete_kv_mismatch",
  "artifacts": "experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds",
  "conclusion": "新8d1a R32+R64 head温度epilogue809源，原官方16K四轮[3812.37, 4532.39, 4529.58, 4527.39] tok/s，弃首暖均4529.786667对A 4526.573333，单组观察+0.070988%；512请求SUCCESS，实际R32 SELECTED/SAMPLED、原stack/provider、source/native不变、DB恢复及清理通过。main56/native14f与共同初始DB，KV548432对A548384，不报严格因果或稳定净收益；首次回执不证明命中占比。仅本次新源码16K完整资格，不继承旧R64-only/31094098的4K结果或105资格。359原件逐SHA回收。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261027_170946.csv](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/benchmark_results/raw_runs_20261027_170946.csv)；[summary_20261027_170946.csv](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/benchmark_results/summary_20261027_170946.csv)；[result.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
