<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T230548Z-preemption-snapshot-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #109 · 抢占请求选择与进展

- **尝试**：抢占瞬间观察、请求选择及其对照；失配结果也保留。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：失败：31running prompt均16384/max1024/output327..569，free0派生需1/failed index1/旧queued1各span1
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T230548Z-preemption-snapshot-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T23:05:50.650959+00:00",
  "profile_id": "running_preemption_snapshot_observer",
  "phase": "short_context16k_long_cpu_snapshot_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_real_preemption_snapshot_no_policy_no_gain",
  "artifacts": "experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long",
  "conclusion": "framework唯一6eb45实际全审pass/report06c16d26；本agent只读原报告登记不重复入口或raw全审；413源/c6b3-ce4e-6ec5/e155/原bc51-SERVER-contextlong-seed721201，32-0/524288in32768out/220.41899300506338s/2527.259526982793total/TTFT62506.0147101176ms仅诊断；KV521936/CPU6/32GiB/DB51919340三SHA89729d71ac前后同/preempt0→1。Engine240315同PID CORE→ARMED→eligible→唯一completeTrue首次失败：31running prompt均16384/max1024/output327..569，free0派生需1/failed index1/旧queued1各span1；最小remaining455在index0已schedule1，原tail index30 output327/rem697/owned-private1045/shared0/hashed1044/R16704。29个非protected非failed结构候选含原tail，不选评分/不改victim/不把全页当重算或保证公平；23:11:57.075293Z413源live无变/68-0双栈closed无GPU进程，测前ERROR空/原raw后shutdown ERROR-WARN保留。API进程REJECTED与Engine真实成功事件分别保留，不用INSTALLED替代观测；无gain/accuracy/controller实现。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T230548Z-preemption-snapshot-context16k-long](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-071047.json](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-071047.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long/exit-code)
- 相关说明：[2026-10-22-preemption-snapshot-230548-result](../../../analysis/2026-10-22-preemption-snapshot-230548-result.md)；[2026-10-22-preemption-snapshot-230548-hardware](../../../analysis/2026-10-22-preemption-snapshot-230548-hardware.md)；[2026-10-22-preemption-snapshot-implementation](../../../analysis/2026-10-22-preemption-snapshot-implementation.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
