<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T220122Z-kv-memory-capacity-smoke

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #104 · KV 启动内存观察

- **尝试**：启动内存组成和容量分项诊断，不作为性能成绩。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：启动或描述符诊断；输入 / 输出 / 并发 / 请求数：8 / 32 / 1 / 1。
- **结果**：独立本地审计实际exit0/pass
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T220122Z-kv-memory-capacity-smoke",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T22:01:24.032599+00:00",
  "profile_id": "kv_startup_memory_capacity",
  "phase": "startup_scalar_smoke_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "8",
  "output_len": "32",
  "concurrency": "1",
  "num_prompts": "1",
  "profiler": "false",
  "status": "complete_startup_memory_observed_no_historical_cause",
  "artifacts": "experiments/framework/20261021T220122Z-kv-memory-capacity-smoke",
  "conclusion": "独立本地审计实际exit0/pass；capacity212106416→418/原init完整append39fb/原innovation5bef字节保持，同observer6a/原a8de-e155/0ab0 builder-5bdb launcher/原bc51-SERVER/smoke-only/seed721201/VERIFY0；smoke原greedy请求8in32out/32tokenIDs/logprobs/length完整，非性能或accuracy；实际PID231998/profile_context_calls1/原worker int22447777996→PARENT真list同值/三hook restored true，全部内存原标量完整无新GPU采样；KV521936/CPU6/物理32768MiB，requested29205777612.8/weights5101233152/peak656424960/nonTorch1000341504/nonKV6757999616/graph0/available22447777996.8；双方此次内存分项同、未复现历史6块，不倒补原因或报gain；DBbeforeafter51919340三SHA89743b20/29d740d5/71ac1989实体复算同；post2026-10-21T22:03:14.114658+00:00/source全SHA无变/68MiB0双栈closed无GPU进程，测前及shutdown ERROR均空，forcekill WARN原样保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T220122Z-kv-memory-capacity-smoke](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke)
- 原命令：[launch-command.json](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke/launch-command.json)；[command.txt](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke/server.log)；[gpu.csv](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke/gpu.csv)；[exit-code](../../../experiments/framework/20261021T220122Z-kv-memory-capacity-smoke/exit-code)
- 相关说明：[2026-10-22-kv-capacity-full-phase](../../../analysis/2026-10-22-kv-capacity-full-phase.md)；[2026-10-22-kv-memory-startup-observer](../../../analysis/2026-10-22-kv-memory-startup-observer.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
