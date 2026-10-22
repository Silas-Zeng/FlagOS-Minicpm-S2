<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T124239Z-w8a16-weight-only-gemm

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #128 · int8 与 W8A8 决策测量

- **尝试**：真实形状上的 int8 GEMM、W8A16、_int_mm+融合 epilogue 及 QDQ 精度模拟；负结果与候选并存，不混用证据级别。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：0 / 0 / 0 / 0。
- **结果**：输出通道缩放）自写 Triton kernel，两种权重布局都测：[N,K] 列读（不合并）0.30-0.61x，[K,N] 双向合并 0.34-0.42x，M=8192 0.21x
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T124239Z-w8a16-weight-only-gemm",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:42:39+00:00",
  "profile_id": "int8_decision",
  "phase": "kernel_micro",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "0",
  "output_len": "0",
  "concurrency": "0",
  "num_prompts": "0",
  "profiler": "false",
  "status": "complete_negative_w8a16",
  "artifacts": "experiments/operator/20261022T124239Z-w8a16-weight-only-gemm",
  "conclusion": "W8A16（int8 权重、bf16 数学、末端按输出通道缩放）自写 Triton kernel，两种权重布局都测：[N,K] 列读（不合并）0.30-0.61x，[K,N] 双向合并 0.34-0.42x，M=8192 0.21x；权重带宽只有 39-129 GB/s，而设备锚点 553 GB/s。瓶颈是内循环逐元素 int8→bf16 加宽，不是地址模式，与 int8 KV 探针慢 1.58x 同源。结论：该设备上进 tensor core 的数据必须一路 int8，任何逐元素转换都亏。不保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T124239Z-w8a16-weight-only-gemm](../../../experiments/operator/20261022T124239Z-w8a16-weight-only-gemm)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
