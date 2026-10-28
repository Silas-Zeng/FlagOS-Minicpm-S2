<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T215829Z-bm32bn32-warp32-cpu-compile-metadata-failed

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #464 · BI-V150特定形状GEMM

- **尝试**：检查BM64/BN64/BK128下w16/w32候选的CPU编译可行性。
- **改动**：w16成功编译并保存6项产物；随后distribution version查询失败，因此w32未执行。父归档目录名不代表tile配置。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：BM64/BN64/BK128，CPU-only；只有w16已运行编译，w32未执行。
- **结果**：实际为BM64/BN64/BK128：w16编译成功并留下6项产物，随后Triton distribution version查询因metadata缺失失败；w32未执行。父归档目录名bm32bn32不代表本次tile。
- **是否保留**：保留环境查询失败；父归档目录名称bm32bn32不代表本次tile配置。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T215829Z-bm32bn32-warp32-cpu-compile-metadata-failed",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T21:58:29.635885+00:00",
  "profile_id": "shape-gemm",
  "phase": "cpu_compile",
  "device": "CPU",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "shape_gemm_bm32bn32_warp32_cpu_metadata_failed",
  "artifacts": "experiments/bundles/20261028T215829Z-bm32bn32-warp32-cpu-compile-metadata-failed",
  "conclusion": "实际为BM64/BN64/BK128：w16编译成功并留下6项产物，随后Triton distribution version查询因metadata缺失失败；w32未执行。父归档目录名bm32bn32不代表本次tile。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T215829Z-bm32bn32-warp32-cpu-compile-metadata-failed](../../../experiments/bundles/20261028T215829Z-bm32bn32-warp32-cpu-compile-metadata-failed)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T215829Z-bm32bn32-warp32-cpu-compile-metadata-failed/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T215829Z-bm32bn32-warp32-cpu-compile-metadata-failed/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
