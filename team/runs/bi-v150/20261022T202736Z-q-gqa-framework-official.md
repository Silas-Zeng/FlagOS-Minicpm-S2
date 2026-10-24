<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T202736Z-q-gqa-framework-official

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #170 · Q-hoist + GQA 框架组合

- **尝试**：仅适配精确GQA包装的安装身份，保留两条算术路径与原服务参数；已获单pair正信号及独立101/105准确率通过，评测DB增长另列。
- **改动**：相关实现 [METHOD.md](../../../archive/ai/20261022-framework-kv/q-gqa-framework/METHOD.md)；[biv150_q_fragment_service.py](../../../archive/ai/20261022-framework-kv/q-gqa-framework/biv150_q_fragment_service.py)；[q-gqa-service-pair.json](../../../analysis/q-gqa-service-pair.json)；[accuracy-review.json](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/accuracy-review.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：未记录 / 1024 / 64 / 未记录。
- **结果**：两case×4完成exit0、1536成功0失败，原driver核8行raw/2行summary及丢首轮2–4均值，未改CSV
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T202736Z-q-gqa-framework-official",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T20:27:37.671439+00:00",
  "profile_id": "q_gqa_framework",
  "phase": "official_two_case_current_combination",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "",
  "profiler": "false",
  "status": "completed_official_absolute_result_no_gain_claim",
  "artifacts": "experiments/official/20261022T202736Z-q-gqa-framework-official",
  "conclusion": "原官方两case×4完成exit0、1536成功0失败，原driver核8行raw/2行summary及丢首轮2–4均值，未改CSV。4K总5002.10/output1000.42 tok/s、262.25s；16K总3679.39/output216.43 tok/s、605.60s。固定QGQA414/原SERVER/benchmark/521936KV，真实同Engine Q/GQA各42；准确率引用184819的101/105。DB532/19839→540/20112，三SHA改变，绝对成绩不算跨DB增益。21:00只读一次metrics往返42.845ms、累计抢占4非终态且不能按case分摊；无profiler。原owner清理且root核703原件。详analysis/q-gqa-official-final.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T202736Z-q-gqa-framework-official](../../../experiments/official/20261022T202736Z-q-gqa-framework-official)
- 原命令：[benchmark-command.json](../../../experiments/official/20261022T202736Z-q-gqa-framework-official/benchmark-command.json)；[command.txt](../../../experiments/official/20261022T202736Z-q-gqa-framework-official-control/command.txt)；[launch.sh](../../../experiments/official/20261022T202736Z-q-gqa-framework-official-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261022T202736Z-q-gqa-framework-official/manifest.json)；[postflight-full.json](../../../experiments/official/20261022T202736Z-q-gqa-framework-official/postflight-full.json)；[purpose.json](../../../experiments/official/20261022T202736Z-q-gqa-framework-official-control/purpose.json)；[source-sha256.json](../../../experiments/official/20261022T202736Z-q-gqa-framework-official-control/source-sha256.json)
- 原始结果：[raw_runs_20261023_042832.csv](../../../experiments/official/20261022T202736Z-q-gqa-framework-official/benchmark_results/raw_runs_20261023_042832.csv)；[summary_20261023_042832.csv](../../../experiments/official/20261022T202736Z-q-gqa-framework-official/benchmark_results/summary_20261023_042832.csv)；[result.json](../../../experiments/official/20261022T202736Z-q-gqa-framework-official/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261022T202736Z-q-gqa-framework-official/server.log)；[gpu.csv](../../../experiments/official/20261022T202736Z-q-gqa-framework-official/gpu.csv)；[exit-code](../../../experiments/official/20261022T202736Z-q-gqa-framework-official/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
