<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T073309Z-sql-decode-screen

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #39 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：SQL+C2 only
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T073309Z-sql-decode-screen",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T07:33:10.554277+00:00",
  "profile_id": "sql_reflection+C2",
  "phase": "decode-4k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "",
  "status": "single_combination_short_screen",
  "artifacts": "experiments/framework/20261021T073309Z-sql-decode-screen",
  "conclusion": "SQL+C2 only; exit 0; 64 completed 0 failed; 262144 input/8192 output tokens; 41.15406773984432 s; total tok/s 6568.876780514884; median ITL 92.26066176779568 ms; same official SERVER/seed721101/load/driver22a076e; no profiler; both install markers and C2 first selected during graph capture; no service hit count; KV521936 versus SQL-only521840 prevents an attributed C2 increment claim; 630 CPU periods/4 throttles/18.773013462 s cumulative throttled time; DB before/after manifests show 479 tables 17982 rows and equal schema/logical/physical hashes; snapshot binaries retained remote and local with matching SHA256; Git ignores *.sqlite; postflight 07:35:58.660801 UTC 68 MiB 0 percent port closed; no official score or new accuracy claim; commit is manifest base plus source hashes"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T073309Z-sql-decode-screen](../../../experiments/framework/20261021T073309Z-sql-decode-screen)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T073309Z-sql-decode-screen/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T073309Z-sql-decode-screen/launch-command.json)；[command.txt](../../../experiments/framework/20261021T073309Z-sql-decode-screen-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T073309Z-sql-decode-screen-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T073309Z-sql-decode-screen/manifest.json)；[postflight.json](../../../experiments/framework/20261021T073309Z-sql-decode-screen/postflight.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261021-153505.json](../../../experiments/framework/20261021T073309Z-sql-decode-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-153505.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T073309Z-sql-decode-screen/server.log)；[gpu.csv](../../../experiments/framework/20261021T073309Z-sql-decode-screen/gpu.csv)；[exit-code](../../../experiments/framework/20261021T073309Z-sql-decode-screen/exit-code)
- 相关说明：[2026-10-21-next-framework-research](../../../analysis/2026-10-21-next-framework-research.md)；[2026-10-21-memory-lifecycle-feasibility](../../../analysis/2026-10-21-memory-lifecycle-feasibility.md)；[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
