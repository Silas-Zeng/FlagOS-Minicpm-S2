<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T115247Z-growth-v2-innovation-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #70 · 准入与输出增长

- **尝试**：准入候选及其负结果、未激活和容量限制。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：Independent22sourceSHA
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T115247Z-growth-v2-innovation-context16k-long",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T11:52:47.849934+00:00",
  "profile_id": "growth_admission_v2",
  "phase": "innovation_context16k_long",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "activated_cold_db_confounded_independent_review",
  "artifacts": "experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long",
  "conclusion": "Independent22sourceSHA;exit0 actualEngineCore162561 CHECKED31595free1151future andDEFERRED2702free2722future;238.11336583085358s2339.4570819502455total tok/s meanTTFT68405.78491348424ms;32success0failed524288in32768out;driverbc51same16Klongseed721201;KV521936versuscontrol521840;preempt0to0versuscontrol0to1;DB506tables18926rowsto512tables19130rows adds6tables204rows all3hasheschange;beforematches114713after;longertimecoldconfounded necessarywarmonly no finalgainregressionoraccuracyclaim;fullpost11:59:21.132870UTC68MiB0percentclosed"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T115247Z-growth-v2-innovation-context16k-long](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long-control/postflight-full.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261021-195801.json](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261021-195801.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T115247Z-growth-v2-innovation-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
