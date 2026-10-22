<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T122607Z-original-baseline

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #72 · 完整官方吞吐对照

- **尝试**：原版与完整候选的原始官方结果；保留DB、KV和计分边界。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：未记录 / 1024 / 64 / 未记录。
- **结果**：fullpost16:17:27.184712Z68MiB0%IPv4IPv6端口闭无GPU进程，server/benchmark/EngineCore退出；最终分档候选/原版1.933207729x和3.166027317x，初始DB不同且KV候选+96，不作cache-matched因果稳定或官方总分
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T122607Z-original-baseline",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T12:26:07.844667+00:00",
  "profile_id": "original13eb",
  "phase": "official_two_case_original_baseline",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "",
  "profiler": "false",
  "status": "official_two_case_complete_independent_review_pass_with_exit_warning",
  "artifacts": "experiments/official/20261021T122607Z-original-baseline",
  "conclusion": "本地stdlib独立终审通过：原8raw/2summary每档四轮SUCCESS并丢原首轮；4K原2-4均值1905.46total tok/s/687.936667s/TTFT12310.556667ms；16K861.986667total/2584.99s/TTFT636429.44ms；逐项225archiveSHA及captured live225匹配，原13eb/worker446f/Attention archive-live-postcopy bab2，无retained模块挂钩或BIV150日志marker；原CLI/model/benchmark0813/driver791/packages/单卡32768MiB/CPU6固定；KV521840；DB512表19130行到516表19270行实体三hash复算；benchmark12:28:47.784861至16:14:45.731362UTC/driver16:14:50.001906exit0cleanup_errors空；fullpost16:17:27.184712Z68MiB0%IPv4IPv6端口闭无GPU进程，server/benchmark/EngineCore退出；runner166637仅Z/PPid1未回收，首次seal末/proc断言失败及process-review说明保留；双方shutdown均有force-kill剩余1进程warning，monitor-15；最终分档候选/原版1.933207729x和3.166027317x，初始DB不同且KV候选+96，不作cache-matched因果稳定或官方总分；详见analysis/2026-10-21-official-final-comparison.json及本run/independent-final-review.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T122607Z-original-baseline](../../../experiments/official/20261021T122607Z-original-baseline)
- 原命令：[benchmark-command.json](../../../experiments/official/20261021T122607Z-original-baseline/benchmark-command.json)；[command.txt](../../../experiments/official/20261021T122607Z-original-baseline-control/command.txt)；[launch.sh](../../../experiments/official/20261021T122607Z-original-baseline-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261021T122607Z-original-baseline/manifest.json)；[postflight-full.json](../../../experiments/official/20261021T122607Z-original-baseline/postflight-full.json)
- 原始结果：[result.json](../../../experiments/official/20261021T122607Z-original-baseline/result.json)；[raw_runs_20261021_202847.csv](../../../experiments/official/20261021T122607Z-original-baseline/benchmark_results/raw_runs_20261021_202847.csv)；[summary_20261021_202847.csv](../../../experiments/official/20261021T122607Z-original-baseline/benchmark_results/summary_20261021_202847.csv)
- 日志 / 采样：[server.log](../../../experiments/official/20261021T122607Z-original-baseline/server.log)；[gpu.csv](../../../experiments/official/20261021T122607Z-original-baseline/gpu.csv)；[exit-code](../../../experiments/official/20261021T122607Z-original-baseline/exit-code)
- 相关说明：[2026-10-21-team-reproduction-review](../../../analysis/2026-10-21-team-reproduction-review.md)；[2026-10-21-prefill-unmeasured-candidates](../../../analysis/2026-10-21-prefill-unmeasured-candidates.md)；[2026-10-21-original-baseline-final-evidence](../../../analysis/2026-10-21-original-baseline-final-evidence.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
