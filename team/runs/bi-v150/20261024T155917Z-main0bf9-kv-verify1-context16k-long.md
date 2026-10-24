<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T155917Z-main0bf9-kv-verify1-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #222 · PR25 与缓存修复后的 KV 保存恢复

- **尝试**：当前性能对照基线已更新到main0bf9/tree8671（526文件、SO14f）：161030按官方4K/16K各四轮，第2–4轮5758.72/4045.20 total tok/s，TTFT3626.85/124212.05ms，1536/0；KV547536、初始DBfb035。该版本本实例完整105仍待，不能称最终合格基线。532组合155917 VERIFY1与4题语义门通过；171101正式测量前因目录前缀被图门误拒，原exit1和后验强身份相同证据保留，不记吞吐。只修测量门的重试由运行负责人维护，完成后另登记。

队友[PR31](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/31)实际受测e972997、SO271327a0，暖后单轮4K/16K为5766.41/4048.28，准确率102/105；标题Draft且未合并。[原manifest](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/d79b7b1a012943dce867d1adcc29a45e0d7b79bf/docs/evidence/ragged-gqa-segments-20261024/service-final/manifest.json)与[acceptance](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/d79b7b1a012943dce867d1adcc29a45e0d7b79bf/docs/evidence/ragged-gqa-segments-20261024/service-final/acceptance.json)保留其边界。双方源码、SO、轮数及DB/KV不完全同条件，不直接算收益；#33/#36仍是局部探针，#37服务准确率仍待，#38仅调研，不当作新基线。

前序7596共同基点的两轮筛选继续保留：同KV546432与DB，4K+0.103%/+0.644%但无FULL覆盖，16K+4.728%/−0.493%；仅保留候选，不确认稳定收益，不把旧组合成绩赋给新main。
- **改动**：相关实现 [pr25-kv-current-pair.json](../../../analysis/pr25-kv-current-pair.json)；[result.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/result.json)；[archive-receipt.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds-control/archive-receipt.json)；[source-manifest.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/source-manifest.json)；[coverage.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/coverage.json)；[semantic-validation.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/model-path/semantic-validation.json)；[archive-receipt.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds/result.json)；[state.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/archive-receipt.json)；[coverage.json](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long-control/coverage.json)；[semantic-validation.json](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/model-path/semantic-validation.json)；[summary_20261025_001229.csv](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark_results/summary_20261025_001229.csv)；[state.json](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T171101Z-main0bf9-kv-official-four-rounds/result.json)；[audit.json](../../../experiments/framework/20261024T171101Z-main0bf9-kv-official-four-rounds-control/postfailure-cache-audit/audit.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务KV全字节VERIFY1与独立4题语义/实际编译图检查；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32/0；R16960、每方向729415680字节一致，SAVE504/FULL2688。另同服务4/4语义正确、实际34层native图；VERIFY1不计性能或完整准确率。
- **是否保留**：保留KV字节、真实模型路径和4题语义门；允许进入关闭VERIFY回读的性能对照，完整组合准确率另验。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T155917Z-main0bf9-kv-verify1-context16k-long",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T15:59:17Z",
  "profile_id": "pr25-kv-current",
  "phase": "kv_verify1_context16k_long",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "kv_verify1_model_path_pass",
  "artifacts": "experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long",
  "conclusion": "main0bf9显式加入单victim KV SAVE/FULL后的532文件组合通过VERIFY1：32成功0失败，R16960/1060页、每方向729415680字节一致，SAVE504次（420 linear＋84 pitched）/FULL2688次/zero0，17个scheduled token消费者到达；同服务4/4语义正确、实际34层native图。候选tree350938b7，KV547536，SO14f4457a复用7596构建；初始DBfb035397。driver exit0，16:05:22 UTC清理、source/native未变、原DB207f1b恢复。只保留字节与模型路径门，不报性能或完整准确率；P重排未观察到，不声称每请求native执行或B40覆盖。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T155917Z-main0bf9-kv-verify1-context16k-long](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/manifest.json)；[source-sha256.json](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
