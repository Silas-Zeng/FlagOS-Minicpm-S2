<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T092944Z-sql-mixed-official

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #57 · 完整官方吞吐对照

- **尝试**：原版与完整候选的原始官方结果；保留DB、KV和计分边界。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：未记录 / 1024 / 64 / 未记录。
- **结果**：原2-4均值分档totalTPS比4K1.933207729x/16K3.166027317x，TTFT变化-61.15818754%/-70.92157564%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T092944Z-sql-mixed-official",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T09:29:44.531166+00:00",
  "profile_id": "sql_reflection+C3",
  "phase": "official_two_case",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "",
  "profiler": "false",
  "status": "official_two_case_complete_independent_review_pass",
  "artifacts": "experiments/official/20261021T092944Z-sql-mixed-official",
  "conclusion": "Independent CPU reviewPASS all8raw2summary originalcaseorder4rounds each skiporiginalfirst;4K each256success1048576in262144out summary3683.65total736.73output tok/s355.88s meanTTFT4781.64ms meanTPOT81.79ms sampleCV1.50674249percent;16K each128success2097152in131072out summary2729.07total160.53output tok/s816.48s meanTTFT185063.65ms meanTPOT166.71ms sampleCV0.02391699percent;all numeric summary means verified;230archiveSHA individually verified;fourcore hash exact090505 accuracy source080656;original0813benchmark argv andSERVER verified no profiler no smoke;KV521936;DB489tables18384rows to501tables18789rows physical/schema/logical hashes independently recomputed change;benchmark09:30:39.405817 to10:53:36.070467UTC;exit0 cleanup_errors empty;fullpostflight10:55:26.276614UTC68MiB0percent closed no processes;候选绝对成绩及原122607完整对照已独立终审；原2-4均值分档totalTPS比4K1.933207729x/16K3.166027317x，TTFT变化-61.15818754%/-70.92157564%；原DBbefore512/19130对候489/18384非cache-matched，KV原521840对候521936；不声称因果稳定或官方总分；详见analysis/2026-10-21-official-final-comparison.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T092944Z-sql-mixed-official](../../../experiments/official/20261021T092944Z-sql-mixed-official)
- 原命令：[benchmark-command.json](../../../experiments/official/20261021T092944Z-sql-mixed-official/benchmark-command.json)；[command.txt](../../../experiments/official/20261021T092944Z-sql-mixed-official-control/command.txt)；[launch.sh](../../../experiments/official/20261021T092944Z-sql-mixed-official-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261021T092944Z-sql-mixed-official/manifest.json)；[postflight-full.json](../../../experiments/official/20261021T092944Z-sql-mixed-official/postflight-full.json)
- 原始结果：[raw_runs_20261021_173039.csv](../../../experiments/official/20261021T092944Z-sql-mixed-official/benchmark_results/raw_runs_20261021_173039.csv)；[summary_20261021_173039.csv](../../../experiments/official/20261021T092944Z-sql-mixed-official/benchmark_results/summary_20261021_173039.csv)；[raw_runs_20261021_173039.csv](../../../experiments/official/20261021T092944Z-sql-mixed-official/live-20261021T1004Z/raw_runs_20261021_173039.csv)；[summary_20261021_173039.csv](../../../experiments/official/20261021T092944Z-sql-mixed-official/live-20261021T1004Z/summary_20261021_173039.csv)；[result.json](../../../experiments/official/20261021T092944Z-sql-mixed-official/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261021T092944Z-sql-mixed-official/server.log)；[gpu.csv](../../../experiments/official/20261021T092944Z-sql-mixed-official/gpu.csv)；[exit-code](../../../experiments/official/20261021T092944Z-sql-mixed-official/exit-code)
- 相关说明：[2026-10-22-mm-cta-group](../../../analysis/2026-10-22-mm-cta-group.md)；[2026-10-21-sql-mixed-full-package](../../../analysis/2026-10-21-sql-mixed-full-package.md)；[2026-10-21-prefill-unmeasured-candidates](../../../analysis/2026-10-21-prefill-unmeasured-candidates.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
