<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T231259Z-pr105-hotspot16k-single-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #470 · BI-V150特定形状GEMM

- **尝试**：分析PR105原官方16K单轮诊断的真实热点和native GQA覆盖。
- **改动**：benchmark前reader将真实overlap_v=true错判为false，0请求/0吞吐；保留资格失败，不归为模型错误。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原官方16K输入16384/输出1024/并发64/128请求入口；GQA shape/SO/stride/capture marker reader gate在benchmark前拒绝。
- **结果**：预检在benchmark前因GQA reader契约错误退出；没有模型请求、吞吐样本或性能/数值结论。不是模型错误。清理及DB/source恢复通过。
- **是否保留**：保留reader资格失败；0请求，不作为模型数值错误或性能结果。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T231259Z-pr105-hotspot16k-single-diagnostic",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T23:12:59+00:00",
  "profile_id": "shape-gemm",
  "phase": "profile_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b3b87d2a1c13448bd8c6bc24e8045c0458b8b9dd",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "cuda",
  "status": "profile_diagnostic_reader_gate_failed_before_benchmark",
  "artifacts": "experiments/bundles/20261028T231259Z-pr105-hotspot16k-single-diagnostic",
  "conclusion": "预检在benchmark前因GQA reader契约错误退出；没有模型请求、吞吐样本或性能/数值结论。不是模型错误。清理及DB/source恢复通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T231259Z-pr105-hotspot16k-single-diagnostic](../../../experiments/bundles/20261028T231259Z-pr105-hotspot16k-single-diagnostic)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T231259Z-pr105-hotspot16k-single-diagnostic/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T231259Z-pr105-hotspot16k-single-diagnostic/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
