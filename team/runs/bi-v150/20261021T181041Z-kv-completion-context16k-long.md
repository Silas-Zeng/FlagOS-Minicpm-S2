<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T181041Z-kv-completion-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #83 · KV 生命周期观察

- **尝试**：分配失败、抢占与恢复的观察原件，不自动等于可回收机会。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败/524288in32768out/220.345997615717s仅诊断，KV521840
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T181041Z-kv-completion-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:10:42.597669+00:00",
  "profile_id": "sql_mixed_kv_completion_probe",
  "phase": "context16k_long_readonly_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_diagnostic_no_terminal_reclaim_opportunity",
  "artifacts": "experiments/framework/20261021T181041Z-kv-completion-context16k-long",
  "conclusion": "独立411源SHA/a4de/initb3b7/e155/bc51/原SERVER/seed721201；32成功0失败/524288in32768out/220.345997615717s仅诊断，KV521840；EngineCore199565 first_checked eligible/batchqueue2，35快照逐项对应原log，末周期2112core2109schedule/1failure-preempt-resume/obs0；失败free0需要1页queue1但terminal0/private0/coverage0，不实现drain；resume cache2944/floor16702/gap13758仅prefix exposure非已执行GPUwork/time，周期非全程；DBbeforeafter51619270实体3hash同1593/a0a590/90e9；preemptmetrics0到1/CPU6；18:17:30.243359Z完整post68MiB0双栈闭无GPU进程、owned退出或Z，见independent-diagnostic-review.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T181041Z-kv-completion-context16k-long](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-021539.json](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-021539.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T181041Z-kv-completion-context16k-long/exit-code)
- 相关说明：[2026-10-22-scheduler-kv-innovation](../../../analysis/2026-10-22-scheduler-kv-innovation.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
