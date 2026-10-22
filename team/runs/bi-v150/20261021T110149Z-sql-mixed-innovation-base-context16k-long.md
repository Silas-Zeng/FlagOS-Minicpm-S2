<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T110149Z-sql-mixed-innovation-base-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #60 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：Exit0/32completed0failed524288in32768out
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T110149Z-sql-mixed-innovation-base-context16k-long",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T11:01:50.271474+00:00",
  "profile_id": "sql_reflection+C3",
  "phase": "innovation_matched_context16k_long_base",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "matched_short_control_complete_independent_review",
  "artifacts": "experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long",
  "conclusion": "Exit0/32completed0failed524288in32768out;220.49432305898517s2526.3961097582546total tok/s;21declaredsourceSHA matched controlplugin/actualdependency snapshots;driverbc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9;seed721201;KV521840;DBbeforeafter501tables18789rowsall3hashes equalofficialaftere90b;metrics before0after1preemption;fullpost11:07:46.868216UTC68MiB0percentclosed;original080656source;no official score"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T110149Z-sql-mixed-innovation-base-context16k-long](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long-control/postflight-full.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261021-190647.json](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261021-190647.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long/exit-code)
- 相关说明：[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
