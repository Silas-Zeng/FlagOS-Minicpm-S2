<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T005351Z-final-query-row-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #242 · 末层Query精确选行

- **尝试**：仅末层Attention选择需要输出的Query，完整M行K/V仍保留；组件核P映射、metadata、全slot字节及独立参考差异，不是模型准确率或端到端收益。
- **改动**：相关实现 [candidate.diff](../../../archive/candidates/20261025-final-rows/final-query-row-model-candidate/candidate.diff)；[state.json](../../../experiments/framework/20261025T005351Z-final-query-row-component/state.json)；[state.json](../../../experiments/framework/20261025T013820Z-final-query-row-component-v2/state.json)；[state.json](../../../experiments/framework/20261025T014029Z-final-query-row-component-v3/state.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 独立组件，未执行有效case。
- **结果**：selected-Q首次组件在原526 native安装链因TP组未初始化而失败，无有效case或双臂数值。00:54:11 UTC源码/native保持、DB恢复、设备清理通过。保留原失败；不将初始化问题算作算法数值负结果。
- **是否保留**：原始证据和失败保留；是否进入模型/合并以本轮结论为准，不自动续测。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T005351Z-final-query-row-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T00:53:51Z",
  "profile_id": "selected-query-row",
  "phase": "query_component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "独立组件，未执行有效case",
  "profiler": "false",
  "status": "query_component_tp_initialization_failed",
  "artifacts": "experiments/framework/20261025T005351Z-final-query-row-component",
  "conclusion": "selected-Q首次组件在原526 native安装链因TP组未初始化而失败，无有效case或双臂数值。00:54:11 UTC源码/native保持、DB恢复、设备清理通过。保留原失败；不将初始化问题算作算法数值负结果。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T005351Z-final-query-row-component](../../../experiments/framework/20261025T005351Z-final-query-row-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T005351Z-final-query-row-component/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T005351Z-final-query-row-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T005351Z-final-query-row-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T005351Z-final-query-row-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
