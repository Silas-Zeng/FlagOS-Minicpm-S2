<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T061252978123Z-prefill-lpt-bitwise-causal-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #309 · Prefill序列内CTA调序

- **尝试**：核对causal CTA调序的原生产等价性及提交开销。
- **改动**：仅反转CTA枚举，单query数学和K顺序不变。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-lpt.md)。
- **怎么测**：Q2048/KV2048，原writer、换值Graph及直接JIT ABBA；FP64原阈值保留为诊断。
- **结果**：Q2048/KV2048仅CTA reversal，初始/换值跨臂逐位及自臂换值Graph通过。直接JIT ABBA Event0.660719→0.582717ms省11.8056%，wall0.783708→0.805652ms慢2.8000%，不以此认定Graph或整模收益。旧long-only FP64门两臂同为false，初始max_abs0.00352174、换值0
- **是否保留**：保留逐位依据；直接JIT不代替完整Graph或整模，FP64诊断false不改判。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T061252978123Z-prefill-lpt-bitwise-causal-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T06:12:52.978123+00:00",
  "profile_id": "prefill-lpt",
  "phase": "LPT纯causal逐位对照与直接JIT组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_lpt_causal_bitwise_component",
  "artifacts": "experiments/framework/20261026T061252978123Z-prefill-lpt-bitwise-causal-component",
  "conclusion": "Q2048/KV2048仅CTA reversal，初始/换值跨臂逐位及自臂换值Graph通过。直接JIT ABBA Event0.660719→0.582717ms省11.8056%，wall0.783708→0.805652ms慢2.8000%，不以此认定Graph或整模收益。旧long-only FP64门两臂同为false，初始max_abs0.00352174、换值0.00287200，阈值不改；不是候选特有新误差，亦不能写硬门通过。DB/source/native和清理通过；完整Graph另run。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T061252978123Z-prefill-lpt-bitwise-causal-component](../../../experiments/framework/20261026T061252978123Z-prefill-lpt-bitwise-causal-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T061252978123Z-prefill-lpt-bitwise-causal-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T061252978123Z-prefill-lpt-bitwise-causal-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T061252978123Z-prefill-lpt-bitwise-causal-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T061252978123Z-prefill-lpt-bitwise-causal-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T061252978123Z-prefill-lpt-bitwise-causal-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
