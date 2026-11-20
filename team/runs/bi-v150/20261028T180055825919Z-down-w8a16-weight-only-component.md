<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T180055825919Z-down-w8a16-weight-only-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #449 · BI-V150特定形状GEMM

- **尝试**：检查W8A16 down候选能否用当前生产compile/config接口编译。
- **改动**：编译调用接口异常，未取得可比较内核。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：本条所列source/result/manifest原件完整打包并按SHA256分块；组件/CPU筛查与官方成绩分开。
- **结果**：编译接口异常，未获得性能结果
- **是否保留**：保留接口失败原件；不判量化候选快慢。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T180055825919Z-down-w8a16-weight-only-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T18:00:55.825919+00:00",
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
  "status": "shape_gemm_w8a16_compile_interface_failed",
  "artifacts": "experiments/bundles/20261028T180055825919Z-down-w8a16-weight-only-component",
  "conclusion": "编译接口异常，未获得性能结果"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T180055825919Z-down-w8a16-weight-only-component](../../../experiments/bundles/20261028T180055825919Z-down-w8a16-weight-only-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T180055825919Z-down-w8a16-weight-only-component/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
