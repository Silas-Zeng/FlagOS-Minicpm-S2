<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T062007042651Z-prefill-lpt-graph-causal-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #310 · Prefill序列内CTA调序

- **尝试**：隔离Python JIT提交后核完整Graph实际收益。
- **改动**：与逐位组件同CTA调序，完整Attention Graph回放。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-lpt.md)。
- **怎么测**：Q2048/KV2048完整Graph replay ABBA，跨臂逐位；原FP64门两臂false，阈值未变。
- **结果**：Q2048/KV2048完整Attention Graph replay ABBA Event0.663944→0.582823ms省12.2180%，wall0.667164→0.585344ms省12.2639%；初始/换值跨臂及自臂Graph逐位。旧long-only FP64 max_abs门仍两臂false且误差相同，阈值未改，仅保留诊断，不写硬门通过。保留早期chu
- **是否保留**：保留早期chunk候选；无官方/105新资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T062007042651Z-prefill-lpt-graph-causal-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T06:20:07.042651+00:00",
  "profile_id": "prefill-lpt",
  "phase": "LPT纯causal完整Graph replay组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_lpt_causal_graph_positive_component",
  "artifacts": "experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component",
  "conclusion": "Q2048/KV2048完整Attention Graph replay ABBA Event0.663944→0.582823ms省12.2180%，wall0.667164→0.585344ms省12.2639%；初始/换值跨臂及自臂Graph逐位。旧long-only FP64 max_abs门仍两臂false且误差相同，阈值未改，仅保留诊断，不写硬门通过。保留早期chunk组件候选；DB/source/native和清理通过，尚无官方收益或新准确率基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T062007042651Z-prefill-lpt-graph-causal-component](../../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
