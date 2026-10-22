<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T072153Z-sql-reflection-screen

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #36 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：versus B0 071554 throughput factor 2.795773385 duration reduction 64.231722 percent
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T072153Z-sql-reflection-screen",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T07:21:53.484030+00:00",
  "profile_id": "sql_reflection",
  "phase": "decode-4k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "",
  "status": "large_short_screen_signal_repeat_supported",
  "artifacts": "experiments/framework/20261021T072153Z-sql-reflection-screen",
  "conclusion": "SQL repeat exit 0; 64 completed 0 failed; 262144 input/8192 output tokens; 43.090572 s and 6273.669276 total tok/s; median ITL 124.503668 ms; same source hashes/SERVER/load/seed/driver22a076e/packages/KV521840 as first SQL; versus B0 071554 throughput factor 2.795773385 duration reduction 64.231722 percent; candidate throughput +0.250827 percent versus first SQL; 5 CPU throttles and 12.427074 s cumulative throttled time; postflight 07:24:45 UTC 68 MiB 0 percent port closed; stronger repeated screen signal only; no official score or accuracy/stable causal claim; commit is manifest base plus hashed source"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T072153Z-sql-reflection-screen](../../../experiments/framework/20261021T072153Z-sql-reflection-screen)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T072153Z-sql-reflection-screen/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T072153Z-sql-reflection-screen/launch-command.json)；[command.txt](../../../experiments/framework/20261021T072153Z-sql-reflection-screen-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T072153Z-sql-reflection-screen-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T072153Z-sql-reflection-screen/manifest.json)；[postflight.json](../../../experiments/framework/20261021T072153Z-sql-reflection-screen/postflight.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261021-152350.json](../../../experiments/framework/20261021T072153Z-sql-reflection-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-152350.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T072153Z-sql-reflection-screen/server.log)；[gpu.csv](../../../experiments/framework/20261021T072153Z-sql-reflection-screen/gpu.csv)；[exit-code](../../../experiments/framework/20261021T072153Z-sql-reflection-screen/exit-code)
- 相关说明：[2026-10-21-next-framework-research](../../../analysis/2026-10-21-next-framework-research.md)；[2026-10-21-prefill-graph-feasibility](../../../analysis/2026-10-21-prefill-graph-feasibility.md)；[2026-10-21-memory-lifecycle-feasibility](../../../analysis/2026-10-21-memory-lifecycle-feasibility.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
