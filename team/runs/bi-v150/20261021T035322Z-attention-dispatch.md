<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T035322Z-attention-dispatch

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #11 · Attention 分流与 launch

- **尝试**：prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：bitwise equal
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T035322Z-attention-dispatch",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T03:53:22.210462+00:00",
  "profile_id": "direct_decode",
  "phase": "attention_dispatch",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "single_layer_small_candidate",
  "artifacts": "experiments/framework/20261021T035322Z-attention-dispatch",
  "conclusion": "5 direct cases bitwise equal; 4K about 1.3 percent single-layer latency signal; no E2E or accuracy claim; mixed exploratory rows retained"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T035322Z-attention-dispatch](../../../experiments/framework/20261021T035322Z-attention-dispatch)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T035322Z-attention-dispatch/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T035322Z-attention-dispatch/results.json)
- 日志 / 采样：[gpu.csv](../../../experiments/framework/20261021T035322Z-attention-dispatch/gpu.csv)；[exit-code](../../../experiments/framework/20261021T035322Z-attention-dispatch/exit-code)
- 相关说明：[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
