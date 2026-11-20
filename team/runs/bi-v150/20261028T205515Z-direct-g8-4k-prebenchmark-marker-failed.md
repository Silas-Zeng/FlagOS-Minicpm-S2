<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T205515Z-direct-g8-4k-prebenchmark-marker-failed

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #460 · BI-V150特定形状GEMM

- **尝试**：验证Direct-G8官方4K入口能否在服务启动后完成首请求前资格检查。
- **改动**：冷路径尚未触发真实GEMM，driver因预期direct marker缺失而停止；benchmark未开始。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原始成员、清单与压缩分块按SHA256核验；入口资格失败与完整官方负结果分开。
- **结果**：服务已启动，benchmark请求前因Direct-G8 marker缺失退出；0轮benchmark。保留原exit1和完整清理证据，不判数值或性能失败。
- **是否保留**：保留入口时序失败原件；不归类为kernel正确性或性能负结果。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T205515Z-direct-g8-4k-prebenchmark-marker-failed",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T20:55:14+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_4k_prebenchmark_failed",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "",
  "status": "shape_gemm_direct_g8_official_prebenchmark_marker_failed",
  "artifacts": "experiments/bundles/20261028T205515Z-direct-g8-4k-prebenchmark-marker-failed",
  "conclusion": "服务已启动，benchmark请求前因Direct-G8 marker缺失退出；0轮benchmark。保留原exit1和完整清理证据，不判数值或性能失败。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T205515Z-direct-g8-4k-prebenchmark-marker-failed](../../../experiments/bundles/20261028T205515Z-direct-g8-4k-prebenchmark-marker-failed)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T205515Z-direct-g8-4k-prebenchmark-marker-failed/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T205515Z-direct-g8-4k-prebenchmark-marker-failed/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
