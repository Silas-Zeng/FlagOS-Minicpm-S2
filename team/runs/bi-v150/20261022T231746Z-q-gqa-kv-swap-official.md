<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T231746Z-q-gqa-kv-swap-official

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #184 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：未记录 / 1024 / 64 / 未记录。
- **结果**：两case×4完成exit0、1536成功，717原件全核
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T231746Z-q-gqa-kv-swap-official",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T23:17:46+00:00",
  "profile_id": "q_gqa_kv_swap",
  "phase": "official_two_case_current422",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "",
  "profiler": "false",
  "status": "completed_official_absolute_result_no_gain_claim",
  "artifacts": "experiments/official/20261022T231746Z-q-gqa-kv-swap-official",
  "conclusion": "原422官方两case×4完成exit0、1536成功，717原件全核；原8行raw/2摘要/丢首轮2–4均值不改。4K总4957.95/output991.59 tok/s、264.56s；16K总3669.74/output215.87 tok/s、607.19s。KV521840、DB544/20246→554/20517，gain=null，不与旧414跨条件算收益。原Q/GQA同Engine各42实际命中；16独立key的SAVE/FULL/DROP/runner/output链完整，rollback0；VERIFY0资格与准确率103/105另见既有门。原owner清理；详analysis/q-gqa-kv-official-final.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T231746Z-q-gqa-kv-swap-official](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official)
- 原命令：[benchmark-command.json](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official/benchmark-command.json)；[command.txt](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official-control/command.txt)；[launch.sh](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official/manifest.json)；[postflight-full.json](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official/postflight-full.json)；[purpose.json](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official-control/purpose.json)；[source-sha256.json](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official-control/source-sha256.json)
- 原始结果：[raw_runs_20261023_071841.csv](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official/benchmark_results/raw_runs_20261023_071841.csv)；[summary_20261023_071841.csv](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official/benchmark_results/summary_20261023_071841.csv)；[result.json](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official/server.log)；[gpu.csv](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official/gpu.csv)；[exit-code](../../../experiments/official/20261022T231746Z-q-gqa-kv-swap-official/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
