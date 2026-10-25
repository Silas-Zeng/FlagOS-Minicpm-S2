<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T130735173560Z-head-major-paged-prefill-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #269 · Attention head-major分页读取

- **尝试**：用head-major大query tile和分页loader增加长prefill局部复用。
- **改动**：新增page16 loader并把N32改N64；原库臂未改，不能拆分loader/归约两变化的因果。 版本、命令和源码见下方原件；[方法记录](../../methods/attention-head-major.md)。
- **怎么测**：M2047/KV16K、Q16/KV2/D128/page16，真实原库对照；独立FP64抽样、KV writer/guard、同址换值Graph，当前锚定的两组ABBA。
- **结果**：三臂编译及数值/Graph通过；Event当前8.366/原FlagGems29.733/新loader82.944ms，候选明显负。
- **是否保留**：停止该方法，不再调参、不创建优化PR；完整三臂结果保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T130735173560Z-head-major-paged-prefill-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T13:07:35.173560+00:00",
  "profile_id": "attention-head-major",
  "phase": "独立算子组件对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "head_major_paged_prefill_negative",
  "artifacts": "experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component",
  "conclusion": "M2047/KV16K、Q16/KV2/D128/page16三臂：当前GQA、原FlagGems head-major、新page16 loader+N64。三臂均真实编译，独立FP64抽样、同址换值Graph/guard、KV writer与输入保持通过；Event当前8.366ms/原库29.733ms/候选82.944ms，候选明显负。N32→N64同时改变归约分块，非逐位保证，不能拆成loader单项因果。源码/native/DB恢复通过；停止，不继续调参或开优化PR。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T130735173560Z-head-major-paged-prefill-component](../../../experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
