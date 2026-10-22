<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T214400Z-kv-full-restore-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #102 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：226.79482778999954s/2456.2112171085555total/TTFT62775.54467374284ms
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T214400Z-kv-full-restore-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T21:44:02.300924+00:00",
  "profile_id": "kv_full_restore_explicit_operation",
  "phase": "short_context16k_long_protocol_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_full_restore_no_zero_42layer_verified",
  "artifacts": "experiments/framework/20261021T214400Z-kv-full-restore-context16k-long",
  "conclusion": "2071独立入口实际exit0/pass；416源/1aff+84be+5d9a/c95f/e155/b4e-63947/080656/bc51原SERVER/seed721201/VERIFY1；32-0/524288in32768out/226.79482778999954s/2456.2112171085555total/TTFT62775.54467374284ms仅诊断，无收益比较；KV521936/CPU6/32768MiB/preempt0→1，DBbeforeafter51919340三SHA同89743b20/29d740d5/71ac1989实体复算；真实SAVE→RESTORE_FULL→DROP serial123且0ZERO，R16704/P1044/718405632B/source24runs/SAVE1008/目的66run/FULL与42回读各2772/全bytepass，zero_stagefalse/zero_calls0/fullcoverage/destbound，fast454/host释放/runner六checks/原consumer8；21:49:38.171431Z416源post无变/68MiB0双栈closed无GPU进程；测前ERROR空，raw后shutdown EngineDeadError/forcekill WARN分类保留；非旧16688/1043/16token，不是完整accuracy/默认资格或性能增益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T214400Z-kv-full-restore-context16k-long](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-054905.json](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-054905.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T214400Z-kv-full-restore-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-capacity-full-phase](../../../analysis/2026-10-22-kv-capacity-full-phase.md)；[2026-10-22-kv-full-restore-worker](../../../analysis/2026-10-22-kv-full-restore-worker.md)；[2026-10-22-kv-full-overwrite-no-zero-plan](../../../analysis/2026-10-22-kv-full-overwrite-no-zero-plan.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
