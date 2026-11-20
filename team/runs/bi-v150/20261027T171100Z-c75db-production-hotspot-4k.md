<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T171100Z-c75db-production-hotspot-4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #389 · 同步原生GQA实际热点诊断

- **尝试**：原profile posthoc因关闭compile cache缺fresh FX而不完整；现成节点解析通过。4个N64样本的1988插桩区间中，S2/42层17.9005ms、MM6.1148ms、W8A8 1.8053ms、reduce0.4305ms；不能当未插桩时延或官方吞吐。N32未达采样门，未采M2048。
- **改动**：相关实现 [summary.json](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/summary.json)；[raw-evidence.json](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/raw-evidence.json)；[hotspot-and-posthoc-review.json](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/hotspot-and-posthoc-review.json)；[graph-summaries.csv](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/graph-summaries.csv)；[kernel-rankings.csv](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/kernel-rankings.csv)；[native-logical-bandwidth.json](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/native-logical-bandwidth.json)；[manifest.json.storage.json](../../../experiments/bundles/20261027T171100Z-c75db-production-hotspot-4k/manifest.json.storage.json)；[raw.tar.xz.storage.json](../../../experiments/bundles/20261027T171100Z-c75db-production-hotspot-4k/raw.tar.xz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：3109原件完整xz75.29MB；N32仅17replay，未采M2048。
- **结果**：原posthoc不完整；节点解析通过，4个N64样本/1988插桩区间；S2共17.9005ms为主要区间。
- **是否保留**：保留热点诊断；不是未插桩时延或官方吞吐。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T171100Z-c75db-production-hotspot-4k",
  "local_date": "2026-10-27",
  "utc_start": "20261027T171100Z",
  "profile_id": "native-gqa-production-hotspot",
  "phase": "profile",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b3b87d2a1c13448bd8c6bc24e8045c0458b8b9dd",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "true",
  "status": "native_gqa_profile_diagnostic_incomplete_parsed",
  "artifacts": "experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k",
  "conclusion": "原服务/driver成功，原posthoc=false因关闭compile cache无fresh FX/graph文件，不改写原失败。既有节点解析通过：4个N64样本/1988插桩区间，boundary26.7253ms/full29.2221ms，S2共17.9005ms、MM6.1148ms、W8A8 1.8053ms、reduce0.4305ms；不是未插桩时延或吞吐。N32未达32replay，未采M2048。退出源814/native14f/SOf720与DB真。3109原件完整xz75.29MB无损分块，原gzip147.96MB本地保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T171100Z-c75db-production-hotspot-4k](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：[graph-summaries.csv](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/graph-summaries.csv)；[kernel-rankings.csv](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/kernel-rankings.csv)；[samples.csv](../../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/samples.csv)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
