<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T064944259294Z-biv150-qkv-rope-fusion-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #315 · QKV GEMM与RoPE融合

- **尝试**：减少QKV到RoPE的launch和中间访存。
- **改动**：新GEMM输出融合RoPE，不含KV writer。 版本、命令和源码见下方原件；[方法记录](../../methods/qkv-rope-fusion.md)。
- **怎么测**：layer0真实权重＋合成激活，M2030/2048共14项；两臂完整Graph ABBA，原RoPE heuristic重新编译。
- **结果**：layer0真实QKV GEMM＋原native RoPE combo对照新融合输出，M2030/2048共14项Q/K/V逐位、独立FP64、换值Graph及side stream通过，RNG不变。Graph Event均值分别0.384947→0.432756ms、0.385697→0.435131ms，慢12.4198%/12.8168%，负结果停止，不进官方。候选不含K
- **是否保留**：停止，不进官方；无生产adapter或新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T064944259294Z-biv150-qkv-rope-fusion-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T06:49:44.259294+00:00",
  "profile_id": "qkv-rope-fusion",
  "phase": "真实QKV GEMM与RoPE融合组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "qkv_rope_fusion_negative_component",
  "artifacts": "experiments/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component",
  "conclusion": "layer0真实QKV GEMM＋原native RoPE combo对照新融合输出，M2030/2048共14项Q/K/V逐位、独立FP64、换值Graph及side stream通过，RNG不变。Graph Event均值分别0.384947→0.432756ms、0.385697→0.435131ms，慢12.4198%/12.8168%，负结果停止，不进官方。候选不含KV writer，不是旧RoPE→KV融合；DB恢复、source不变及清理通过，official_qualified=false。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T064944259294Z-biv150-qkv-rope-fusion-component](../../../experiments/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
