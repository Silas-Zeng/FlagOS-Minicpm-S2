<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T202750315445Z-biv150-down-g8-sdk-vs-samekernel-direct-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #459 · BI-V150特定形状GEMM

- **尝试**：比较原SDK GROUP_M8与其同一CompiledKernel的直接调用。
- **改动**：保留原GPU核及数学，只减少LibEntry处理；42层真实权重、两pattern各一次ABBA。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原始文件按清单SHA核验并完整打包；性能组件、官方成绩与入口准备失败分开。
- **结果**：D对A两pattern wall省7.755105%/6.109667%，GPU Event近似；84输出、FP64、D变值Graph对fresh A、side 0/41、输入/RNG通过。A Graph快照被后续eager覆盖，不授A新增Graph资格；无全数组保存，仅记录冻结worker门。组件观察，不是官方或整模收益。
- **是否保留**：保留D进入生产对照；不称官方收益，A Graph快照已被eager覆盖，未保存全输出数组。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T202750315445Z-biv150-down-g8-sdk-vs-samekernel-direct-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T20:27:50.315445+00:00",
  "profile_id": "shape-gemm",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "shape_gemm_direct_launch_samekernel_component_positive",
  "artifacts": "experiments/bundles/20261028T202750315445Z-biv150-down-g8-sdk-vs-samekernel-direct-component",
  "conclusion": "D对A两pattern wall省7.755105%/6.109667%，GPU Event近似；84输出、FP64、D变值Graph对fresh A、side 0/41、输入/RNG通过。A Graph快照被后续eager覆盖，不授A新增Graph资格；无全数组保存，仅记录冻结worker门。组件观察，不是官方或整模收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T202750315445Z-biv150-down-g8-sdk-vs-samekernel-direct-component](../../../experiments/bundles/20261028T202750315445Z-biv150-down-g8-sdk-vs-samekernel-direct-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T202750315445Z-biv150-down-g8-sdk-vs-samekernel-direct-component/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T202750315445Z-biv150-down-g8-sdk-vs-samekernel-direct-component/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
