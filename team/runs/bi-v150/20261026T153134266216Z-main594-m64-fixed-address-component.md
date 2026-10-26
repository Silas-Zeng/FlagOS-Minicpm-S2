<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T153134266216Z-main594-m64-fixed-address-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #338 · BI-V150特定形状GEMM

- **尝试**：PR59合并后按main594真实MM-out继续。M64原路径已BN64/grid32，旧窄N停止；新增固定寻址仅去通用地址除余，原tile/math/自然权重保持。8门及RNG通过，单组完整MM Graph省1.47792%，无权重副本；保留组件正信号，待同main594生产官方对照，不把旧main6971数据迁为新候选收益。
- **改动**：相关实现 [2026-10-26-gemm-target-priority.json](../../../analysis/2026-10-26-gemm-target-priority.json)；[2026-10-26-gemm-component-results.json](../../../analysis/2026-10-26-gemm-component-results.json)；[candidate.py](../../../experiments/framework/20261026T035139678096Z-biv150-down-wide-working-set-component/source/candidate.py)；[candidate.py](../../../experiments/framework/20261026T034152136640Z-biv150-down-small-working-set-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/archive-receipt.json)；[2026-10-26-team-main594-source-manifest.json](../../../analysis/2026-10-26-team-main594-source-manifest.json)；[2026-10-26-team-main594-github-receipt.json](../../../analysis/2026-10-26-team-main594-github-receipt.json)；[candidate.py](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/archive-receipt.json)；[README.md](../../../analysis/m64-fixed-address-production-20261026/README.md)；[raw_runs_20261026_234328.csv](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/benchmark_results/raw_runs_20261026_234328.csv)；[interruption-recovery.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/interruption-recovery.json)；[result.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/posthoc-provider-recovery/result.json)；本轮准确变体以原件源码清单为准。
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
