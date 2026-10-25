<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T140749Z-team-main0915-current-official-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #274 · GQA KV读取缓存策略

- **尝试**：补当期原main冷/首暖对照，帮助阅读.cg组件与整模结果差异。
- **改动**：没有新增优化；原0915/603源码与native14f。run名four-rounds及原failed/SIGTERM/stage=running保持，实际只有两轮且已结束。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-kv-cg.md)。
- **怎么测**：原团队main0915完整603/tree766b、native14f与官方参数不变，无.cg或stride；RUNS4/SKIP_FIRST1原设置保留，用户提醒已有完整基线后向所属owner SIGTERM。14:18:14 source/native/DB及清理通过。
- **结果**：原main4K冷/首暖5404.31/5761.99 tok/s、512成功；因已有完整基线主动停止，仅两轮，16K未测。
- **是否保留**：保留当期部分对照，不覆盖旧完整基线；.cg搁置、当前不能合并，不追加profile，转下个高潜力方向。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T140749Z-team-main0915-current-official-four-rounds",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T14:07:49+00:00",
  "profile_id": "gqa-kv-cg",
  "phase": "当期原main两轮对照主动停止",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0915f01d5efc2b31af65182ddb87e2d2f62bab0c",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "team_main_current_control_partial",
  "artifacts": "experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds",
  "conclusion": "原团队main0915/tree766b完整603、native14f、原官方参数，无.cg或stride。4K冷/首暖5404.31/5761.99 tok/s，TTFT5869.37/3729.51ms，两轮512请求全部成功。用户提醒已有同生产代码完整基线，主动SIGTERM停止；14:18:14源码/native/DB恢复与清理、9031关闭和68MiB/0%后态通过。run名four-rounds与原failed/SIGTERM/stale stage保留，本次只有两轮、16K未测，不冒充完整官方成绩或覆盖旧基线。与.cg首暖4944.66并列保留，不据此定位内核因果；.cg搁置、不新增profile，主线转下个高潜力方向。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T140749Z-team-main0915-current-official-four-rounds](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261025_220850.csv](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds/benchmark_results/raw_runs_20261025_220850.csv)；[result.json](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
