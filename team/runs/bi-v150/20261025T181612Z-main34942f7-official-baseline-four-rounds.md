<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T181612Z-main34942f7-official-baseline-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #286 · 主线复核与native备用方案

- **尝试**：为包含PR51修复的新main建立本站同条件原官方性能基线，用于本次A配对。
- **改动**：无本方优化补丁；完整团队34942f7/618原源码。旧wrapper control只提供native/环境原件，不继承旧main或队友成绩。 版本、命令和源码见下方原件；[方法记录](../../methods/main-correctness.md)。
- **怎么测**：原官方4K/16K、输出1024、并发64、请求256/128，各四轮弃首轮；34942f7/618/treee35bdbe6，原native14f及服务参数。实际PR51/Q-fragment/compute-order及Graph门通过，源码/native不变、DB恢复和清理通过。
- **结果**：干净main34942/618原官方两档各四轮、1536成功；暖均4K5638.86/16K4100.08 tok/s，TTFT3368.34/122586.38ms。
- **是否保留**：保留为本次新main/A性能对照。KV548432、DB207f；4K暖轮渐升，不将单轮差值当稳定收益；本机新源105未跑。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T181612Z-main34942f7-official-baseline-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-25T18:16:12+00:00",
  "profile_id": "main-correctness",
  "phase": "团队main34942f7原官方基线",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "34942f7e28da5c954ab05878dec75807da9d7a93",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "official_baseline_complete",
  "artifacts": "experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds",
  "conclusion": "干净团队main34942f7/618/treee35bdbe6，原native14f、DB207f与官方参数；4K/16K各四轮，原CSV共1536 SUCCESS，实际PR51/Q-fragment/compute-order及Graph门通过。弃首轮暖均5638.86/4100.076667 tok/s，TTFT3368.34/122586.38ms；实际KV548432。4K暖轮5504.07→5661.71→5750.80渐升，不能把后续单轮差异当稳定收益。源码/native未变、DB恢复、所属进程与设备清理通过。仅登记本次新main性能基线，父main/队友准确率不转授；旧wrapper control仅原件来源。当前A独立配对尚在运行，不预判收益。小原件已回收核SHA，完整包待GPU空窗封存。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T181612Z-main34942f7-official-baseline-four-rounds](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_021828.csv](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds/benchmark_results/raw_runs_20261026_021828.csv)；[summary_20261026_021828.csv](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds/benchmark_results/summary_20261026_021828.csv)；[result.json](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261025T181612Z-main34942f7-official-baseline-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
