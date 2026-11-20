<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T182129Z-biv150-down-groupm4-official-staging-failed

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #446 · BI-V150特定形状GEMM

- **尝试**：验证GROUP_M4官方4K候选能否通过冻结源暂存门。
- **改动**：沿用原官方owner，只记stage源映射异常；未启动benchmark。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：本条所列source/result/manifest原件完整打包并按SHA256分块；组件/CPU筛查与官方成绩分开。
- **结果**：官方源暂存接口失败，未运行benchmark
- **是否保留**：保留接口失败证据；不能归为性能或数值结果。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T182129Z-biv150-down-groupm4-official-staging-failed",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T18:21:29+00:00",
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
  "status": "shape_gemm_groupm4_official_staging_failed",
  "artifacts": "experiments/bundles/20261028T182129Z-biv150-down-groupm4-official-staging-failed",
  "conclusion": "官方源暂存接口失败，未运行benchmark"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T182129Z-biv150-down-groupm4-official-staging-failed](../../../experiments/bundles/20261028T182129Z-biv150-down-groupm4-official-staging-failed)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
