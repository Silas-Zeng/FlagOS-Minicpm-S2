<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T033421188581Z-biv150-down-tiny-splitk-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #293 · BI-V150特定形状GEMM

- **尝试**：针对BI-V150 warp64/16SM与真实M/N/K降低净开销。
- **改动**：实际实现和精确固定tile见原source/candidate.py；未改官方参数或切换现成库，不承诺任意输入bitwise。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：真实down权重，原安装MM或当前PR51 small_o JIT对照；数值/FP64抽样/换值Graph后ABBA，完整输出和SplitK归约计入。
- **结果**：Event每GEMM毫秒 {"baseline": 0.07281111553311348, "split4": 0.05686087720096111, "split8": 0.05061881057918072}；wall {"baseline": 0.0744598359375, "split4": 0.057787476562499995, "split8": 0.05
- **是否保留**：保留局部信号，后继完整权重工作集结果另列，不把组件比例当整轮收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T033421188581Z-biv150-down-tiny-splitk-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T03:34:21.188581+00:00",
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
  "status": "shape_gemm_local_positive",
  "artifacts": "experiments/framework/20261026T033421188581Z-biv150-down-tiny-splitk-component",
  "conclusion": "Event每GEMM毫秒 {\"baseline\": 0.07281111553311348, \"split4\": 0.05686087720096111, \"split8\": 0.05061881057918072}；wall {\"baseline\": 0.0744598359375, \"split4\": 0.057787476562499995, \"split8\": 0.0515390859375}。10项数值/尾部/换值Graph及FP64抽样通过。保留组件正向候选，整模型吞吐/105尚未验证、不合并。 未改已安装FlagGems/模型/官方参数，DB207f未变，source及设备清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T033421188581Z-biv150-down-tiny-splitk-component](../../../experiments/framework/20261026T033421188581Z-biv150-down-tiny-splitk-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T033421188581Z-biv150-down-tiny-splitk-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T033421188581Z-biv150-down-tiny-splitk-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T033421188581Z-biv150-down-tiny-splitk-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T033421188581Z-biv150-down-tiny-splitk-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T033421188581Z-biv150-down-tiny-splitk-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
