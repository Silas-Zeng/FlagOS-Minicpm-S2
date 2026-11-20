<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #398 · 原生BF16 GQA：mixed S4覆盖扩展

- **尝试**：原c75db仅覆盖B64/S2与B32/S4，真实mixed prefix61原回落Triton。B61/B60完整mixed组件Event省8.8533%/25.5143%、B63位型通过；仅helper/CPP扩32–63且排40，CU/chooser/S2不动。原官方4K两轮首暖6168.07对A6301.93观察−2.1241%后主动停，KV548432对548336不同，不能严格归因。候选不合并，停止16K/105，不定新基线；正确性门通过与性能筛选负分列。
- **改动**：相关实现 [summary.json](../../../experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T181731151743Z-corex-native-gqa-mixed61-component/manifest.json)；[raw.tar.xz.storage.json](../../../experiments/bundles/20261027T181731151743Z-corex-native-gqa-mixed61-component/raw.tar.xz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T182749Z-native-gqa-mixed-s4-production-build/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T182749Z-native-gqa-mixed-s4-production-build/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T182749Z-native-gqa-mixed-s4-production-build/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T182749Z-native-gqa-mixed-s4-production-build/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/summary.json)；[raw-evidence.json](../../../experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：KV548432对548336不同，不严格归因；原partial/KeyboardInterrupt15及DB/源/两库清理保留，非数值或模型故障。
- **结果**：原官方4K两轮512成功；首暖6168.07对6301.93观察−2.1241%，按预设主动停止。
- **是否保留**：候选不合并；停止16K/105，不更新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "20261027T183747Z",
  "profile_id": "native-gqa-mixed-s4",
  "phase": "official",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b3b87d2a1c13448bd8c6bc24e8045c0458b8b9dd",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "native_gqa_mixed_s4_official_partial_negative",
  "artifacts": "experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds",
  "conclusion": "mixed-S4 f6b4／b9bff11d原官方4K性能筛选两轮512请求成功，首暖6168.07对A145950首暖6301.93观察−2.1241%，按预设主动停止，第三／四轮、16K和105不跑；候选不合并。首冷新eager覆盖及原栈门通过，KV548432对548336不同，不能严格归因；state completed=false及KeyboardInterrupt(15)是信号收尾原件，非数值／服务错误，DB／源码／两库／清理正常。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds](../../../experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
