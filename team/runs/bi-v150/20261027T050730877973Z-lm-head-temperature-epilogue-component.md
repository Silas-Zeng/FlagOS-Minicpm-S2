<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T050730877973Z-lm-head-temperature-epilogue-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #360 · LM-head温度epilogue融合

- **尝试**：新8d1a同源原官方4K/16K各四轮，暖均5971.44/4529.79 tok/s，对各自A观察+1.1634%/+0.0710%；两档KV不同，非严格因果或稳定收益，不定新基线。原105为103/105 valid/pass，但head32/64和Q32未覆盖，分支准确率未证。旧31094098与局部组件结果另列，不相加。

同融合基线上的R32 BN256扩展已完成：十门过，但完整ABBA Event慢2.6150%、wall快5.7801%，按nonpositive停止，不影响原BN64融合生产结果。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：R64真实head W/合成hidden，唯一完整eager ABBA，原采样链不变。
- **结果**：R64真实LM-head权重130560×2048、合成hidden；保留原BF16舍入后融合FP32转换与温度除法，原stats/top-p/RNG不变。10组逐位/FP64/采样ID/RNG/换值Graph及输入不变检查通过。完整eager head+Sampler唯一ABBA含分配与提交，Event3.828030→3.165252ms（省17.3138%），wall4.
- **是否保留**：保留局部正信号，待实际服务验证；不是官方收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T050730877973Z-lm-head-temperature-epilogue-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T050730877973Z",
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
  "status": "lm_head_temperature_component_positive",
  "artifacts": "experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component",
  "conclusion": "R64真实LM-head权重130560×2048、合成hidden；保留原BF16舍入后融合FP32转换与温度除法，原stats/top-p/RNG不变。10组逐位/FP64/采样ID/RNG/换值Graph及输入不变检查通过。完整eager head+Sampler唯一ABBA含分配与提交，Event3.828030→3.165252ms（省17.3138%），wall4.165081→3.655269ms（省12.2401%），无CPU节流。寄存器31→37，shared40960B不变，两臂spill0，无候选新增持久权重副本。保留局部正信号，下一步最窄生产接入；尚非模型准确率或官方吞吐资格，不迁移为整模收益。main56/native14f，DB恢复、源码/native不变及清理通过。44份原件逐SHA核验。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T050730877973Z-lm-head-temperature-epilogue-component](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
