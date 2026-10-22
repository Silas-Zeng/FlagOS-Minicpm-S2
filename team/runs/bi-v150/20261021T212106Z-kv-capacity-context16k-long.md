<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T212106Z-kv-capacity-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #99 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：227.19113439507782s/2451.9266629097337total/TTFT62762.77446313179ms
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T212106Z-kv-capacity-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T21:21:07.683129+00:00",
  "profile_id": "kv_capacity_necessary_bound",
  "phase": "short_context16k_long_protocol_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_fast_reject462_restore_verified",
  "artifacts": "experiments/framework/20261021T212106Z-kv-capacity-context16k-long",
  "conclusion": "独立416源/67e4+616+31cc+c95f/e155/bc51/原SERVER/seed721201，32-0/524288in32768out/227.19113439507782s/2451.9266629097337total/TTFT62762.77446313179ms，仅VERIFY1诊断；KV521840/CPU6/32768MiB/preempt0→1；真实fast_rejects462，首free1039<P1043/R16688/717717504B，明确快路不触后续hash-history-allocator但无CPU耗时结论；PRIVATE1043→66run，真实ZERO/RESTORE/42层回读各2772调用全bytepass，publish/drop/runner六checks/原output16token消费；DBbeforeafter51919340三SHA同89743b20/29d740d5/71ac1989实体复算；21:27:50.103577Z416源post无变/68MiB0双栈closed无GPU进程，无ERROR但forcekill WARN保留；非新RESTORE_FULL证据/不算性能收益或完整accuracy。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T212106Z-kv-capacity-context16k-long](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-052611.json](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-052611.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T212106Z-kv-capacity-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-capacity-full-phase](../../../analysis/2026-10-22-kv-capacity-full-phase.md)；[2026-10-22-kv-full-restore-worker](../../../analysis/2026-10-22-kv-full-restore-worker.md)；[2026-10-22-kv-worker-implementation](../../../analysis/2026-10-22-kv-worker-implementation.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
