<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T202526Z-kv-retain-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #95 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：失败多抢占覆盖，详analysis/source/kv-transaction/202526-independent-review.json
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T202526Z-kv-retain-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T20:25:27.942340+00:00",
  "profile_id": "kv_protocol_transient_host_retention",
  "phase": "short_context16k_long_protocol_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_one_victim_save_restore_publish_consume_diagnostic",
  "artifacts": "experiments/framework/20261021T202526Z-kv-retain-context16k-long",
  "conclusion": "独立416源/a1b691+616+31cc/e155/bc51/原SERVER/seed721201；32-0/524288in32768out/240.92993535706773s仅VERIFY诊断，KV521936/CPU6/32768MiB/preempt0→1；11条真实事件：SAVE16704tokens/718405632B完成后原free，首allocationNone free1030/prefix1044/16712known，HOST保留454skip后ZERO→RESTORE全42层718405632B回读byteequal→PUBLISH→DROP→runner六checks全true→原output处理8tokens；未提前消费/原worker事务不变；DB51619270→51819337三SHA变为d935/a5ca/a180，不能称cache不变或收益；20:31:52.483652Z68MiB0双栈闭无GPU进程/sourcefailures空；controller仅Z，shutdown错误保留；只一个victim成功，不等完整accuracy/取消失败多抢占覆盖，详analysis/source/kv-transaction/202526-independent-review.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T202526Z-kv-retain-context16k-long](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-043044.json](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-043044.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T202526Z-kv-retain-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-private-page-order](../../../analysis/2026-10-22-kv-private-page-order.md)；[2026-10-22-kv-transaction-protocol](../../../analysis/2026-10-22-kv-transaction-protocol.md)；[2026-10-22-kv-owned-page-order-plan](../../../analysis/2026-10-22-kv-owned-page-order-plan.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
