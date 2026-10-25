<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T211402Z-final-ffn-row-prune-logger-v2

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #237 · 末层FFN/o_proj选行与模型对照

- **尝试**：真实权重和编译suffix，对比全M后选行与两gather后FFN。
- **改动**：本轮来源与原件见下方证据，限制见方法记录。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 四shape独立组件；非模型请求。
- **结果**：四shape逐bit/变输入Graph通过；M2048→S32/64 Graph总wall约2.386→0.170/2.397→0.183ms，仅组件，不含dense回填。
- **是否保留**：保留局部正信号供模型接线，实际模型准确率/端到端收益待。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T211402Z-final-ffn-row-prune-logger-v2",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T21:14:02Z",
  "profile_id": "final-ffn-row-prune",
  "phase": "final_ffn_component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "四shape独立组件；非模型请求",
  "profiler": "false",
  "status": "final_ffn_component_positive_signal",
  "artifacts": "experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2",
  "conclusion": "末层FFN选行logger-v2完成四shape：2048→32/64与32/64 identity均逐bit一致，变输入/残差/indices Graph与fresh一致；真实权重、原编译suffix和实际FlagGems dispatch。Graph总wall中位2048→32为2.385658→0.169884ms、2048→64为2.397497→0.182909ms，包含两gather，仅局部组件、不含后继模型dense fill/scatter及第二编译入口成本。21:14:39 UTC清理/source与DB恢复通过。保留局部正信号供独立模型接线，不替代模型准确率/吞吐。首次日志失败不改判。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T211402Z-final-ffn-row-prune-logger-v2](../../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/worker.log)；[gpu.csv](../../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/gpu.csv)；[exit-code](../../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
