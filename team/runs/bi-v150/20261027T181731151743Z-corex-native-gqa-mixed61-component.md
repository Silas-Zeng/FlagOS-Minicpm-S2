<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T181731151743Z-corex-native-gqa-mixed61-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #395 · 原生BF16 GQA：mixed S4覆盖扩展

- **尝试**：原c75db仅覆盖B64/S2与B32/S4，真实mixed prefix61原回落Triton。B61/B60完整mixed组件Event省8.8533%/25.5143%、B63位型通过；仅helper/CPP扩32–63且排40，CU/chooser/S2不动。原官方4K两轮首暖6168.07对A6301.93观察−2.1241%后主动停，KV548432对548336不同，不能严格归因。候选不合并，停止16K/105，不定新基线；正确性门通过与性能筛选负分列。
- **改动**：相关实现 [summary.json](../../../experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T181731151743Z-corex-native-gqa-mixed61-component/manifest.json)；[raw.tar.xz.storage.json](../../../experiments/bundles/20261027T181731151743Z-corex-native-gqa-mixed61-component/raw.tar.xz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T182749Z-native-gqa-mixed-s4-production-build/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T182749Z-native-gqa-mixed-s4-production-build/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T182749Z-native-gqa-mixed-s4-production-build/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T182749Z-native-gqa-mixed-s4-production-build/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/summary.json)；[raw-evidence.json](../../../experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：完整原件与manifest无损保存；不复跑未变检查，不叠加不同形状或组合收益。
- **结果**：回放真实step125的61decode＋1987prefill CPU几何，随机QKV；私有B61桥直接链接同f720 S4导出，CU不重编。
- **是否保留**：保留候选；等待独立模型／官方验证。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T181731151743Z-corex-native-gqa-mixed61-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T181731151743Z",
  "profile_id": "native-gqa-mixed-s4",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b3b87d2a1c13448bd8c6bc24e8045c0458b8b9dd",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_gqa_mixed61_component_positive",
  "artifacts": "experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component",
  "conclusion": "回放真实step125的61decode＋1987prefill CPU几何，随机QKV；私有B61桥直接链接同f720 S4导出，CU不重编。全2048输出逐位、原九门／Graph、parent／输入RNG／guard通过；完整mixed eager Event1.289934576→1.175732970ms省8.8533%，wall省5.6627%。保留生产扩覆盖候选，非模型／官方幅度；完整105份原件tar流无损xz。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T181731151743Z-corex-native-gqa-mixed61-component](../../../experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
