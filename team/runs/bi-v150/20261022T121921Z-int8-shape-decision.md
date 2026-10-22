<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T121921Z-int8-shape-decision

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #127 · int8 与 W8A8 决策测量

- **尝试**：真实形状上的 int8 GEMM、W8A16、_int_mm+融合 epilogue 及 QDQ 精度模拟；负结果与候选并存，不混用证据级别。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：准确率门；输入 / 输出 / 并发 / 请求数：0 / 0 / 0 / 0。
- **结果**：int8 linear 候选在模型真实形状上的 A/B（seed=1234，权重预量化，激活量化单独计时）
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T121921Z-int8-shape-decision",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:19:21+00:00",
  "profile_id": "int8_decision",
  "phase": "kernel_micro_and_accuracy_screen",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "0",
  "output_len": "0",
  "concurrency": "0",
  "num_prompts": "0",
  "profiler": "false",
  "status": "complete_negative_for_triton_int8_and_torch_chain",
  "artifacts": "experiments/operator/20261022T121921Z-int8-shape-decision",
  "conclusion": "int8 linear 候选在模型真实形状上的 A/B（seed=1234，权重预量化，激活量化单独计时）。原件为 20261022T122551Z-int8-decision2/int8-shapes.json：FlagGems scaled_mm（该 vendor 走通用 Triton 回退）fg_ratio 在 m=2048 为 0.5185–0.6997、m=8192 为 0.5335–0.7020，对应 46.25–63.53 TOP/s；torch._int_mm 加 torch 反量化链 chain_ratio 全域 0.3162–1.0382。同一份数据在 m=64 给出 fg_ratio 0.8689–2.0536，其中 gate 1.974 / up 2.054 / down 1.756 / q_proj 1.603 / o_proj 1.545 快于 bf16，而 k_proj 0.873、v_proj 0.869、lm_head 0.968 慢于 bf16；该臂的 torch 版激活量化耗时 0.063–0.082 ms，与 int8 GEMM 同量级。结论：int8 在 decode 尺寸靠减半字节取胜，在 prefill 尺寸任何现成 int8 GEMM 都是负的。（本目录的 int8-shapes.log 是首次运行，只出 1 行后因脚本 del 位置错误 rc=1 中止，完整数据在同名 json，来自 #130（20261022T122551Z）那次重跑。）"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T121921Z-int8-shape-decision](../../../experiments/operator/20261022T121921Z-int8-shape-decision)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
