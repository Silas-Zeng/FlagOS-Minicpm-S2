<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T061506Z-host-gap-control

平台：未记录。本页只摘录既有登记；未记录字段不补猜。

## 登记 #29 · 早期集成、块表与 profile

- **尝试**：早期基点、块表提交、集成短筛和profile，不自动作为诊断开关或top-p单项性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：只记录启动、日志或封存，不单独测性能。
- **结果**：启动或收集记录，实验结果见对应主run。
- **是否保留**：保留作过程记录。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T061506Z-host-gap-control",
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
  "artifacts": "experiments/profiles/20261021T061506Z-host-gap-control",
  "conclusion": "PID/log/launch command attachment for corresponding host profile; no independent device measurement"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T061506Z-host-gap-control](../../../experiments/profiles/20261021T061506Z-host-gap-control)
- 原命令：[command.txt](../../../experiments/profiles/20261021T061506Z-host-gap-control/command.txt)；[launch.sh](../../../experiments/profiles/20261021T061506Z-host-gap-control/launch.sh)
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
