<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T093453Z-gqa-decode-official-4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #121 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：4096 / 1024 / 64 / 256。
- **结果**：相对官方基线 1878.47 为 +156.0%，相对队友官方 3683.65 为 +30.6%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T093453Z-gqa-decode-official-4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T09:34:53+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "official_4k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b71e585342d6ea1638dad3e42fa1c0ec7f70b8df",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "complete_official_four_rounds",
  "artifacts": "experiments/operator/20261022T093453Z-gqa-decode-official-4k",
  "conclusion": "自研 GQA decode attention kernel（ROWS=8、grid=(seq,kv_head,segment)、页标量索引、exp2 softmax、自带 strided 段归约、split-K 宽度按 TARGET_PROGRAMS=256 自适应）。官方驱动四轮原始值为 2646.96 / 4615.49 / 4904.45 / 4908.13，协议丢第一轮取后三轮平均得 total 4809.36 tok/s，mean TTFT 4723.09 ms，mean TPOT 61.64 ms（后三轮 60.32/64.23/60.37）。相对官方基线 1878.47 为 +156.0%，相对队友官方 3683.65 为 +30.6%。四轮递增来自官方驱动不传 seed 造成的 prefix cache 逐轮升温，协议均值比稳态低约 2%。本行不含任何探针数字：48 ms 级 TPOT 属于 #125 的暖探针，不能与官方四轮混写。保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T093453Z-gqa-decode-official-4k](../../../experiments/operator/20261022T093453Z-gqa-decode-official-4k)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：[summary.csv](../../../experiments/operator/20261022T093453Z-gqa-decode-official-4k/summary.csv)；[raw_runs.csv](../../../experiments/operator/20261022T093453Z-gqa-decode-official-4k/raw_runs.csv)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
