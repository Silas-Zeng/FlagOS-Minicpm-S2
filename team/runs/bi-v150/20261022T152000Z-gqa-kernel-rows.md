<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T152000Z-gqa-kernel-rows

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #133 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：0 / 0 / 64 / 0。
- **结果**：kernel 级 A/B，同一份 seed 固定操作数，参考为通用 kernel 钉住 w1s1
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T152000Z-gqa-kernel-rows",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T15:20:00+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "kernel_micro_ab",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b71e585342d6ea1638dad3e42fa1c0ec7f70b8df",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "0",
  "output_len": "0",
  "concurrency": "64",
  "num_prompts": "0",
  "profiler": "false",
  "status": "complete_kernel_ab",
  "artifacts": "experiments/operator/20261022T152000Z-gqa-kernel-rows",
  "conclusion": "kernel 级 A/B，同一份 seed 固定操作数，参考为通用 kernel 钉住 w1s1；CSV 每行含 median_ms、speedup、effective_gbps、max_abs_diff。最快配置 rows=8/pages=1/w1s1：batch64/kv4096 0.6484 ms 对 0.9477 ms（1.462x，414.0 对 283.3 GB/s，max_abs_diff 4.88e-4）；batch16/kv16384 0.5362 ms 对 0.9807 ms（1.829x，500.6 对 273.7 GB/s，max_abs_diff 1.22e-4）；batch1/kv64 0.0181 对 0.0217 ms（1.204x，发射受限）。变差项：pages_per_step=2 在 batch64 掉到 0.9669 ms、num_warps=2 到 0.7402 ms、rows=16 到 0.6706 ms，所以 ROWS=8、一步一页、单 warp 是网格最优。这是 kernel 层证据，不是服务吞吐。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T152000Z-gqa-kernel-rows](../../../experiments/operator/20261022T152000Z-gqa-kernel-rows)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：[20261022T152000Z-gqa-kernel-rows.csv](../../../experiments/operator/20261022T152000Z-gqa-kernel-rows/20261022T152000Z-gqa-kernel-rows.csv)
- 日志 / 采样：未单列，见原始目录
- 相关说明：[2026-10-22-gqa-decode-kernel](../../../analysis/2026-10-22-gqa-decode-kernel.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
