<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #231 · PR25 与缓存修复后的 KV 保存恢复

- **尝试**：验证535 KV保存＋H2D批量恢复组合在原官方两档各四轮的表现；不包含staging primitive。
- **改动**：main0bf9＋535组合/tree98f4688a，SO14f；[源码身份](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds-control/source-manifest.json)，前序实现与边界见[方法记录](../../methods/pr25-kv-current.md)。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：4096/16384 / 1024 / 64 / 1536。
- **结果**：535官方两档各4轮、1536/0；第2–4轮4K5703.70/16K4060.24 tok/s，28条FULL链。KV失配、差值null；完整105未过，不设新基线。
- **是否保留**：保留完整官方组合观察与原件；不算严格因果收益、不更新accepted baseline，完整105仍待。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T19:31:00Z",
  "profile_id": "pr25-kv-current",
  "phase": "official_four_rounds_restore_pitched",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "4096/16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "1536",
  "profiler": "false",
  "status": "official_restore_pitched_kv_mismatch",
  "artifacts": "experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds",
  "conclusion": "535 KV＋H2D组合完成原官方4K/16K各四轮，1536请求全成功；第2–4轮4K5703.70、16K4060.24 total tok/s，Mean TTFT3635.20/123213.90ms。4K原四轮5404.12/5733.36/5614.67/5763.06，16K3807.83/4059.89/4060.90/4059.94，首轮原件保留。28条完整SAVE/FULL/DROP链、VERIFY0；真实34层native图通过。main0bf9加535组合/tree98f4688a、SO14f、初始DBfb035；实际KV546432对526基线547536，比较仅actual_kv失配，gain_calculated=false、差值null；只保留组合绝对观察，不称H2D独立或稳定收益。20:29:16 UTC清理、source/native未变与DB恢复通过；完整105尚未通过，保留结果但不更新accepted baseline，不为解释差异重跑。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/benchmark-command.json)；[command.txt](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261025_033156.csv](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/benchmark_results/raw_runs_20261025_033156.csv)；[summary_20261025_033156.csv](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/benchmark_results/summary_20261025_033156.csv)；[result.json](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
