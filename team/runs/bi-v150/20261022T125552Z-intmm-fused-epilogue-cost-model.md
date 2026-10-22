<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T125552Z-intmm-fused-epilogue-cost-model

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #128 · int8 与 W8A8 决策测量

- **尝试**：真实形状上的 int8 GEMM、W8A16、_int_mm+融合 epilogue 及 QDQ 精度模拟；负结果与候选并存，不混用证据级别。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：0 / 0 / 0 / 0。
- **结果**：三 kernel 成本模型（自写 Triton per-token 对称量化、torch._int_mm、自写融合 dequant+bias）在合并服务形状上的分相实测
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T125552Z-intmm-fused-epilogue-cost-model",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:55:52+00:00",
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
  "status": "complete_positive_for_three_kernel_chain",
  "artifacts": "experiments/operator/20261022T125552Z-intmm-fused-epilogue-cost-model",
  "conclusion": "三 kernel 成本模型（自写 Triton per-token 对称量化、torch._int_mm、自写融合 dequant+bias）在合并服务形状上的分相实测。ratio = bf16 / 三 kernel 合计：m=2048 为 qkv 1.412、o 1.224、gate_up 1.493、down 1.543、lm_head 1.523；m=8192 为 qkv 1.178、o 1.246、gate_up 1.504、down 1.614（lm_head 在 m=8192 未测，受输出张量尺寸保护跳过）；m=64 为 gate_up 1.604、lm_head 1.523、down 1.135、qkv 1.103、o 0.877；m=128 多数形状低于 1（qkv 0.776、o 0.681）。`_int_mm` 吞吐只在 m>=2048 达到 193–255 TOP/s，m=64/128 为 27.3–112.4 TOP/s，小 M 的收益来自字节减半而非更快的整数通路。量化与反量化各只有一次启动且含 eager Python 开销，进 CUDA graph 后小 M 还应改善。保留为候选，未上服务端到端。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T125552Z-intmm-fused-epilogue-cost-model](../../../experiments/operator/20261022T125552Z-intmm-fused-epilogue-cost-model)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
