<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T174414509153Z-main594-m32-fixed-address-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #343 · BI-V150特定形状GEMM

- **尝试**：main594分服务性能控制：4K暖均5847.6667、16K4192.49。M64固定寻址组件省1.47792%，但实际4K首暖5743.94对5843.85低1.70966%，512请求成功后按约定停止，无16K/105或合并。M32固定寻址八门通过，单组组件省0.87680%，保留准备独立生产对照；组件收益与模型结果分别保留。
- **改动**：相关实现 [2026-10-26-gemm-target-priority.json](../../../analysis/2026-10-26-gemm-target-priority.json)；[2026-10-26-gemm-component-results.json](../../../analysis/2026-10-26-gemm-component-results.json)；[candidate.py](../../../experiments/framework/20261026T035139678096Z-biv150-down-wide-working-set-component/source/candidate.py)；[candidate.py](../../../experiments/framework/20261026T034152136640Z-biv150-down-small-working-set-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/archive-receipt.json)；[2026-10-26-team-main594-source-manifest.json](../../../analysis/2026-10-26-team-main594-source-manifest.json)；[2026-10-26-team-main594-github-receipt.json](../../../analysis/2026-10-26-team-main594-github-receipt.json)；[candidate.py](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/archive-receipt.json)；[README.md](../../../analysis/m64-fixed-address-production-20261026/README.md)；[raw_runs_20261026_234328.csv](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/benchmark_results/raw_runs_20261026_234328.csv)；[interruption-recovery.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/interruption-recovery.json)；[result.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/posthoc-provider-recovery/result.json)；[raw_runs_20261027_004556.csv](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/raw_runs_20261027_004556.csv)；[summary_20261027_004556.csv](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/summary_20261027_004556.csv)；[state.json](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds-control/state.json)；[archive-receipt.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/archive-receipt.json)；[supervisor-final.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds-control/supervisor-final.json)；[result.json](../../../experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：精确命令、版本及原始结果见本轮manifest/state、source和日志。
- **结果**：保留M32单组小正，准备M32-only生产及16K同版本官方对照，不叠已停M64。
- **是否保留**：保留M32单组小正，准备M32-only生产及16K同版本官方对照，不叠已停M64。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T174414509153Z-main594-m32-fixed-address-component",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-26T17:44:14.509153+00:00",
  "profile_id": "shape-gemm",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "594ae2a9d17aadc4587ad54ade2b34e17f4af990",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "main594_m32_fixed_address_positive",
  "artifacts": "experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component",
  "conclusion": "M32固定寻址真实原MM-out同32/64/128、w8/s2和原W；原八项逐位/FP64/换值Graph/side及RNG通过。唯一ABBA完整MM Event 49.417669→48.984375us，单组省0.87680%；实际rcp3→0，SME6/async4/shared49152/regs25/spill0保持，无额外权重或workspace。仅layer0组件正信号，尚无模型/105/官方资格；DB207f恢复、source/进程与9031清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T174414509153Z-main594-m32-fixed-address-component](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
