<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T200759Z-native-gqa-overlap-16k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #458 · BI-V150特定形状GEMM

- **尝试**：检验G4直调C在原官方16K负载上的整体表现。
- **改动**：原服务与评测参数不变；对PR105同档首暖筛选，负结果提前停止。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原始文件按清单SHA核验并完整打包；性能组件、官方成绩与入口准备失败分开。
- **结果**：冷/首暖4361.39/4825.32 tok/s，256成功；相对PR105首暖−0.188853%，KV548384对548288不匹配。按首暖负门停止；未跑完整四轮/105，不合并、不更新基线。
- **是否保留**：停止C，不合并、不更新基线；不是完整四轮成绩，105条件包未运行。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T200759Z-native-gqa-overlap-16k-four-rounds",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T20:07:59+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_16k_first_warm_stop",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "",
  "status": "shape_gemm_direct_launch_official16k_first_warm_negative_stop",
  "artifacts": "experiments/bundles/20261028T200759Z-native-gqa-overlap-16k-four-rounds",
  "conclusion": "冷/首暖4361.39/4825.32 tok/s，256成功；相对PR105首暖−0.188853%，KV548384对548288不匹配。按首暖负门停止；未跑完整四轮/105，不合并、不更新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T200759Z-native-gqa-overlap-16k-four-rounds](../../../experiments/bundles/20261028T200759Z-native-gqa-overlap-16k-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T200759Z-native-gqa-overlap-16k-four-rounds/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T200759Z-native-gqa-overlap-16k-four-rounds/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
