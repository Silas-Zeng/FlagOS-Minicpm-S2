<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T080656Z-sql-mixed-screen

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #43 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：SQL+C2+mixed original implementation
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T080656Z-sql-mixed-screen",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T08:06:57.145584+00:00",
  "profile_id": "sql_reflection+C3",
  "phase": "decode-4k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "",
  "status": "single_combination_signal_later_accuracy_pass",
  "artifacts": "experiments/framework/20261021T080656Z-sql-mixed-screen",
  "conclusion": "SQL+C2+mixed original implementation; exit0; 64 completed0failed; input/output262144/8192; duration39.16018311912194s total6903.338505278714tok/s medianITL94.86219752579927ms; same official SERVER/packages/load/seed721101/driver22a076e/KV521936 as073309 SQL+C2; single-pair throughput+5.091612percent duration-4.844927percent but medianITL worsens; no repeated/official performance claim; no mixed accuracy result and prior101/105 applies only SQL+C2; all3 install markers but no service mixed-hit count; CPU615periods4throttles16.487770594s cumulative throttled time; DB479tables17982rows and schema/logical/snapshot hashes same before/after and as073309 with local entities verified; postflight08:10:57.096925UTC68MiB0percent portclosed no processes; commit is manifest base plus source hashes;later same080656 SQL+C3 source independently passes090505 accuracy103/105;this row remains a short performance screen"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T080656Z-sql-mixed-screen](../../../experiments/framework/20261021T080656Z-sql-mixed-screen)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T080656Z-sql-mixed-screen/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T080656Z-sql-mixed-screen/launch-command.json)；[command.txt](../../../experiments/framework/20261021T080656Z-sql-mixed-screen-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T080656Z-sql-mixed-screen-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T080656Z-sql-mixed-screen/manifest.json)；[postflight.json](../../../experiments/framework/20261021T080656Z-sql-mixed-screen/postflight.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261021-160853.json](../../../experiments/framework/20261021T080656Z-sql-mixed-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-160853.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T080656Z-sql-mixed-screen/server.log)；[gpu.csv](../../../experiments/framework/20261021T080656Z-sql-mixed-screen/gpu.csv)；[exit-code](../../../experiments/framework/20261021T080656Z-sql-mixed-screen/exit-code)
- 相关说明：[2026-10-21-sql-mixed-full-package](../../../analysis/2026-10-21-sql-mixed-full-package.md)；[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
