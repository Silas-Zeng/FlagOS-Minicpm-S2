<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T172509Z-main594-m64-fixed-address-4096-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #341 · BI-V150特定形状GEMM

- **尝试**：main594控制4K暖均5847.6667、16K4192.49；M64首暖低1.70966%，但旧4K控制与候选跨容器，不能归因于方法。M32首暖低0.23295%，与16K控制同在重启后；两者按约定停止且请求全成功。后续以main241研究，原main594 4K另作重启后两轮复查。
- **改动**：相关实现 [2026-10-26-gemm-target-priority.json](../../../analysis/2026-10-26-gemm-target-priority.json)；[2026-10-26-gemm-component-results.json](../../../analysis/2026-10-26-gemm-component-results.json)；[candidate.py](../../../experiments/framework/20261026T035139678096Z-biv150-down-wide-working-set-component/source/candidate.py)；[candidate.py](../../../experiments/framework/20261026T034152136640Z-biv150-down-small-working-set-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/archive-receipt.json)；[2026-10-26-team-main594-source-manifest.json](../../../analysis/2026-10-26-team-main594-source-manifest.json)；[2026-10-26-team-main594-github-receipt.json](../../../analysis/2026-10-26-team-main594-github-receipt.json)；[candidate.py](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/archive-receipt.json)；[README.md](../../../analysis/m64-fixed-address-production-20261026/README.md)；[raw_runs_20261026_234328.csv](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/benchmark_results/raw_runs_20261026_234328.csv)；[interruption-recovery.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/interruption-recovery.json)；[result.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/posthoc-provider-recovery/result.json)；[raw_runs_20261027_004556.csv](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/raw_runs_20261027_004556.csv)；[summary_20261027_004556.csv](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/summary_20261027_004556.csv)；[state.json](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds-control/state.json)；[archive-receipt.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/archive-receipt.json)；[supervisor-final.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds-control/supervisor-final.json)；[result.json](../../../experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/archive-receipt.json)；[supervisor-final.json](../../../experiments/official/20261026T180653Z-main594-m32-fixed-address-16384-four-rounds-control/supervisor-final.json)；[archive-receipt.json](../../../experiments/official/20261026T180653Z-main594-m32-fixed-address-16384-four-rounds/archive-receipt.json)；[container-observation.json](../../../experiments/environment/20261026T185836Z-container-context/container-observation.json)；[comparison-context.json](../../../experiments/environment/20261026T185836Z-container-context/comparison-context.json)；[summary.json](../../../experiments/framework/20261027T190017939358Z-qkv-bn32-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T190017939358Z-qkv-bn32-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T190017939358Z-qkv-bn32-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T190017939358Z-qkv-bn32-component/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：精确命令、版本及原始结果见本轮manifest/state、source和日志。
- **结果**：停止当前M64生产路线；保留组件与官方负结果，不开优化PR或拼成完整四轮成绩。
- **是否保留**：暂不恢复M64生产路线；先复查同源码4K环境漂移，原组件和两轮记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T172509Z-main594-m64-fixed-address-4096-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-26T17:25:09+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "594ae2a9d17aadc4587ad54ade2b34e17f4af990",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "main594_m64_fixed_address_firstwarm_negative",
  "artifacts": "experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds",
  "conclusion": "M64固定寻址生产候选同main594/native14f/初始DB207f，4K冷轮5014.13、首暖5743.94 tok/s；对同档首暖5843.85观察低1.70966%，按约定提前停止，512请求全部SUCCESS，新旧实际路径通过。原组件省1.47792%未转为本次官方首暖收益；单组不证明稳定回退或纯kernel因果。未跑后两轮、16K或105，无新基线/合并资格。SIGTERM来自性能监督器，不是框架报错；source/native不变、DB与设备清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T172509Z-main594-m64-fixed-address-4096-four-rounds](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261027_012726.csv](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/benchmark_results/raw_runs_20261027_012726.csv)；[result.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
