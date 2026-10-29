<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T153134266216Z-main594-m64-fixed-address-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #338 · BI-V150特定形状GEMM

- **尝试**：main594控制4K暖均5847.6667、16K4192.49；M64首暖低1.70966%，但旧4K控制与候选跨容器，不能归因于方法。M32首暖低0.23295%，与16K控制同在重启后；两者按约定停止且请求全成功。后续以main241研究，原main594 4K另作重启后两轮复查。 另有PR105 16K单次profile诊断完成128请求，posthoc缺fresh FX图证，非官方分数。
- **改动**：相关实现 [2026-10-26-gemm-target-priority.json](../../../analysis/2026-10-26-gemm-target-priority.json)；[2026-10-26-gemm-component-results.json](../../../analysis/2026-10-26-gemm-component-results.json)；[candidate.py](../../../experiments/framework/20261026T035139678096Z-biv150-down-wide-working-set-component/source/candidate.py)；[candidate.py](../../../experiments/framework/20261026T034152136640Z-biv150-down-small-working-set-component/source/candidate.py)；[manifest.json](../../../experiments/bundles/20261028T174702433104Z-biv150-down-groupm4-provided-linear-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T174702433104Z-biv150-down-groupm4-provided-linear-component/raw.tar.gz.storage.json)；[manifest.json](../../../experiments/bundles/20261028T175144741472Z-biv150-down-groupm4-provided-linear-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T175144741472Z-biv150-down-groupm4-provided-linear-component/raw.tar.gz.storage.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T182129Z-biv150-down-groupm4-official-staging-failed/raw.tar.gz.storage.json)；[manifest.json](../../../experiments/bundles/20261028T182535Z-native-gqa-overlap-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T182535Z-native-gqa-overlap-4k-four-rounds/raw.tar.gz.storage.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T173517Z-down-w8a16-weight-screen/raw.tar.gz.storage.json)；[manifest.json](../../../experiments/bundles/20261028T180055825919Z-down-w8a16-weight-only-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T180055825919Z-down-w8a16-weight-only-component/raw.tar.gz.storage.json)；[manifest.json](../../../experiments/bundles/20261028T180433423251Z-down-w8a16-weight-only-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T180433423251Z-down-w8a16-weight-only-component/raw.tar.gz.storage.json)；[manifest.json](../../../experiments/bundles/20261028T180844751927Z-down-w8a16-weight-only-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T180844751927Z-down-w8a16-weight-only-component/raw.tar.gz.storage.json)；[manifest.json](../../../experiments/bundles/20261028T184911473313Z-down-bm32bn32-tile-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T184911473313Z-down-bm32bn32-tile-component/raw.tar.gz.storage.json)；[manifest.json](../../../experiments/bundles/20261028T185611249396Z-down-bm32bn32-tile-handles-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T185611249396Z-down-bm32bn32-tile-handles-component/raw.tar.gz.storage.json)；[manifest.json](../../../experiments/official/20261028T183704Z-native-gqa-overlap-4k-four-rounds/manifest.json)；[result.json](../../../experiments/official/20261028T183704Z-native-gqa-overlap-4k-four-rounds/result.json)；[raw_runs_20261029_023914.csv](../../../experiments/official/20261028T183704Z-native-gqa-overlap-4k-four-rounds/raw_runs_20261029_023914.csv)；[manifest.json](../../../experiments/bundles/20261028T183704Z-native-gqa-overlap-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T183704Z-native-gqa-overlap-4k-four-rounds/raw.tar.gz.storage.json)；[result.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/archive-receipt.json)；[2026-10-26-team-main594-source-manifest.json](../../../analysis/2026-10-26-team-main594-source-manifest.json)；[2026-10-26-team-main594-github-receipt.json](../../../analysis/2026-10-26-team-main594-github-receipt.json)；[candidate.py](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/archive-receipt.json)；[README.md](../../../analysis/m64-fixed-address-production-20261026/README.md)；[raw_runs_20261026_234328.csv](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/benchmark_results/raw_runs_20261026_234328.csv)；[interruption-recovery.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/interruption-recovery.json)；[result.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/posthoc-provider-recovery/result.json)；[raw_runs_20261027_004556.csv](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/raw_runs_20261027_004556.csv)；[summary_20261027_004556.csv](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/summary_20261027_004556.csv)；[state.json](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds-control/state.json)；[archive-receipt.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/archive-receipt.json)；[supervisor-final.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds-control/supervisor-final.json)；[result.json](../../../experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/archive-receipt.json)；[supervisor-final.json](../../../experiments/official/20261026T180653Z-main594-m32-fixed-address-16384-four-rounds-control/supervisor-final.json)；[archive-receipt.json](../../../experiments/official/20261026T180653Z-main594-m32-fixed-address-16384-four-rounds/archive-receipt.json)；[container-observation.json](../../../experiments/environment/20261026T185836Z-container-context/container-observation.json)；[comparison-context.json](../../../experiments/environment/20261026T185836Z-container-context/comparison-context.json)；[summary.json](../../../experiments/framework/20261027T190017939358Z-qkv-bn32-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T190017939358Z-qkv-bn32-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T190017939358Z-qkv-bn32-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T190017939358Z-qkv-bn32-component/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：实际生产MM callback对候选、同原W和预分配out，唯一ABBA各16次完整Graph；profiler关闭、DB恢复，无pack或永久副本。
- **结果**：M64固定寻址单组组件省1.47792%，8门过/无额外权重；待官方净收益。
- **是否保留**：保留组件正信号；最小生产接线后同main594官方对照，尚不合并或更新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T153134266216Z-main594-m64-fixed-address-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T15:31:34.266216+00:00",
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
  "status": "main594_m64_fixed_address_positive",
  "artifacts": "experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component",
  "conclusion": "新main594实际MM-out，固定M64/N2048网格寻址，原tile/runtime K/dot/原W不变，无额外权重。8类数值/FP64/换值Graph/side门及RNG通过；唯一ABBA完整MM Event 59.546635→58.666585us，单组省1.47792%。实际rcp3→0，SME/async/shared/regs不变。仅单层组件信号，未有42层/模型/105/官方或新基线资格；保留进入同版本生产对照。DB/source/进程与9031清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T153134266216Z-main594-m64-fixed-address-component](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
