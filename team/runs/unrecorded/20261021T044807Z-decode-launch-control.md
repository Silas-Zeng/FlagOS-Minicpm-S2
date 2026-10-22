<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T044807Z-decode-launch-control

平台：未记录。本页只摘录既有登记；未记录字段不补猜。

## 登记 #18 · Attention 分流与 launch

- **尝试**：prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：只记录启动、日志或封存，不单独测性能。
- **结果**：启动或收集记录，实验结果见对应主run。
- **是否保留**：保留作过程记录。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T044807Z-decode-launch-control",
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
  "artifacts": "experiments/framework/20261021T044807Z-decode-launch-control",
  "conclusion": "PID/log attachment for corresponding decode-launch run; no independent device measurement"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T044807Z-decode-launch-control](../../../experiments/framework/20261021T044807Z-decode-launch-control)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
