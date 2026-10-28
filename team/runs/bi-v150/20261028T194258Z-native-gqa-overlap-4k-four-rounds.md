<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T194258Z-native-gqa-overlap-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #456 · BI-V150特定形状GEMM

- **尝试**：检验direct C/GROUP_M4候选在原官方4K设置下的端到端表现。
- **改动**：沿用原官方benchmark与服务参数，仅声明的生产down wrapper候选；首暖有正信号后完成四轮。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原始文件按清单SHA核验并完整打包；性能组件、官方成绩与入口准备失败分开。
- **结果**：四轮完成，首暖/暖均对照PR105观察+0.1425%/+0.0714%；KV548432对548336不匹配，不宣称严格因果、稳定收益或更新基线。1024请求成功，source/native/DB恢复及selector/direct门通过。
- **是否保留**：仅保留小幅观察；不作严格因果/稳定收益，不更新基线、不合并；16K和准确率另判。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T194258Z-native-gqa-overlap-4k-four-rounds",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T19:42:58.557593+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_4k_four_rounds",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "",
  "status": "shape_gemm_direct_launch_official4k_small_positive_kv_mismatch",
  "artifacts": "experiments/bundles/20261028T194258Z-native-gqa-overlap-4k-four-rounds",
  "conclusion": "四轮完成，首暖/暖均对照PR105观察+0.1425%/+0.0714%；KV548432对548336不匹配，不宣称严格因果、稳定收益或更新基线。1024请求成功，source/native/DB恢复及selector/direct门通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T194258Z-native-gqa-overlap-4k-four-rounds](../../../experiments/bundles/20261028T194258Z-native-gqa-overlap-4k-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T194258Z-native-gqa-overlap-4k-four-rounds/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T194258Z-native-gqa-overlap-4k-four-rounds/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
