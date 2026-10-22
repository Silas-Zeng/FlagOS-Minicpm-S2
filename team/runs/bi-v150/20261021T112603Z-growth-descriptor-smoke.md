<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T112603Z-growth-descriptor-smoke

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #64 · 准入与输出增长

- **尝试**：准入候选及其负结果、未激活和容量限制。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：Independent23sourceSHA
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T112603Z-growth-descriptor-smoke",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T11:26:04.085632+00:00",
  "profile_id": "growth_descriptors",
  "phase": "constructor_only_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "diagnosis_complete_independent_review",
  "artifacts": "experiments/framework/20261021T112603Z-growth-descriptor-smoke",
  "conclusion": "Independent23sourceSHA;exit0 exactEngineCore156959 builtinAsyncScheduler;29guards onlynotV2false28true setuperrorsempty use_v2true;actual42layerBF16FullSpec16block128headFCFSreserveTrue;driverbc51 smoke_onlyseed721001;DB501tables18789rows3hashesunchanged;no perf;fullpost11:32:08.170110UTC68MiB0percentclosed;v2revision72d6 prepared withoutenvchanges"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T112603Z-growth-descriptor-smoke](../../../experiments/framework/20261021T112603Z-growth-descriptor-smoke)
- 原命令：[launch-command.json](../../../experiments/framework/20261021T112603Z-growth-descriptor-smoke/launch-command.json)；[command.txt](../../../experiments/framework/20261021T112603Z-growth-descriptor-smoke-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T112603Z-growth-descriptor-smoke-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T112603Z-growth-descriptor-smoke/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T112603Z-growth-descriptor-smoke-control/postflight-full.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T112603Z-growth-descriptor-smoke/server.log)；[gpu.csv](../../../experiments/framework/20261021T112603Z-growth-descriptor-smoke/gpu.csv)；[exit-code](../../../experiments/framework/20261021T112603Z-growth-descriptor-smoke/exit-code)
- 相关说明：[2026-10-21-growth-admission-diagnostic](../../../analysis/2026-10-21-growth-admission-diagnostic.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
