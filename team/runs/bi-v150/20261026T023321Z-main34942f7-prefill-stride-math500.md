<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T023321Z-main34942f7-prefill-stride-math500

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #288 · Prefill stride常量特化

- **尝试**：验证最新A组合是否满足官方准确率门槛，不继承父main或队友分数。
- **改动**：不新增源码或改采样；复用已审冻结组合与原35d驱动/评分器，只跑这一轮，不反复抽样刷分。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-stride.md)。
- **怎么测**：与性能组同冻结618/treeaa43，原105/temperature1/top_p.95/batch8/max32768及服务参数未改，source/native未变，DB恢复和清理通过。
- **结果**：原105题103/105（98.0952%），valid/pass；105 stop，0 transport/截断/空答案/空提取，模型实际路径及收尾通过。
- **是否保留**：结合本组两档完整官方对照保留，PR60已合并为6971ef48；新基线5656.77/4119.24 tok/s、103/105，保留KV差异和单组小幅观察限制。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T023321Z-main34942f7-prefill-stride-math500",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T02:33:21+00:00",
  "profile_id": "prefill-stride",
  "phase": "Prefill stride接入main34942f7原105准确率",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "34942f7e28da5c954ab05878dec75807da9d7a93",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_stride_main34942_accuracy_pass",
  "artifacts": "experiments/accuracy/20261026T023321Z-main34942f7-prefill-stride-math500",
  "conclusion": "A在main34942/PR51上同冻结618/treeaa43ea2c原105题为103/105（98.0952%），valid/pass，105 stop，0 transport/截断/空答案/空提取；原temperature1/top_p.95/batch8/max32768不变。模型实际路径、源码/native未变、DB恢复和清理通过。保留该资格与原官方4K/16K完整对照5656.77/4119.24 tok/s；对同base观察+0.3176%/+0.4674%，KV548336对548432及单组暖轮趋势限制保留，不能称严格因果或抹去旧源码异常。按已审冻结3文件创建PR并合并，不重复测试、不重复抽样。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T023321Z-main34942f7-prefill-stride-math500](../../../experiments/accuracy/20261026T023321Z-main34942f7-prefill-stride-math500)
- 原命令：[command.json](../../../experiments/accuracy/20261026T023321Z-main34942f7-prefill-stride-math500-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/accuracy/20261026T023321Z-main34942f7-prefill-stride-math500/manifest.json)；[source-sha256.json](../../../experiments/accuracy/20261026T023321Z-main34942f7-prefill-stride-math500-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/accuracy/20261026T023321Z-main34942f7-prefill-stride-math500/result.json)
- 日志 / 采样：[server.log](../../../experiments/accuracy/20261026T023321Z-main34942f7-prefill-stride-math500/server.log)；[gpu.csv](../../../experiments/accuracy/20261026T023321Z-main34942f7-prefill-stride-math500/gpu.csv)；[exit-code](../../../experiments/accuracy/20261026T023321Z-main34942f7-prefill-stride-math500/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
