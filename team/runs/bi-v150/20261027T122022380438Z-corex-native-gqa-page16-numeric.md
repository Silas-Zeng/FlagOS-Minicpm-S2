<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T122022380438Z-corex-native-gqa-page16-numeric

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #373 · CoreX原生BF16 GQA：单页与完整分页

- **尝试**：服务post-RoPE Q实际连续2048。S4连续布局九门通过，组件Event省22.1242%；ABI v2原官方4K弃首暖均6481.2267对A5971.44，观察+8.5371%，1024成功且S2/S4实际覆盖。KV548336对548288差48，不称严格因果或稳定幅度；待16K/105后定基线。旧a596只有安装未覆盖，不是内核负收益；QKV切片2560组件及夹具失败保留。
- **改动**：相关实现 [comparison.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/result.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/result.json)；[recompute.py](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/recompute.py)；[llvm-build.log](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/related-cpu/113301/llvm-build.log)；[compile-check.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/compile-proof/compile-check.json)；[backend-equivalence.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source/backend-equivalence.json)；[archive-receipt.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/result.json)；[independent-review.md](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/comparison.json)；[results.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/results.json)；[archive-receipt.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/comparison.json)；[results.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json)；[summary.json](../../../experiments/official/20261027T140221Z-native-gqa-4k-four-rounds/summary.json)；[raw-evidence.json](../../../experiments/official/20261027T140221Z-native-gqa-4k-four-rounds/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T140221Z-native-gqa-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T140221Z-native-gqa-4k-four-rounds/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/summary.json)；[raw-evidence.json](../../../experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：main56/807/native14f；87原件逐SHA，exit0，DB/source/native清理通过。
- **结果**：v3七组全位型/FP64/Graph poison/side与coverage通过，无计时。
- **是否保留**：保留单页数值资格；不授历史loop/性能或模型资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T122022380438Z-corex-native-gqa-page16-numeric",
  "local_date": "2026-10-27",
  "utc_start": "20261027T122022380438Z",
  "profile_id": "corex-native-gqa-page16",
  "phase": "numeric_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "corex_native_gqa_page16_single_page_numeric_passed",
  "artifacts": "experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric",
  "conclusion": "v3原生CoreX单page16/D128、每KV头8Q数值诊断：仅修CPU覆盖判定两行，CU8545及原GPU数学不变。7组shared BF16、FP32/BF16 P、partial/max/sum跨臂全位型、独立FP64、输入只读/RNG、同址换值poisoned Graph、side stream及underflow三范围coverage均通过。owner73041于12:20:40 exit0，DB/source/native恢复及9031清理通过。87原件逐SHA复制，独审保留。只取得单页数值资格；timings空，无历史loop/tail/empty/reducer、性能、完整模型或准确率资格。旧120655 failed_stop和覆盖false原件不改，事后CPU解释与本次实际全门成功分开。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T122022380438Z-corex-native-gqa-page16-numeric](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/worker.log)；[gpu.csv](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/gpu.csv)；[exit-code](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
