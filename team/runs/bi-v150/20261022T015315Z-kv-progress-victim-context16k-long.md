<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T015315Z-kv-progress-victim-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #110 · 抢占请求选择与进展

- **尝试**：抢占瞬间观察、请求选择及其对照；失配结果也保留。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：全bytespass/0ZERO/fast454/runner6/consumer9/host释放，原preempt0→1
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T015315Z-kv-progress-victim-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T01:53:17.513041+00:00",
  "profile_id": "single_progress_victim_full_restore_verify1",
  "phase": "short_context16k_long_progress_victim_mechanism_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_distinct_progress_victim_full_42layer_verified_DB_changed",
  "artifacts": "experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long",
  "conclusion": "本agent唯一b7ff实际全审exit0/pass/reportf776f89b；417源/72942-bbb49-1f8/原init791c-worker5d9a-txn84be-e155-c95f/bc51-SERVER-long-seed721201/VERIFY1且无6a/c6；32-0/524288in32768out/238.5769370230846s/2334.9113579494883total/TTFT63043.00184814201ms仅诊断。真实Engine250261仅一次主动选择，28候选，selected原index2/output552/rem472/ownedprivate1059不同于tailindex30/output327，保护minrem455/maxconfirmed569且未scheduled；同selected rid完成SAVE-FULL-DROP serial123，R16928/P1058/728039424B/source37runs/SAVE1554/目的65/FULL及42层回读各2730/全bytespass/0ZERO/fast454/runner6/consumer9/host释放，原preempt0→1。KV521936/CPU6/32768MiB；DB51919340三SHA89729d71ac→52319474三SHAdc2c7646-0dc7a465-c05d7e31（+4表134行），不可比较gain或当新accuracy/公平证明；01:59:22.547218Z417源live无变/68-0双栈closed无GPU进程，测前与shutdown ERROR皆空/forcekill WARN留。旧f43未执行，POSIX修复b7ff已终审，原件与负例不改。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T015315Z-kv-progress-victim-context16k-long](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-095836.json](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-095836.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T015315Z-kv-progress-victim-context16k-long/exit-code)
- 相关说明：[2026-10-22-progress-victim-015315-result](../../../analysis/2026-10-22-progress-victim-015315-result.md)；[2026-10-22-progress-victim-015315-hardware](../../../analysis/2026-10-22-progress-victim-015315-hardware.md)；[2026-10-22-progress-victim-performance-plan](../../../analysis/2026-10-22-progress-victim-performance-plan.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
