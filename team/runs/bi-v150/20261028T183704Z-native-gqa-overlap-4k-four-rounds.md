<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T183704Z-native-gqa-overlap-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #452 · BI-V150特定形状GEMM

- **尝试**：验证GROUP_M4生产接线的官方4K吞吐净影响。
- **改动**：G4为已测自研JIT CTA分组映射；源、两库及DB均恢复，selector/config有效。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：本条所列source/result/manifest原件完整打包并按SHA256分块；组件/CPU筛查与官方成绩分开。
- **结果**：512 SUCCESS；候选冷/暖两轮5316.89/6387.44 tok/s，基线首暖6441.35，候选首暖低0.836936%；KV548336/548432不匹配，非因果。首暖负后按预设停止，未完成四轮、16K或105，不合并/不更新基线；DB、源码及两库恢复全true。
- **是否保留**：首暖负后按预设停止；不完整四轮/16K/105，不合并或更新基线；保留非因果限制。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T183704Z-native-gqa-overlap-4k-four-rounds",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T18:37:04+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_4k_first_warm_screen",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "shape_gemm_groupm4_official_first_warm_negative_stop",
  "artifacts": "experiments/bundles/20261028T183704Z-native-gqa-overlap-4k-four-rounds",
  "conclusion": "512 SUCCESS；候选冷/暖两轮5316.89/6387.44 tok/s，基线首暖6441.35，候选首暖低0.836936%；KV548336/548432不匹配，非因果。首暖负后按预设停止，未完成四轮、16K或105，不合并/不更新基线；DB、源码及两库恢复全true。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T183704Z-native-gqa-overlap-4k-four-rounds](../../../experiments/bundles/20261028T183704Z-native-gqa-overlap-4k-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T183704Z-native-gqa-overlap-4k-four-rounds/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
