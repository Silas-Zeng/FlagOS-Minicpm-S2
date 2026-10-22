<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T173003Z-c3-coverage-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #74 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：EngineCore191286八周期快照与原log逐项匹配，末384calls/305metadata/250mixed/3000single-query-decode request-step/2241prefix及plan/759outside=25.3%，77unsupported单列，obs与execute错误0
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T173003Z-c3-coverage-context16k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T17:30:04.991591+00:00",
  "profile_id": "sql_reflection+C3_coverage",
  "phase": "coverage_diagnostic_context16k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_diagnostic_independent_review_pass_partial_coverage",
  "artifacts": "experiments/framework/20261021T173003Z-c3-coverage-context16k",
  "conclusion": "独立CPU验收：原SERVER/bc51/seed721201/16K128输出32req c64；32成功0失败/524288in4096out/120.483993092s，仅计数诊断非性能；plugin完整411SHA及e155 exact append/a39a与coverage29137核实，KV521936；DB before=after516表19270行，physical1593/schemaa0a590/logical90e9实体复算；preempt0到0/CPU6；EngineCore191286八周期快照与原log逐项匹配，末384calls/305metadata/250mixed/3000single-query-decode request-step/2241prefix及plan/759outside=25.3%，77unsupported单列，obs与execute错误0；非全程非forward执行非独立请求计数；manifest启动前Attentionbab2到post54c为retained启动写回，原版已单独封存；exit0/fullpost17:38:31.137125Z68MiB0双栈闭无GPU进程，runnerZ parent1/serverengine退出；不推accuracy或gain"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T173003Z-c3-coverage-context16k](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261022-013321.json](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261022-013321.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T173003Z-c3-coverage-context16k/exit-code)
- 相关说明：[2026-10-22-c3-coverage-and-metadata](../../../analysis/2026-10-22-c3-coverage-and-metadata.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
