<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T162319726359Z-native-q32-direct-q-grouped-incremental-pure2048-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #443 · CoreX原生Prefill Attention：Q32／Q64

- **尝试**：检查grouped pure2048与qualified direct-Q组件组合。
- **改动**：A/B完整ABBA，Event为原筛选门；不把wall单项改作通过依据。 版本、命令和源码见下方原件；[方法记录](../../methods/native-q32-transfer.md)。
- **怎么测**：pure2048完整ABBA与18项硬门；依原Event筛选门停止，保留原始性能状态及flag。
- **结果**：18项硬门通过；Event A/B .519592/.550852ms，慢6.016321%，按Event门停止。wall省8.498318%，B重复值波动大。
- **是否保留**：保留raw原值并停止组件；wall不称稳定收益/退化，raw numerical_component_passed=false保留，系性能early return未赋值，18项数值/状态门全过。无模型/官方资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T162319726359Z-native-q32-direct-q-grouped-incremental-pure2048-component",
  "local_date": "2026-10-28",
  "utc_start": "20261028T162319726359Z",
  "profile_id": "directq-grouped-incremental-pure2048",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_q32_direct_q_grouped_component_stopped_event_negative",
  "artifacts": "experiments/framework/20261028T162319726359Z-native-q32-direct-q-grouped-incremental-pure2048-component",
  "conclusion": "direct-Q＋grouped pure2048组件完整ABBA，18项硬门通过；Event A/B均值.519592/.550852ms（慢6.016321%），按事前Event门停止。wall省8.498318%但B两次.605957/.495748ms波动大，不称稳定退化或收益。原raw顶层numerical_component_passed=false因性能early return早于赋true，保留原值；18项数值/状态门全过，非数值失败。无模型/官方资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T162319726359Z-native-q32-direct-q-grouped-incremental-pure2048-component](../../../experiments/framework/20261028T162319726359Z-native-q32-direct-q-grouped-incremental-pure2048-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
