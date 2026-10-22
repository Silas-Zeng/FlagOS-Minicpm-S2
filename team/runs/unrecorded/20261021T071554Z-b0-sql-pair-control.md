<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T071554Z-b0-sql-pair-control

平台：未记录。本页只摘录既有登记；未记录字段不补猜。

## 登记 #35 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：只记录启动、日志或封存，不单独测性能。
- **结果**：启动或收集记录，实验结果见对应主run。
- **是否保留**：保留作过程记录。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T071554Z-b0-sql-pair-control",
  "local_date": "",
  "utc_start": "",
  "profile_id": "launcher_only",
  "phase": "launcher_log",
  "device": "",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "control_log_only",
  "artifacts": "experiments/framework/20261021T071554Z-b0-sql-pair-control",
  "conclusion": "PID/log attachment for corresponding SQL-pair service run; no independent device measurement"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T071554Z-b0-sql-pair-control](../../../experiments/framework/20261021T071554Z-b0-sql-pair-control)
- 原命令：[command.txt](../../../experiments/framework/20261021T071554Z-b0-sql-pair-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T071554Z-b0-sql-pair-control/launch.sh)
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
