<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T105526Z-mixed-bucket-row-kv-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #58 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：Localraw independently reviewed
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T105526Z-mixed-bucket-row-kv-gate",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T10:55:26.916723+00:00",
  "profile_id": "mixed-token-bucket-row-kv",
  "phase": "synthetic_correctness_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "infrastructure_failure_before_cases_independently_confirmed",
  "artifacts": "experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate",
  "conclusion": "Localraw independently reviewed;exit1 casesempty;all8recordedsourceSHA match;IsADirectoryError source__pycache__ duringarchive no candidate cases;finished10:55:41.544311UTC;retry changes only2sourcehash comprehensions toregularfile filter;not candidate correctness failure;raw/controlpreserved"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T105526Z-mixed-bucket-row-kv-gate](../../../experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate/postflight-full.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate/results.json)
- 日志 / 采样：[gate.log](../../../experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate/gate.log)；[exit-code](../../../experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate/exit-code)
- 相关说明：[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
