<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T182535Z-native-gqa-overlap-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #447 · BI-V150特定形状GEMM

- **尝试**：验证GROUP_M4官方selector首暖回执与编译身份门。
- **改动**：沿用官方路径；selector接口异常，未进入benchmark计时。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：本条所列source/result/manifest原件完整打包并按SHA256分块；组件/CPU筛查与官方成绩分开。
- **结果**：官方selector接口失败，未进入性能计时
- **是否保留**：保留失败证据；不当作候选性能失败。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T182535Z-native-gqa-overlap-4k-four-rounds",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T18:25:35+00:00",
  "profile_id": "shape-gemm",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "shape_gemm_groupm4_official_selector_failed",
  "artifacts": "experiments/bundles/20261028T182535Z-native-gqa-overlap-4k-four-rounds",
  "conclusion": "官方selector接口失败，未进入性能计时"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T182535Z-native-gqa-overlap-4k-four-rounds](../../../experiments/bundles/20261028T182535Z-native-gqa-overlap-4k-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T182535Z-native-gqa-overlap-4k-four-rounds/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
