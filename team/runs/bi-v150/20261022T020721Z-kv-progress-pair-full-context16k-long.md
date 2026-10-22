<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T020721Z-kv-progress-pair-full-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #111 · 抢占请求选择与进展

- **尝试**：抢占瞬间观察、请求选择及其对照；失配结果也保留。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：218.39959823712707s/2550.627402689529total/TTFT62408.937510466785ms
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T020721Z-kv-progress-pair-full-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T02:07:24.204049+00:00",
  "profile_id": "progress_victim_pair_original_full_reference",
  "phase": "short_context16k_long_original_full_VERIFY0_reference",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_A_original_FULL_reference_pair_environment_mismatch_closed",
  "artifacts": "experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long",
  "conclusion": "本agent唯一3f1实际full验收exit0/pass/reportbe286a95；共同FULL416起点a67c/93375+同6a/init39fb+新manifest418，当前protocol1aff/worker5d9a-txn84be-e155/6ffb-1aaf/bc51原SERVER-contextlong-seed721201/VERIFY0；32-0/524288in32768out/218.39959823712707s/2550.627402689529total/TTFT62408.937510466785ms；KV521936/CPU6/32768MiB/preempt0→1，DB beforeafter52319474三SHAdc2c7646-0dc7a465-c05d7e31全同。actualPID252228/profile1/原int22447777996→父真list/三hook恢复，nonTorch1000341504/available22447777996.8；原FULL无progress decision，SAVE-FULL-DROP serial123/R16704-P1044-718405632B/SAVE24段1008/目的66段2772/0ZERO/fast454/runner6/consumer8/host释放，无回读。02:13:19.255413Z418源live/68-0双栈闭无GPU进程，测前和shutdown ERROR皆空/WARN留；B021658已完成且KV521840/启动分项失配，A为521936，DB四端三SHA仍同；三收益字段null，策略动态行为另列，本首对结束不追加盲复跑，不用015315诊断或旧pair作对照。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T020721Z-kv-progress-pair-full-context16k-long](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-101221.json](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-101221.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T020721Z-kv-progress-pair-full-context16k-long/exit-code)
- 相关说明：[2026-10-22-progress-pair-startup-geometry](../../../analysis/2026-10-22-progress-pair-startup-geometry.md)；[2026-10-22-progress-victim-performance-validation](../../../analysis/2026-10-22-progress-victim-performance-validation.md)；[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
