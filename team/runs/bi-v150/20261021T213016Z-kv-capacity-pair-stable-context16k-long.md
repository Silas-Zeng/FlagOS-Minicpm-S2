<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T213016Z-kv-capacity-pair-stable-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #100 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：220.5050202300772s/2526.2735488686926total/TTFT62602.81379344815ms
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T213016Z-kv-capacity-pair-stable-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T21:30:18.827999+00:00",
  "profile_id": "kv_capacity_pair_stable_verify0",
  "phase": "short_context16k_long_performance_baseline",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_capacity_pair_base_kv_mismatch_db_matched",
  "artifacts": "experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long",
  "conclusion": "独立410源/stable080656/e155/bc51/原SERVER/packages/seed721201与前stable同、0协议marker；32-0/524288in32768out/220.5050202300772s/2526.2735488686926total/TTFT62602.81379344815ms；KV521936/CPU6/物理32768MiB/preempt0→1，DBbeforeafter51919340三SHA同89743b20/29d740d5/71ac1989实体复算；21:35:42.054721Z410源post无变/68MiB0双栈closed无GPU进程；raw完成后shutdown EngineDeadError/forcekill WARN原样保留，非测前错误；VERIFY0，root已实查在途213616候选KV521840对基点521936差96，容量已失配，不补stable凑容量；213616已完成且DBafter仍51919340三SHA同，容量失配不变，不报gain。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T213016Z-kv-capacity-pair-stable-context16k-long](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-053515.json](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-053515.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T213016Z-kv-capacity-pair-stable-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-capacity-full-phase](../../../analysis/2026-10-22-kv-capacity-full-phase.md)；[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
