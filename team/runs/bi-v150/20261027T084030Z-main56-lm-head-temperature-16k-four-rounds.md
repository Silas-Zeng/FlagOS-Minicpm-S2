<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T084030Z-main56-lm-head-temperature-16k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #365 · LM-head温度epilogue融合

- **尝试**：新8d1a R32+R64原官方16K暖均4529.79对A4526.57 tok/s，单组+0.0710%、KV不同，非严格因果。完整105取得103/105（98.0952%）且运行/清理通过，但head32/64与prefill Q32未覆盖，不授分支准确率资格；本新源4K仍在跑。旧31094098的4K+0.3109%单列，组件收益不相加。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：仅1个冷轮，非完整官方；R32+R64后继另行验证。
- **结果**：R64-only 16K首冷4029.77 tok/s、128成功；KV548288≠548384资格停止。head无覆盖/无异常，原栈及清理通过。
- **是否保留**：停止旧R64-only无覆盖16K；非数值错误，不计算收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T084030Z-main56-lm-head-temperature-16k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T08:40:30+00:00",
  "profile_id": "lm-head-temperature",
  "phase": "official_screen",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "false",
  "status": "lm_head_temperature_r64_16k_kv_mismatch_stopped",
  "artifacts": "experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds",
  "conclusion": "R64-only head温度epilogue候选main56/809/native14f原官方16K筛选，仅首冷4029.77 tok/s、128请求SUCCESS。实际KV548288对A548384，资格不匹配触发监督SIGTERM；原stack实际选中，head READY/SELECTED/SAMPLED均未覆盖、abnormal=false，无REJECTED/RAW_FALLBACK。原completed=false/KeyboardInterrupt(15)保留，DB恢复/source/native不变及清理通过。不是数值错误，非完整官方四轮，不计算收益或继承105资格；停止此R64-only无覆盖16K，R32+R64后继单列。346原件逐SHA回收。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T084030Z-main56-lm-head-temperature-16k-four-rounds](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261027_164144.csv](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/benchmark_results/raw_runs_20261027_164144.csv)；[result.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
