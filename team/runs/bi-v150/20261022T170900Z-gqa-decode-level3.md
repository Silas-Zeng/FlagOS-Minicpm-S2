<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T170900Z-gqa-decode-level3

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #123 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：准确率门；输入 / 输出 / 并发 / 请求数：0 / 0 / 8 / 105。
- **结果**：evalscope math_500 Level 3 全 105 题、temperature 1.0、top_p 0.95、max_tokens 32768、model-graded：0.9714（102/105），门槛 0.95，余 2.1 分
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T170900Z-gqa-decode-level3",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T17:09:00+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "accuracy_level3",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b71e585342d6ea1638dad3e42fa1c0ec7f70b8df",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "0",
  "output_len": "0",
  "concurrency": "8",
  "num_prompts": "105",
  "profiler": "false",
  "status": "complete_accuracy_gate_pass",
  "artifacts": "experiments/operator/20261022T170900Z-gqa-decode-level3",
  "conclusion": "evalscope math_500 Level 3 全 105 题、temperature 1.0、top_p 0.95、max_tokens 32768、model-graded：0.9714（102/105），门槛 0.95，余 2.1 分；队友同协议 0.9810（103/105）。kernel 与通用路径不是逐位一致：同 seed 同操作数的 A/B（见 20261022T152000Z-gqa-kernel-rows 登记行）max_abs_diff 在 batch64/kv4096 为 4.88e-4、batch16/kv16384 为 1.22e-4，bf16 约 1 ULP，因此这一关是必要条件。与固定宽度版（accuracy/20261022T152000Z-level3-gqa-kernel，0.9714）同分，说明动态段宽度不损失精度；该原件在 BI-V150 实例上，未随本轮打包。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T170900Z-gqa-decode-level3](../../../experiments/operator/20261022T170900Z-gqa-decode-level3)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
