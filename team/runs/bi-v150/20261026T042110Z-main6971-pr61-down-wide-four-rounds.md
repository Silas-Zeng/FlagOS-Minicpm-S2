<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T042110Z-main6971-pr61-down-wide-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #298 · BI-V150特定形状GEMM

- **尝试**：针对BI-V150 warp64/16SM与真实M/N/K降低净开销。
- **改动**：实际实现和精确固定tile见原source/candidate.py；未改官方参数或切换现成库，不承诺任意输入bitwise。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：真实down权重，原安装MM或当前PR51 small_o JIT对照；数值/FP64抽样/换值Graph后ABBA，完整输出和SplitK归约计入。
- **结果**：down wide组件42层省24.12%，实际模型M2030/2048均选中，但4K冷4914.39、首暖5451.11 tok/s，对PR60对应5533.03观察−1.4806%。512 SUCCESS后按规则主动停止，第三轮中断；16K/105未跑，不是完整官方或正确性失败。source/native不变、DB207f恢复、GPU/9031清理通过；实际KV548432
- **是否保留**：首暖负按约定主动停止，保留已测轮次和运行条件；未测16K/105，不合并或定基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T042110Z-main6971-pr61-down-wide-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T04:21:10+00:00",
  "profile_id": "shape-gemm",
  "phase": "BI-V150 down宽tile原官方首暖筛选",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "e9b042b928c8246d22a907cdb51a3f196ac8eedd",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "shape_gemm_official_negative_screen",
  "artifacts": "experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds",
  "conclusion": "down wide组件42层省24.12%，实际模型M2030/2048均选中，但4K冷4914.39、首暖5451.11 tok/s，对PR60对应5533.03观察−1.4806%。512 SUCCESS后按规则主动停止，第三轮中断；16K/105未跑，不是完整官方或正确性失败。source/native不变、DB207f恢复、GPU/9031清理通过；实际KV548432对548336，非严格孤立因果。PR61已关闭未合并，不定新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T042110Z-main6971-pr61-down-wide-four-rounds](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_122327.csv](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds/benchmark_results/raw_runs_20261026_122327.csv)；[result.json](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261026T042110Z-main6971-pr61-down-wide-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
