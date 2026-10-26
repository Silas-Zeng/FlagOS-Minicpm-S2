<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T114133003627Z-gqa-scalar-page-base-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #333 · GQA标量KV页基址与动态for组合

- **尝试**：scalar＋while原8门过但慢0.38635%，SME未生效；后继for＋scalar＋一维i64正确性及逐位通过，实际SME LLVM/ASM各8条，却完整组件慢10.73864%。两者停止，不接模型；机制成功不等于净收益。
- **改动**：相关实现 [kernel.diff](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/source/kernel.diff)；[results.json](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/archive-receipt.json)；[gqa-scalar-page-base-114133.json](../../../analysis/main6971-084521-nodes/gqa-scalar-page-base-114133.json)；[kernel.diff](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/source/kernel.diff)；[results.json](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/archive-receipt.json)；[gqa-for-scalar-i64-134937.json](../../../analysis/main6971-084521-nodes/gqa-for-scalar-i64-134937.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：沿main6971实际N64/S2及4K replay32长度多重集，合成Q/KV；原page16 while、数学/reducer不变，仅标量化KV页基址＋二维span。原数值门后完整producer＋reducer一次16-call ABBA；不修改模型或官方参数。
- **结果**：8类门及跨臂逐位通过；Event0.542196542→0.544291317ms，慢0.38635%，停止。SGPR spill75为lane保存非HBM；实际SME仍0，for＋scalar未验证。
- **是否保留**：停止当前scalar-page-base实现，不进模型或合并；保留正确性通过及小幅负结果，不把一次ABBA写稳定因果。for＋scalar尚未实现验证，不自动列为已获益组合。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T114133003627Z-gqa-scalar-page-base-hotspot-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T11:41:33.003627+00:00",
  "profile_id": "gqa-scalar-page-base",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_scalar_page_base_negative_component",
  "artifacts": "experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component",
  "conclusion": "原page16 while与FP顺序不变，将KV页基址提升为标量并保留二维span；实际N64/S2、4K观测长度多重集、合成激活，8类原门及跨臂逐位通过。完整producer＋原reducer Graph一次ABBA Event0.542196542→0.544291317ms，慢0.38635%，wall慢0.18463%，停止不接模型。SGPR64→104、SGPR spill字段0→75；ASM保存于VGPR lane，private_segment=0，不能当HBM spill或独立耗时因果。真实LLVM/ASM SME传输仍0，mask14→62和TTGIR标签不是实际启用证明。动态for＋scalar只属未验证机制候选，不继承旧for或本轮资格；无官方/105/新基线，source/DB/native及清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T114133003627Z-gqa-scalar-page-base-hotspot-component](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
