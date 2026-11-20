<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T075700478338Z-biv150-gate-partial-fusion-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #317 · gate partial融合

- **尝试**：将SiLU尾合入up输出以降低完整gate链开销。
- **改动**：A为生产merged linear＋原SiLU；B为gate写BF16 scratch＋up保留BF16 round并融合SiLU，均两个launch。 版本、命令和源码见下方原件；[方法记录](../../methods/gate-partial-fusion.md)。
- **怎么测**：真实layer0 gate/up权重＋合成BF16激活M2030，实际opaque/F.linear身份/config；完整output/gate逐位、FP64、换值Graph/side stream与ABBA。
- **结果**：真实opaque/F.linear默认FlagGems身份与config门通过；M2030共8项output/gate逐位、FP64、换值Graph和side stream通过，RNG不变。完整Graph原linear＋SiLU对partial融合Event1.305488646→1.499709368ms，慢14.8772%，停止M2048、8层工作集与模型。原linear 
- **是否保留**：停止M2048、工作集和模型；不合并、不定基线，保留负结果。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T075700478338Z-biv150-gate-partial-fusion-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T07:57:00.478338+00:00",
  "profile_id": "gate-partial-fusion",
  "phase": "gate partial融合真实opaque线性组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gate_partial_fusion_negative_component",
  "artifacts": "experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component",
  "conclusion": "真实opaque/F.linear默认FlagGems身份与config门通过；M2030共8项output/gate逐位、FP64、换值Graph和side stream通过，RNG不变。完整Graph原linear＋SiLU对partial融合Event1.305488646→1.499709368ms，慢14.8772%，停止M2048、8层工作集与模型。原linear shared64KiB/reg97，partial_up128KiB/reg169，无spill不保证快，未隔离资源与退化因果。两臂都两个launch；合成激活、单层，无生产adapter/官方资格。source/DB及清理通过，不改主线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T075700478338Z-biv150-gate-partial-fusion-component](../../../experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
