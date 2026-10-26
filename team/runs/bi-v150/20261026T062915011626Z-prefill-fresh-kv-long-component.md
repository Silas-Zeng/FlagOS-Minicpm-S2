<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T062915011626Z-prefill-fresh-kv-long-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #314 · Prefill当前chunk直读K/V

- **尝试**：减少当前chunk从paged KV读取的地址成本。
- **改动**：按context_len逐lane选择历史cache或当前post-RoPE K/V，原writer保留。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-fresh-kv.md)。
- **怎么测**：Q2047/KV16384，原数值门、换值Graph与fresh来源反事实证明；已暖直接JIT完整2D输出ABBA。
- **结果**：历史KV读paged cache、当前chunk直读post-RoPE BF16 K/V，保留writer、绝对T64/K顺序与softmax。Q2047/KV16384初始/换值跨臂逐位、FP64/Graph通过；修改raw来源而cache不变时仅fresh臂变化，证明新来源实际使用。Event8.347201→10.860539ms慢30.1099%，wall慢30.987
- **是否保留**：停止，不叠LPT或接模型；causal未测。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T062915011626Z-prefill-fresh-kv-long-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T06:29:15.011626+00:00",
  "profile_id": "prefill-fresh-kv",
  "phase": "Prefill当前chunk直读K/V长上下文组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_fresh_kv_long_negative_component",
  "artifacts": "experiments/framework/20261026T062915011626Z-prefill-fresh-kv-long-component",
  "conclusion": "历史KV读paged cache、当前chunk直读post-RoPE BF16 K/V，保留writer、绝对T64/K顺序与softmax。Q2047/KV16384初始/换值跨臂逐位、FP64/Graph通过；修改raw来源而cache不变时仅fresh臂变化，证明新来源实际使用。Event8.347201→10.860539ms慢30.1099%，wall慢30.9874%；负结果停止，不叠LPT、不接模型。DB/source/native和清理通过；causal场景未测，不定新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T062915011626Z-prefill-fresh-kv-long-component](../../../experiments/framework/20261026T062915011626Z-prefill-fresh-kv-long-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T062915011626Z-prefill-fresh-kv-long-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T062915011626Z-prefill-fresh-kv-long-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T062915011626Z-prefill-fresh-kv-long-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T062915011626Z-prefill-fresh-kv-long-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T062915011626Z-prefill-fresh-kv-long-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
