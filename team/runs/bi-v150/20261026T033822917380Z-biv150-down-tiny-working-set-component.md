<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T033822917380Z-biv150-down-tiny-working-set-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #294 · BI-V150特定形状GEMM

- **尝试**：针对BI-V150 warp64/16SM与真实M/N/K降低净开销。
- **改动**：实际实现和精确固定tile见原source/candidate.py；未改官方参数或切换现成库，不承诺任意输入bitwise。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：真实down权重，原安装MM或当前PR51 small_o JIT对照；数值/FP64抽样/换值Graph后ABBA，完整输出和SplitK归约计入。
- **结果**：42层真实权重1056964608B轮换，M1/2（计时M2）；Event整环3.057749748→2.088809967ms（省31.6880%），wall3.062777281→2.093116094ms。84项数值通过，Graph换值/side stream/RNG通过；原基线对候选全输出误差保留，不承诺所有输入bitwise。保留组件正向候选，整模型吞吐/105尚未验
- **是否保留**：保留候选；优先推进热点M2048 wide，M1-8 SplitK另列；需要实际接入、整模型性能/105和新增代码独立复核。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T033822917380Z-biv150-down-tiny-working-set-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T03:38:22.917380+00:00",
  "profile_id": "shape-gemm",
  "phase": "BI-V150 down GEMM特定形状组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "shape_gemm_working_set_positive",
  "artifacts": "experiments/framework/20261026T033822917380Z-biv150-down-tiny-working-set-component",
  "conclusion": "42层真实权重1056964608B轮换，M1/2（计时M2）；Event整环3.057749748→2.088809967ms（省31.6880%），wall3.062777281→2.093116094ms。84项数值通过，Graph换值/side stream/RNG通过；原基线对候选全输出误差保留，不承诺所有输入bitwise。保留组件正向候选，整模型吞吐/105尚未验证、不合并。 未改已安装FlagGems/模型/官方参数，DB207f未变，source及设备清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T033822917380Z-biv150-down-tiny-working-set-component](../../../experiments/framework/20261026T033822917380Z-biv150-down-tiny-working-set-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T033822917380Z-biv150-down-tiny-working-set-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T033822917380Z-biv150-down-tiny-working-set-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T033822917380Z-biv150-down-tiny-working-set-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T033822917380Z-biv150-down-tiny-working-set-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T033822917380Z-biv150-down-tiny-working-set-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
