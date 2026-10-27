<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T140221Z-native-gqa-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #379 · CoreX原生BF16 GQA：单页与完整分页

- **尝试**：服务post-RoPE Q实际连续2048。S4连续布局九门通过，组件Event省22.1242%；ABI v2原官方4K弃首暖均6481.2267对A5971.44，观察+8.5371%，1024成功且S2/S4实际覆盖。KV548336对548288差48，不称严格因果或稳定幅度；待16K/105后定基线。旧a596只有安装未覆盖，不是内核负收益；QKV切片2560组件及夹具失败保留。
- **改动**：相关实现 [comparison.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/result.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/result.json)；[recompute.py](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/recompute.py)；[llvm-build.log](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/related-cpu/113301/llvm-build.log)；[compile-check.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/compile-proof/compile-check.json)；[backend-equivalence.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source/backend-equivalence.json)；[archive-receipt.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/result.json)；[independent-review.md](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/comparison.json)；[results.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/results.json)；[archive-receipt.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/comparison.json)；[results.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json)；[summary.json](../../../experiments/official/20261027T140221Z-native-gqa-4k-four-rounds/summary.json)；[raw-evidence.json](../../../experiments/official/20261027T140221Z-native-gqa-4k-four-rounds/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T140221Z-native-gqa-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T140221Z-native-gqa-4k-four-rounds/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/summary.json)；[raw-evidence.json](../../../experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：379原件由原压缩包、manifest及恢复索引保存。
- **结果**：原官方4K暖5970.98、1024成功；native只有安装，无实际覆盖。
- **是否保留**：不判断native收益或失败，不改基线；保留ABI定位。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T140221Z-native-gqa-4k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "20261027T140221Z",
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
  "status": "native_gqa_4k_not_exercised",
  "artifacts": "experiments/official/20261027T140221Z-native-gqa-4k-four-rounds",
  "conclusion": "a596/814源、SO3ec3的原官方4K四轮为5019.70/5881.84/5929.94/6101.17 tok/s，暖均5970.9833，1024请求成功。仅INSTALL，零SELECTED/CAPTURED，不是有效native候选对照，不据此判内核负收益或改基线。KV548432对A548288不同。fresh FX证实post-RoPE Q行距2048，旧guard只准2560；后继修ABI，原件不改。379原件由原gzip包及manifest无损保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T140221Z-native-gqa-4k-four-rounds](../../../experiments/official/20261027T140221Z-native-gqa-4k-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
