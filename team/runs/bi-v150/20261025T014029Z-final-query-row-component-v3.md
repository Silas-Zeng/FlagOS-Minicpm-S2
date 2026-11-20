<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T014029Z-final-query-row-component-v3

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #245 · 末层Query精确选行

- **尝试**：仅末层Attention选择需要输出的Query，完整M行K/V仍保留；组件核P映射、metadata、全slot字节及独立参考差异，不是模型准确率或端到端收益。
- **改动**：相关实现 [candidate.diff](../../../archive/candidates/20261025-final-rows/final-query-row-model-candidate/candidate.diff)；[state.json](../../../experiments/framework/20261025T005351Z-final-query-row-component/state.json)；[state.json](../../../experiments/framework/20261025T013820Z-final-query-row-component-v2/state.json)；[state.json](../../../experiments/framework/20261025T014029Z-final-query-row-component-v3/state.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 4独立shape×双臂，非模型请求。
- **结果**：selected-Q v3四shape双臂完整：S32/40/64、M2048及S5/M141；两臂均写完整M行K/V，全部slot逐字、guard、输出guard、P与请求顺序通过，真实GQA/Q路径有调用证据。输出均有限但非逐bit：maxabs依次0.001953125/0.001953125/0.00390625/0.015625；各例最长Query保存CPU FP32
- **是否保留**：原始证据和失败保留；是否进入模型/合并以本轮结论为准，不自动续测。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T014029Z-final-query-row-component-v3",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T01:40:29Z",
  "profile_id": "selected-query-row",
  "phase": "query_component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "4独立shape×双臂，非模型请求",
  "profiler": "false",
  "status": "query_component_completed_numerical_unassessed",
  "artifacts": "experiments/framework/20261025T014029Z-final-query-row-component-v3",
  "conclusion": "selected-Q v3四shape双臂完整：S32/40/64、M2048及S5/M141；两臂均写完整M行K/V，全部slot逐字、guard、输出guard、P与请求顺序通过，真实GQA/Q路径有调用证据。输出均有限但非逐bit：maxabs依次0.001953125/0.001953125/0.00390625/0.015625；各例最长Query保存CPU FP32参考，原路/候选误差相近。01:41:20 UTC源/native/DB与真实TP清理通过。只记录合成激活局部数值，不设随意阈值称准确率通过；冷wall不计性能。模型、完整105及端到端仍未验证，按用户要求封存、不续测。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T014029Z-final-query-row-component-v3](../../../experiments/framework/20261025T014029Z-final-query-row-component-v3)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T014029Z-final-query-row-component-v3/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T014029Z-final-query-row-component-v3/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T014029Z-final-query-row-component-v3/worker.log)；[gpu.csv](../../../experiments/framework/20261025T014029Z-final-query-row-component-v3/gpu.csv)；[exit-code](../../../experiments/framework/20261025T014029Z-final-query-row-component-v3/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
