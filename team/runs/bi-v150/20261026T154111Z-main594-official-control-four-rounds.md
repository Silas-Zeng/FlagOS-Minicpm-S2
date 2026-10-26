<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T154111Z-main594-official-control-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #339 · BI-V150特定形状GEMM

- **尝试**：main594分服务性能控制：4K暖均5847.6667、16K4192.49。M64固定寻址组件省1.47792%，但实际4K首暖5743.94对5843.85低1.70966%，512请求成功后按约定停止，无16K/105或合并。M32固定寻址八门通过，单组组件省0.87680%，保留准备独立生产对照；组件收益与模型结果分别保留。
- **改动**：相关实现 [2026-10-26-gemm-target-priority.json](../../../analysis/2026-10-26-gemm-target-priority.json)；[2026-10-26-gemm-component-results.json](../../../analysis/2026-10-26-gemm-component-results.json)；[candidate.py](../../../experiments/framework/20261026T035139678096Z-biv150-down-wide-working-set-component/source/candidate.py)；[candidate.py](../../../experiments/framework/20261026T034152136640Z-biv150-down-small-working-set-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/archive-receipt.json)；[2026-10-26-team-main594-source-manifest.json](../../../analysis/2026-10-26-team-main594-source-manifest.json)；[2026-10-26-team-main594-github-receipt.json](../../../analysis/2026-10-26-team-main594-github-receipt.json)；[candidate.py](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/archive-receipt.json)；[README.md](../../../analysis/m64-fixed-address-production-20261026/README.md)；[raw_runs_20261026_234328.csv](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/benchmark_results/raw_runs_20261026_234328.csv)；[interruption-recovery.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/interruption-recovery.json)；[result.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/posthoc-provider-recovery/result.json)；[raw_runs_20261027_004556.csv](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/raw_runs_20261027_004556.csv)；[summary_20261027_004556.csv](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/summary_20261027_004556.csv)；[state.json](../../../experiments/official/20261026T164443Z-main594-control-16k-four-rounds-control/state.json)；[archive-receipt.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/archive-receipt.json)；[supervisor-final.json](../../../experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds-control/supervisor-final.json)；[result.json](../../../experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方4K先跑四轮；16K首轮中断，原日志/CSV未改；同初始DB与native、无profiler。
- **结果**：main594控制4K四轮暖均5847.6667，16K首轮中断；已恢复并补测，非完整新基线。
- **是否保留**：保留已完成4K控制，独立新服务补16K；候选也分负载启动，不拼接为同一连续8轮。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T154111Z-main594-official-control-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T15:41:11+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_control",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "594ae2a9d17aadc4587ad54ade2b34e17f4af990",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "main594_control_interrupted_4k_complete",
  "artifacts": "experiments/official/20261026T154111Z-main594-official-control-four-rounds",
  "conclusion": "main594原控制4K四轮全部SUCCESS，1024请求，4909.31/5843.85/5767.56/5931.59 tok/s，弃首均值5847.6667。首轮16K中断，无完整16K行，末尾无框架错误证据，原因未确认。原PID全部退出，原件及中断DB已保存，恢复初始207f；source/native未变。旧provider reader未识别CacheCompiledArtifact，已只读原产物补证，真实out调用1/4/3/3；旧false和原state保留，不重测4K。只作为独立4K控制，尚非完整官方基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T154111Z-main594-official-control-four-rounds](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_234328.csv](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/benchmark_results/raw_runs_20261026_234328.csv)；[summary_20261026_234328.csv](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/benchmark_results/summary_20261026_234328.csv)
- 日志 / 采样：[server.log](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261026T154111Z-main594-official-control-four-rounds/gpu.csv)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
