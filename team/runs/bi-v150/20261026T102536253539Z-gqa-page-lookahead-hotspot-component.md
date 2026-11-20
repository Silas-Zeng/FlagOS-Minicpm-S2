<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T102536253539Z-gqa-page-lookahead-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #326 · GQA下一页号预取

- **尝试**：原page16 while仅提前读取下一i32页号，N64/S2观测长度多重集、合成激活；原8类FP64/特殊值/Graph等门与跨臂逐位全部通过。完整producer＋原reducer Event0.542211056→0.542784363ms（慢0.105735%），wall快0.06134%，无可分辨正信号，停止不进模型。ASM下一页load后立即wait，未实现预期计算重叠；SGPR64→68、两臂spill0，源码/DB/native及清理通过。
- **改动**：相关实现 [results.json](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/results.json)；[worker.py](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/archive-receipt.json)；[candidate.py](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/source/candidate.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：固定N64/S2/page16原while及4D KV，同4K观测长度多重集与合成Q/KV；原reducer、FP64/换值Graph/特殊值及完整Graph ABBA。
- **结果**：8类数值门与逐位通过；完整组件Event慢0.1057%、wall快0.0613%，无可分辨正信号，停止。
- **是否保留**：保留数值通过但无净收益的负结果，停止，不扫参、不进模型；不将微小Event/wall反向差异写成稳定因果退化。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T102536253539Z-gqa-page-lookahead-hotspot-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T10:25:36.253539+00:00",
  "profile_id": "gqa-page-lookahead",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_page_lookahead_no_positive_signal",
  "artifacts": "experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component",
  "conclusion": "原page16 while仅提前读取下一i32页号，N64/S2观测长度多重集、合成激活；原8类FP64/特殊值/Graph等门与跨臂逐位全部通过。完整producer＋原reducer Event0.542211056→0.542784363ms（慢0.105735%），wall快0.06134%，无可分辨正信号，停止不进模型。ASM下一页load后立即wait，未实现预期计算重叠；SGPR64→68、两臂spill0，源码/DB/native及清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T102536253539Z-gqa-page-lookahead-hotspot-component](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
