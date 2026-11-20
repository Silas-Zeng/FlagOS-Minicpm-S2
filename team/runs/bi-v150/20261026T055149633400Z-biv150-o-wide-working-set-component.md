<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T055149633400Z-biv150-o-wide-working-set-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #307 · BI-V150特定形状GEMM

- **尝试**：针对BI-V150 warp64/16SM与真实M/N/K降低净开销。
- **改动**：实际实现和精确固定tile见原source/candidate.py；未改官方参数或切换现成库，不承诺任意输入bitwise。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：真实down权重，原安装MM或当前PR51 small_o JIT对照；数值/FP64抽样/换值Graph后ABBA，完整输出和SplitK归约计入。
- **结果**：O M2030/2048,N2048,K2048，原256/128/32/w8/s2对256/256/32/w16/s2。42真实O权重352321536B轮换，84数值/FP64抽样、换值Graph/side stream/RNG通过；Event 10.210501671→8.134766102ms，省20.3294%，wall同向。只保留组件正向，独立模型官方已启动，不继承
- **是否保留**：保留候选；优先推进热点M2048 wide，M1-8 SplitK另列；需要实际接入、整模型性能/105和新增代码独立复核。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T055149633400Z-biv150-o-wide-working-set-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T05:51:49.633400+00:00",
  "profile_id": "shape-gemm",
  "phase": "BI-V150 O宽tile42层工作集",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "shape_gemm_working_set_positive",
  "artifacts": "experiments/framework/20261026T055149633400Z-biv150-o-wide-working-set-component",
  "conclusion": "O M2030/2048,N2048,K2048，原256/128/32/w8/s2对256/256/32/w16/s2。42真实O权重352321536B轮换，84数值/FP64抽样、换值Graph/side stream/RNG通过；Event 10.210501671→8.134766102ms，省20.3294%，wall同向。只保留组件正向，独立模型官方已启动，不继承准确率、不称整轮收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T055149633400Z-biv150-o-wide-working-set-component](../../../experiments/framework/20261026T055149633400Z-biv150-o-wide-working-set-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T055149633400Z-biv150-o-wide-working-set-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T055149633400Z-biv150-o-wide-working-set-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T055149633400Z-biv150-o-wide-working-set-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T055149633400Z-biv150-o-wide-working-set-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T055149633400Z-biv150-o-wide-working-set-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
