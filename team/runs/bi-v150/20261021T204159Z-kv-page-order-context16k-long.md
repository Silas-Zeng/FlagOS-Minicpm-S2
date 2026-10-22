<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T204159Z-kv-page-order-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #96 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：独立416源/0e2115+616+31cc+c95f/e155/bc51/原SERVER/seed721201；不与202526增长DB诊断算收益，未来free顺序改变保留，非完整accuracy/默认资格
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T204159Z-kv-page-order-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T20:42:01.277291+00:00",
  "profile_id": "kv_protocol_private_page_order",
  "phase": "short_context16k_long_protocol_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_private_order_restore_one_victim_verified",
  "artifacts": "experiments/framework/20261021T204159Z-kv-page-order-context16k-long",
  "conclusion": "独立416源/0e2115+616+31cc+c95f/e155/bc51/原SERVER/seed721201；32-0/524288in32768out/227.54834548803046s/2448.0775670122475total仅VERIFY诊断；KV521936/CPU6/32768MiB/preempt0→1；真实PRIVATE1044→66run，同1044页/Block对象/实际list/host逻辑序，ZERO/RESTORE/42层回读各2772调用、718405632B全bytepass；12事件SAVE/free→454skip持HOST→排序→ZERO/RESTORE→publish/drop→runner六checks/原output8tokens；DBbeforeafter51819337三SHA同d935/a5ca/a180实体复算；20:47:45.919662Z68MiB0双栈closed无GPU进程/sourcefailures空；不与202526增长DB诊断算收益，未来free顺序改变保留，非完整accuracy/默认资格；早退仅研究未混入。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T204159Z-kv-page-order-context16k-long](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-044704.json](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-044704.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T204159Z-kv-page-order-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-private-page-order](../../../analysis/2026-10-22-kv-private-page-order.md)；[2026-10-22-kv-transaction-protocol](../../../analysis/2026-10-22-kv-transaction-protocol.md)；[2026-10-22-kv-owned-page-order-plan](../../../analysis/2026-10-22-kv-owned-page-order-plan.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
