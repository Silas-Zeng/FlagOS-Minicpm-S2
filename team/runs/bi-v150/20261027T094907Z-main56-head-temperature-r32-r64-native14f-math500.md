<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #368 · LM-head温度epilogue融合

- **尝试**：新8d1a同源原官方4K/16K各四轮，暖均5971.44/4529.79 tok/s，对各自A观察+1.1634%/+0.0710%；两档KV不同，非严格因果或稳定收益，不定新基线。原105为103/105 valid/pass，但head32/64和Q32未覆盖，分支准确率未证。旧31094098与局部组件结果另列，不相加。

同融合基线上的R32 BN256扩展已完成：十门过，但完整ABBA Event慢2.6150%、wall快5.7801%，按nonpositive停止，不影响原BN64融合生产结果。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：353份原件逐SHA，native14f/DB207f及实际原栈闭合。
- **结果**：新8d1a/809源原105：103/105=98.0952%，valid/pass，105 stop、0错误/截断/空答，owner与清理通过。
- **是否保留**：保留当前源码的完整原官方准确率；head32/64与Q32未覆盖，分支资格另列。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T09:49:07+00:00",
  "profile_id": "lm-head-temperature",
  "phase": "accuracy",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "8",
  "num_prompts": "105",
  "profiler": "false",
  "status": "lm_head_temperature_r32_r64_accuracy_pass_scope_limited",
  "artifacts": "experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500",
  "conclusion": "新8d1a R32+R64 head温度epilogue809源/tree8060、本站native14f/DB207f，原Math500 Level3全105题及采样/服务参数不变：103/105=98.095238%，valid/pass；105 stop，0请求错误/截断/空最终答案/空提取。owner completed=true，原native34层/provider/Q-hoist栈有效，源码/native不变、DB恢复及设备/端口清理通过。head R32/R64和prefill Q32在本105均未实际覆盖，无异常回执；只保留当前完整源码的原官方准确率结果，不授予这三个优化分支准确率资格，也不与吞吐或旧版结果混算。353份原件逐SHA归档，原文件未改。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500)
- 原命令：[command.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/manifest.json)；[source-sha256.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/result.json)
- 日志 / 采样：[server.log](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/server.log)；[gpu.csv](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/gpu.csv)；[exit-code](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
