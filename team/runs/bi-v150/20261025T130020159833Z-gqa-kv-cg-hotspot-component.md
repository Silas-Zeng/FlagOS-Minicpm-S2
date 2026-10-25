<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T130020159833Z-gqa-kv-cg-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #266 · GQA KV读取缓存策略

- **尝试**：检查GQA K/V读取绕过L1是否减少长上下文访存开销。
- **改动**：实际生产GQA仅4处load增加.cg，reducer保持；N33/B40/S16。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-kv-cg.md)。
- **怎么测**：KV16K随机输入，实际GQA+reducer，8组数值/换值Graph边界（含原非有限行为保持）与16-call Graph ABBA；ASM有64处cg load。
- **结果**：N33/B40/S16：8组数值/Graph边界通过，Event1.277376→1.243314ms，省2.6666%；wall省2.7239%。
- **是否保留**：保留16K组件正信号；官方后继首暖负、当期原main两轮已记录，不将局部结果外推端到端。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T130020159833Z-gqa-kv-cg-hotspot-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T13:00:20.159833+00:00",
  "profile_id": "gqa-kv-cg",
  "phase": "独立算子组件对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_cg_hotspot_signal",
  "artifacts": "experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component",
  "conclusion": "实际GQA+reducer随机组件，N33/B40/S16、KV16K，唯一4处K/V load加.cg；8组数值/换值Graph边界通过（含原非有限行为保持），ASM有64处cg。Graph ABBA Event1.277376→1.243314ms，省2.6666%；wall1.283274→1.248319ms，省2.7239%。源码/native未变、DB恢复和清理通过。保留组件正信号；不是模型或官方吞吐收益，后继生产候选另测。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T130020159833Z-gqa-kv-cg-hotspot-component](../../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
