<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T083835962824Z-lm-head-temperature-r32-epilogue-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #364 · LM-head温度epilogue融合

- **尝试**：原main56+受测8d1a五文件已通过中文PR84合并，main dac1b8fb。4K同KV时间相近对照暖均5923.116667→5971.44 tok/s，单组观察+0.8158%；事后首暖−1.3314%、两A漂移+0.3447%，不称稳定幅度或新官方基线。16K暖均4529.79对4526.57（观察+0.0710%），KV不同；同源105为103/105 valid/pass，但head32/64及Q32未覆盖，组件数学资格另列。BN256扩展Event负，停止且不含在PR84。旧R64-only结果不与新组合相加。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：完整eager链ABBA含分配/提交，reg21/shared12288/spill0，无节流。
- **结果**：R32完整head+Sampler Event省10.05%、wall省11.00%；实际BM32/BN64/BK64/w8/s1，10门过。
- **是否保留**：保留局部正信号，待最窄生产验证；不与R64相加。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T083835962824Z-lm-head-temperature-r32-epilogue-component",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T08:38:35.962824+00:00",
  "profile_id": "lm-head-temperature",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "lm_head_temperature_r32_component_positive",
  "artifacts": "experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component",
  "conclusion": "R32真实LM-head权重130560×2048、合成hidden；原head首次捕获BM32/BN64/BK64/w8/s1/CTA1、grid2040，保BF16舍入后融合FP32/temperature，原stats/top-p/RNG不变。10组全scaled/filtered/ID/RNG/FP64/Graph及输入门通过。完整head+Sampler ABBA Event2.607533813→2.345596075ms（省10.0454%），wall3.163781250→2.815723500ms（省11.0013%）；两臂reg21/shared12288/spill0，无CPU节流。main56/native14f，DB恢复、源/native及清理通过。保留局部正信号，不是官方或模型准确率，不与R64组件收益相加；46份原件逐SHA回收。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T083835962824Z-lm-head-temperature-r32-epilogue-component](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
