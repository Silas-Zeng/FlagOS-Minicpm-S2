<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #279 · GQA四页T64计算块

- **尝试**：让T64沿N维分摊到四warp，检查前轮未实现的布局机制。
- **改动**：实际mma改为[1,4]，页表/causal/reducer及原数值合同保持；SGPR spill仍68/shared32K，机制实现不等于净收益。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-four-page-t64.md)。
- **怎么测**：N33/B40/S16、KV16K/page16，固定真实N方向四warp布局与原GQA+reducer；8类原数值门及Graph ABBA，关闭profiler。
- **结果**：8类数值/Graph/FP64门通过，实际mma=[1,4]；Event1.278378→1.827178ms慢42.9294%，wall慢42.5630%。
- **是否保留**：整个四页T64路线收口，不再扫参、不进入4K或模型，不授官方/105资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T15:42:56.643502+00:00",
  "profile_id": "gqa-four-page-t64",
  "phase": "GQA四页T64真实N4布局组件对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_four_page_t64_n4_negative",
  "artifacts": "experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component",
  "conclusion": "在T64候选固定N方向四warp的实际mma=[1,4]，检验前轮未形成的分摊布局；N33/B40/S16、KV16K、原reducer保留。8类数值/Graph/FP64门通过。Graph ABBA Event1.278378→1.827178ms慢42.9294%，wall1.285526→1.832685ms慢42.5630%；候选SGPR99/spill68、VGPR88/shared32K，actual occupancy未证明。15:43:28 clean exit0、source/native未变、DB恢复，完整原件已封存。尽管布局机制实现，仍明显负，整个四页T64路线停止，不再扫参或进入4K/模型，不授官方或105资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component](../../../experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
