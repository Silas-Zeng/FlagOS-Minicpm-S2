<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T105243Z-main56-control-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #371 · LM-head温度epilogue融合

- **尝试**：原main56+受测8d1a五文件已通过中文PR84合并，main dac1b8fb。4K同KV时间相近对照暖均5923.116667→5971.44 tok/s，单组观察+0.8158%；事后首暖−1.3314%、两A漂移+0.3447%，不称稳定幅度或新官方基线。16K暖均4529.79对4526.57（观察+0.0710%），KV不同；同源105为103/105 valid/pass，但head32/64及Q32未覆盖，组件数学资格另列。BN256扩展Event负，停止且不含在PR84。旧R64-only结果不与新组合相加。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：同main56/native14f/初始DB/参数，KV548288；两A暖均漂移+0.3447%，326原件逐SHA。
- **结果**：新A暖均5923.116667；同KV候选B观察+0.8158%，1024成功。
- **是否保留**：支持按小收益建立代码PR；不声称稳定幅度或新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T105243Z-main56-control-4k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T10:52:43+00:00",
  "profile_id": "lm-head-temperature",
  "phase": "official_control",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "lm_head_temperature_same_kv_4k_control_complete",
  "artifacts": "experiments/official/20261027T105243Z-main56-control-4k-four-rounds",
  "conclusion": "时间相近main56原官方4K控制四轮[5659.63, 5828.66, 5895.09, 6045.6]tok/s，弃首暖均5923.116667，1024SUCCESS，807源/tree1e9af、native14f、初始DB207f与原参数/原栈通过，KV548288与新8d1a候选B相同。已登记B暖均5971.440000对本A观察+0.815843%，首暖-1.331352%；旧A暖均5902.770000，两A漂移+0.344697%，各轮波动保留，不宣称稳定幅度。支持按小收益建立中文代码PR并引用已测组件和同源原105，不重复测试；105为103/105但head分支未覆盖，组件严格逐位/IDs/RNG资格与模型准确率分开。16K现有A/B容量不同，仍仅观察；4K本A晚于B且两组暖轮内有升温趋势，不包装成随机交错因果或新稳定基线。326原件逐SHA，源码/native不变、DB恢复和清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T105243Z-main56-control-4k-four-rounds](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261027_185356.csv](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/benchmark_results/raw_runs_20261027_185356.csv)；[summary_20261027_185356.csv](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/benchmark_results/summary_20261027_185356.csv)；[result.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
