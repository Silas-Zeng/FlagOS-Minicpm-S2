<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T115950Z-growth-v2-warm-repeat-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #71 · 准入与输出增长

- **尝试**：准入候选及其负结果、未激活和容量限制。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：Independent22sourceSHA
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T115950Z-growth-v2-warm-repeat-context16k-long",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T11:59:51.420638+00:00",
  "profile_id": "growth_admission_v2",
  "phase": "innovation_context16k_long_warm_repeat",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "warm_screen_no_positive_signal_no_integration",
  "artifacts": "experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long",
  "conclusion": "Independent22sourceSHA;exit0 actualEngineCore164138 CHECKED31589free1151future andDEFERRED2696free2722future;221.23383624106646s2517.95118443368total tok/s meanTTFT67130.2737761871ms;32success0failed524288in32768out;driverbc51seed721201;KV521840preempt0to0;DBbeforeafter512tables19130rows3hashesunchangedmatches115247after;descriptiveversus114713throughputminus0.4448385percent meanTTFTplus7.5110987percent butDB506to512stillconfounds;no positive throughputsignal/defaultoffretain/no integrationorlargeaccuracy;fullpost12:18:37.889080UTC68MiB0percentclosed"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T115950Z-growth-v2-warm-repeat-context16k-long](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long-control/postflight-full.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261021-200449.json](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261021-200449.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
