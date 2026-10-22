<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T095640Z-gqa-decode-official-16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #122 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 128。
- **结果**：同一构建的 16K 官方四轮：原始 3349.87 / 3364.23 / 3364.10 / 3363.77，协议平均 total 3364.03 tok/s，mean TTFT 155385.04 ms，mean TPOT 133.37 ms，后三轮极差 0.0137%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T095640Z-gqa-decode-official-16k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T09:56:40+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "official_16k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b71e585342d6ea1638dad3e42fa1c0ec7f70b8df",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "false",
  "status": "complete_official_four_rounds",
  "artifacts": "experiments/operator/20261022T095640Z-gqa-decode-official-16k",
  "conclusion": "同一构建的 16K 官方四轮：原始 3349.87 / 3364.23 / 3364.10 / 3363.77，协议平均 total 3364.03 tok/s，mean TTFT 155385.04 ms，mean TPOT 133.37 ms，后三轮极差 0.0137%。相对队友官方 2729.07 为 +23.3%。原件 RESULT.md 的结论是 TTFT 由排队与抢占共同主导、KV 接近满容量；本行不再写“不是抢占受限”，该判断没有对应的已登记原件。保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T095640Z-gqa-decode-official-16k](../../../experiments/operator/20261022T095640Z-gqa-decode-official-16k)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：[summary.csv](../../../experiments/operator/20261022T095640Z-gqa-decode-official-16k/summary.csv)；[raw_runs.csv](../../../experiments/operator/20261022T095640Z-gqa-decode-official-16k/raw_runs.csv)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
