<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T145950Z-native-gqa-abi-v2-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #381 · CoreX原生BF16 GQA：单页与完整分页

- **尝试**：PR92已合并main b3b87d2；当前有效4K/16K暖6481.2267/4826.4467、102/105，保留KV差异与105分支覆盖限制。同轮macro0/1 N64/S2完整producer+原reducer Event省1.0521%、wall省1.1805%，新增位型/Graph全过，保留小正候选但未接生产/官方；旧macro1对Triton22.38%不是此增量。
- **改动**：相关实现 [comparison.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/result.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/result.json)；[recompute.py](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/recompute.py)；[llvm-build.log](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/related-cpu/113301/llvm-build.log)；[compile-check.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/compile-proof/compile-check.json)；[backend-equivalence.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source/backend-equivalence.json)；[archive-receipt.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/result.json)；[independent-review.md](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/comparison.json)；[results.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/results.json)；[archive-receipt.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/comparison.json)；[results.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json)；[summary.json](../../../experiments/official/20261027T140221Z-native-gqa-4k-four-rounds/summary.json)；[raw-evidence.json](../../../experiments/official/20261027T140221Z-native-gqa-4k-four-rounds/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T140221Z-native-gqa-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T140221Z-native-gqa-4k-four-rounds/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/summary.json)；[raw-evidence.json](../../../experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/raw.tar.gz.storage.json)；[summary.json](../../../experiments/official/20261027T152326Z-native-gqa-abi-v2-16k-four-rounds/summary.json)；[raw-evidence.json](../../../experiments/official/20261027T152326Z-native-gqa-abi-v2-16k-four-rounds/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T152326Z-native-gqa-abi-v2-16k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T152326Z-native-gqa-abi-v2-16k-four-rounds/raw.tar.gz.storage.json)；[summary.json](../../../experiments/accuracy/20261027T161121Z-native-gqa-abi-v2-native14f-math500/summary.json)；[raw-evidence.json](../../../experiments/accuracy/20261027T161121Z-native-gqa-abi-v2-native14f-math500/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T161121Z-native-gqa-abi-v2-native14f-math500/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T161121Z-native-gqa-abi-v2-native14f-math500/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T163852438077Z-corex-native-gqa-s2-v-overlap-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T163852438077Z-corex-native-gqa-s2-v-overlap-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T163852438077Z-corex-native-gqa-s2-v-overlap-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T163852438077Z-corex-native-gqa-s2-v-overlap-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T180400292465Z-native-gqa-macro01-hotspot-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T180400292465Z-native-gqa-macro01-hotspot-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T180400292465Z-native-gqa-macro01-hotspot-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T180400292465Z-native-gqa-macro01-hotspot-component/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：386原件；KV548336对548288，不称严格单因子因果或稳定幅度。
- **结果**：原官方4K暖6481.2267对A5971.44，观察+8.5371%；1024成功，S2/S4实际覆盖。
- **是否保留**：保留整模正信号；KV差48，待16K/105后定基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T145950Z-native-gqa-abi-v2-4k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "20261027T145950Z",
  "profile_id": "corex-native-gqa-loop",
  "phase": "official",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "dac1b8fb48e7983e48283032efeee9b592c5fbe5",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "native_gqa_abi_v2_4k_positive_observation",
  "artifacts": "experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds",
  "conclusion": "ABI v2源c75db/814、SOf720，保原CU/reducer/runner/采样，仅修2048/2560准入。原官方4K四轮5349.02/6301.93/6445.80/6695.95，弃首暖均6481.2267，对A5971.44观察+8.5371%，1024/1024成功。S2/S4各自SELECTED/CAPTURED，实际Q2048；原栈和DB/source/native/清理通过。KV548336对548288差48，不宣称严格单因子因果或稳定幅度。保留有效整模正信号，待16K与105后判断基线资格。386原件由原gzip包及manifest无损保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T145950Z-native-gqa-abi-v2-4k-four-rounds](../../../experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
