<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T205819Z-kv-pair-page-order-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #98 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：未命中ERROR但原shutdown日志保留
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T205819Z-kv-pair-page-order-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T20:58:22.089683+00:00",
  "profile_id": "kv_pair_page_order_verify0",
  "phase": "short_context16k_long_performance_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_verify0_kv_db_mismatch_no_gain_attribution",
  "artifacts": "experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long",
  "conclusion": "独立416源/0e2115/e155/bc51/原SERVER/seed，32-0/524288in32768out/220.92108358303085s/2521.515787290788total/TTFT62648.45590684854ms；KV521840对base521936差96，同物理32GiB/CPU6；DBbefore51819337三SHA同baseafter，但candidateafter51919340变89743b20/29d740d5/71ac1989实体复算，双失配不报gain，不补stable伪造同cache；真实R16688/1043页/717717504B、SAVE966copy、PRIVATE1043→66、ZERO/RESTORE各2772，VERIFY0没有回读；462skip后publish/drop/runner六checks/原16token消费，不能套204159的1044页8token或回读；21:03:56.715618Z416源post无变/68MiB0双栈closed无GPU进程，本run未命中ERROR但原shutdown日志保留；容量67e4未执行。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T205819Z-kv-pair-page-order-context16k-long](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-050319.json](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-050319.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-pair-screen](../../../analysis/2026-10-22-kv-pair-screen.md)；[2026-10-22-kv-capacity-variance-audit](../../../analysis/2026-10-22-kv-capacity-variance-audit.md)；[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
