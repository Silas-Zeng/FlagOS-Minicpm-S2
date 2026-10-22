<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T073644Z-sql-decode-level3

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #41 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：准确率门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 8 / 105。
- **结果**：Exit 0
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T073644Z-sql-decode-level3",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T07:36:44.831755+00:00",
  "profile_id": "sql_reflection+C2",
  "phase": "accuracy_level3",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "8",
  "num_prompts": "105",
  "profiler": "",
  "status": "accuracy_gate_pass",
  "artifacts": "experiments/accuracy/20261021T073644Z-sql-decode-level3",
  "conclusion": "Exit 0; independent read-only CLI valid/pass 101 of105; exact accuracy0.9619047619047619 reported0.9619 above0.95; 105 succeeded0error; 105 unique official Level3 question IDs and prediction/review mapping valid; 104 stop1max_tokens at index101; empty final/extracted0; original config/score/result unchanged; source227 archived files match manifest SHA256; same SQL+C2 runner/runtime hashes as073309 and original SERVER; EvalScope1.11.1/SQLAlchemy2.0.48; KV521936; SQL/C2 install plus capture FIRST_SELECTED present; DB before/after479 tables17982 rows with equal schema/logical/snapshot hashes and local binaries verified; cleanup errors none; postflight-full08:06:29.426225 UTC68MiB0percent portclosed no processes; not a performance score or accuracy result for mixed/fused; commit is manifest base plus file hashes"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T073644Z-sql-decode-level3](../../../experiments/accuracy/20261021T073644Z-sql-decode-level3)
- 原命令：[command.txt](../../../experiments/accuracy/20261021T073644Z-sql-decode-level3-control/command.txt)；[launch.sh](../../../experiments/accuracy/20261021T073644Z-sql-decode-level3-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/accuracy/20261021T073644Z-sql-decode-level3/manifest.json)；[postflight-full.json](../../../experiments/accuracy/20261021T073644Z-sql-decode-level3/postflight-full.json)
- 原始结果：[result.json](../../../experiments/accuracy/20261021T073644Z-sql-decode-level3/result.json)
- 日志 / 采样：[server.log](../../../experiments/accuracy/20261021T073644Z-sql-decode-level3/server.log)；[gpu.csv](../../../experiments/accuracy/20261021T073644Z-sql-decode-level3/gpu.csv)；[exit-code](../../../experiments/accuracy/20261021T073644Z-sql-decode-level3/exit-code)
- 相关说明：[2026-10-21-next-framework-research](../../../analysis/2026-10-21-next-framework-research.md)；[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
