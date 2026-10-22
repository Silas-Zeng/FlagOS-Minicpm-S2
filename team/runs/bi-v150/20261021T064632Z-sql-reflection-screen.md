<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T064632Z-sql-reflection-screen

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #32 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：SQL/B0 single-pair throughput factor 2.788778380 and duration reduction 64.142005 percent；persistent tuning DB initial contents not snapshotted；no stable/official performance or new accuracy claim；其余限制见完整原登记
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T064632Z-sql-reflection-screen",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T06:46:32.465586+00:00",
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
  "artifacts": "experiments/framework/20261021T064632Z-sql-reflection-screen",
  "conclusion": "SQL only runtime ad84c9a; no C2/C3/fused; duration 43.198655 s and total tok/s 6257.972600; 64 completed; 0 failed; 262144 input/8192 output tokens; exit 0; same SERVER/load/seed721101/driver22a076e7/packages/10 common source hashes/KV521840; SQLAlchemy 2.0.48; no profiler; SQL/B0 single-pair throughput factor 2.788778380 and duration reduction 64.142005 percent; persistent tuning DB initial contents not snapshotted; no stable/official performance or new accuracy claim; postflight 07:15:47 UTC 68 MiB 0 percent port closed; commit is manifest base plus hashed source; second SQL run 072153 is close but B0 only one matched run; no stable causal claim"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T064632Z-sql-reflection-screen](../../../experiments/framework/20261021T064632Z-sql-reflection-screen)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T064632Z-sql-reflection-screen/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T064632Z-sql-reflection-screen/launch-command.json)；[command.txt](../../../experiments/framework/20261021T064632Z-sql-reflection-screen-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T064632Z-sql-reflection-screen-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T064632Z-sql-reflection-screen/manifest.json)；[postflight.json](../../../experiments/framework/20261021T064632Z-sql-reflection-screen/postflight.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261021-144829.json](../../../experiments/framework/20261021T064632Z-sql-reflection-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-144829.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T064632Z-sql-reflection-screen/server.log)；[gpu.csv](../../../experiments/framework/20261021T064632Z-sql-reflection-screen/gpu.csv)；[exit-code](../../../experiments/framework/20261021T064632Z-sql-reflection-screen/exit-code)
- 相关说明：[2026-10-21-next-framework-research](../../../analysis/2026-10-21-next-framework-research.md)；[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
