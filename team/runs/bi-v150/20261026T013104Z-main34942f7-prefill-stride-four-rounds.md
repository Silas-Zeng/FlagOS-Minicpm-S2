<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T013104Z-main34942f7-prefill-stride-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #287 · Prefill stride常量特化

- **尝试**：确认stride常量化能否在保留PR51修复的新main上改善实际吞吐。
- **改动**：仅normalized stride及Q-fragment/compute-order精确依赖身份闭合，共3个生产文件；PR51 runner绑定和其它615文件不变。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-stride.md)。
- **怎么测**：34942f7/618/treeaa43ea2c，原官方4K/16K各四轮弃首轮、原native14f/DB207f/服务参数；actual norm/Q/compute-order/PR51/Graph与source/native/DB恢复清理门通过。
- **结果**：原官方4K/16K各四轮、1536成功；暖均5656.77/4119.24 tok/s，对本组新main基线观察+0.3176%/+0.4674%。
- **是否保留**：保留小幅正信号；本条为性能结束时状态，后继同源原105已103/105通过，见同方法准确率轮次及PR60。实际KV548336对548432及单组暖轮趋势限制保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T013104Z-main34942f7-prefill-stride-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T01:31:04+00:00",
  "profile_id": "prefill-stride",
  "phase": "Prefill stride接入main34942f7官方对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "34942f7e28da5c954ab05878dec75807da9d7a93",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_stride_main34942_positive_pending_accuracy",
  "artifacts": "experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds",
  "conclusion": "main34942/PR51上仅11项prefill stride constexpr及两个严格依赖身份闭合，618/treeaa43ea2c。原官方4K/16K各四轮、1536请求全部SUCCESS，实际prefill/Q-fragment/compute-order、PR51及Graph门通过，source/native不变、DB207f恢复且清理完成。弃首轮4K5656.77、16K4119.24 tok/s，对本次同base原官方基线5638.86/4100.076667观察+0.3176%/+0.4674%；TTFT3355.756667/122086.973333ms。KV548336对基线548432、4K暖轮逐步升速，不能声称严格孤立kernel因果或统计稳定收益。保留本组小幅正信号，已启动同冻结源码原105准确率，尚无分数；不继承父main或队友资格，合并待该轮结果。旧0915对照和SIMT负结果保留，不混入本组。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T013104Z-main34942f7-prefill-stride-four-rounds](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_093324.csv](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds/benchmark_results/raw_runs_20261026_093324.csv)；[summary_20261026_093324.csv](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds/benchmark_results/summary_20261026_093324.csv)；[result.json](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261026T013104Z-main34942f7-prefill-stride-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
