<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T164922Z-w8a8-bf16-inside-op-control

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #145 · int8 与 W8A8 决策测量

- **尝试**：真实形状上的 int8 GEMM、W8A16、_int_mm+融合 epilogue 及 QDQ 精度模拟；负结果与候选并存，不混用证据级别。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 16。
- **结果**：与同实例 kernel-only 的 3236.25 / 56.35 相比，op 边界本身要让出约 18%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T164922Z-w8a8-bf16-inside-op-control",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T16:49:22+00:00",
  "profile_id": "int8_decision",
  "phase": "warm_probe_16k_control_arm",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "db55579",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "16",
  "profiler": "false",
  "status": "complete_control_op_overhead_18pct",
  "artifacts": "experiments/operator/20261022T164922Z-w8a8-bf16-inside-op-control",
  "conclusion": "对照组，用来把“custom op 边界成本”和“int8 链成本”分开：同一 op 包装、同一调用点、`VLLM_FL_BIV150_W8A8_BF16_ONLY=1` 让 op 内部改回 bf16 `F.linear`。16K 缩放暖探针（16384x1024x64x16）：repeat1 2102.84 / TPOT 56.05，repeat2 2645.10 / TPOT 74.37，两轮都 valid。与同实例 kernel-only 的 3236.25 / 56.35 相比，op 边界本身要让出约 18%；而 int8 链在同包装下只有 1721.67 / TPOT 112.72（-47%）。两点合起来：int8 在真实服务里主要在 decode 段吃亏（M 小、每层一次 op 加量化/反量化），prefill 的 1.2–1.54x 无法覆盖，端到端没有确认收益。此轮之后 W8A8 线性链停止集成，补丁保留分支 `codex/20261022-w8a8-linear`（默认关闭），不再进入合并讨论。若将来重启，前提是换成编译器原生捕获、无 Python 分发的 int8 算子，并且只在 prefill 段启用。GPU KV 486,464（保留 bf16 权重 + int8 副本的代价），也是负结果的一部分。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T164922Z-w8a8-bf16-inside-op-control](../../../experiments/operator/20261022T164922Z-w8a8-bf16-inside-op-control)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
