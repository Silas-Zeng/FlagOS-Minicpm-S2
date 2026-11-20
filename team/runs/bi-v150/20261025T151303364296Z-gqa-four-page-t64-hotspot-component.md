<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T151303364296Z-gqa-four-page-t64-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #276 · GQA四页T64计算块

- **尝试**：把四个物理页组成T64计算块，减少GQA循环与地址计算。
- **改动**：实际T16→T64改变归约分块，保留分页/causal/reducer语义；独立FP64抽样判数值，不能声称跨臂逐位。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-four-page-t64.md)。
- **怎么测**：N33/B40/S16、KV16K/page16，生产GQA与四页T64候选+原reducer；8类边界、变输入Graph及独立CPU FP64抽样，Graph ABBA。跨臂不要求逐位，引用原数值合同。
- **结果**：8类数值/Graph/FP64抽样门通过；Event1.276535→2.896506ms，慢126.9037%；SGPR spill0→138、shared8K→32K。
- **是否保留**：明确负结果收口，不测4K/模型、不扫参；保留原件及资源代价，不授模型或官方资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T151303364296Z-gqa-four-page-t64-hotspot-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T15:13:03.364296+00:00",
  "profile_id": "gqa-four-page-t64",
  "phase": "GQA四页T64组件对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_four_page_t64_negative",
  "artifacts": "experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component",
  "conclusion": "在生产GQA上将page16按四页组成T64计算块，尝试降低循环/地址开销；N33/B40/S16、KV16K随机组件，原reducer保留。8类数值/Graph/guard及独立FP64抽样门通过；跨臂不要求逐位，dense参考relativeL2为0.002217/0.002234，非模型准确率。Graph ABBA Event1.276535→2.896506ms慢126.9037%，wall1.283318→2.902030ms慢126.1350%。编译资源SGPR spill0→138、shared8192→32768、VGPR93→199，实际occupancy未测。15:13:37 exit0、源码/native未变、DB恢复及清理通过。明确负结果，停止，不测4K或模型、不扫参；完整包远端留存、小包原字节回收。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T151303364296Z-gqa-four-page-t64-hotspot-component](../../../experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
