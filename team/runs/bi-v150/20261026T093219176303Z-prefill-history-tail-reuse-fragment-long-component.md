<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #323 · Prefill历史区间与causal尾块分离

- **尝试**：首run私有Q-hoist适配失败；v2实际消除loop Q读取及SGPR spill，但跨臂逐位门失败，未计时，停止该候选。FP64通过不覆盖数值不变要求。
- **改动**：相关实现 [source](../../../experiments/framework/20261026T090943131971Z-prefill-history-tail-long-component/source)；[source](../../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/source)；[results.json](../../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/results.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：Q2047/KV16384/ctx14337、相同原tile/顺序；只修私有Q复用，数值/FP64/Graph门未改。初始逐位门拒绝，后续Graph/性能未跑。
- **结果**：v2按真实IR复用已有Q fragment，selected1/fallback0、两臂LLVM循环Q读0。SGPR104→90/spill6→0；两臂FP64门通过，但跨臂逐位失败，max_abs0.0001220703125。违反本方法数值不变要求，未计时，停止当前候选。
- **是否保留**：停止当前候选，不放宽逐位门、不继续修优化或进模型；不能称主线错误/准确率下降，保留首次失败。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T09:32:19.176303+00:00",
  "profile_id": "prefill-history-tail",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "history_tail_bitwise_failed",
  "artifacts": "experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component",
  "conclusion": "v2按真实IR复用已有Q fragment，selected1/fallback0、两臂LLVM循环Q读0。SGPR104→90/spill6→0；两臂FP64门通过，但跨臂逐位失败，max_abs0.0001220703125。违反本方法数值不变要求，未计时，停止当前候选。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component](../../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
