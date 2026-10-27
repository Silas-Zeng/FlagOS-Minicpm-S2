<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T131805595037Z-corex-native-gqa-s4-synchronous-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #375 · CoreX原生BF16 GQA：单页与完整分页

- **尝试**：QKV切片布局组件（非服务post-RoPE布局）的S2/4K与S4/16K均9门通过，Event省21.7137%和22.1644%。服务post-RoPE Q实际contiguous2048；本批不含后续服务成绩，未证明实际启用或官方收益。旧夹具zero_失败及独立定位保留，v2仅修构造。
- **改动**：相关实现 [comparison.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/result.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/result.json)；[recompute.py](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/recompute.py)；[llvm-build.log](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/related-cpu/113301/llvm-build.log)；[compile-check.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/compile-proof/compile-check.json)；[backend-equivalence.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source/backend-equivalence.json)；[archive-receipt.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/result.json)；[independent-review.md](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/comparison.json)；[results.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/results.json)；[archive-receipt.json](../../../experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/comparison.json)；[results.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/comparison.json)；[results.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/results.json)；[independent-review.md](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：同dispatch、原内核未改；DB/source/native/9031清理通过。
- **结果**：S4/N32/KV16384、Qstride2560在第4案extra512守卫失败而停止，尚未计时；其余已记录数值/全partial逐位/Graph门通过。随后132510无GQA诊断复现同zero_错误写入，不能将此原失败归责新内核。保留119原件和原false；仅修输入构造后另run，原CU/bridge/容差不改。
- **是否保留**：保留原失败及定位证据；后继仅修夹具。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T131805595037Z-corex-native-gqa-s4-synchronous-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T131805595037Z",
  "profile_id": "corex-native-gqa-loop",
  "phase": "diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_s4_fixture_guard_failed",
  "artifacts": "experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component",
  "conclusion": "S4/N32/KV16384、Qstride2560在第4案extra512守卫失败而停止，尚未计时；其余已记录数值/全partial逐位/Graph门通过。随后132510无GQA诊断复现同zero_错误写入，不能将此原失败归责新内核。保留119原件和原false；仅修输入构造后另run，原CU/bridge/容差不改。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T131805595037Z-corex-native-gqa-s4-synchronous-component](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
