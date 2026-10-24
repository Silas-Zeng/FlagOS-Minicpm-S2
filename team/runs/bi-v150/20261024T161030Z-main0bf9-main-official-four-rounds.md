<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T161030Z-main0bf9-main-official-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #223 · PR25 与缓存修复后的 KV 保存恢复

- **尝试**：当前性能对照基线已更新到main0bf9/tree8671（526文件、SO14f）：161030按官方4K/16K各四轮，第2–4轮5758.72/4045.20 total tok/s，TTFT3626.85/124212.05ms，1536/0；KV547536、初始DBfb035。该版本本实例完整105仍待，不能称最终合格基线。532组合155917 VERIFY1与4题语义门通过；171101正式测量前因目录前缀被图门误拒，原exit1和后验强身份相同证据保留，不记吞吐。172742第二次启动因额外compiled graph日志文案门误拒，仍未发正式benchmark；原exit1与随后failed-log-replay分开保留，CPU回放不算本轮模型资格。174713按更新的筛选规则主动早停：4K第2–4轮5702.26（−0.98%）；16K第2–3轮3966.86对基线同轮4045.15（−1.94%），第4轮不完整，不计官方完整结果或新基线。18:38:01 UTC清理/source/native/DB恢复通过。候选期间另有远端证据归档、背景主机负载未完全匹配，负差仅为实测观察，不严格归因KV，不重复跑解释负差。183929独立42层搬运诊断给出0.31–0.34s毛预算，未计gather/scatter、索引与scratch，不代表staging净收益。535后续验证与性能筛选由负责人继续，本批未导入该组原件，不纳入其成绩。

队友[PR31](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/31)实际受测e972997、SO271327a0，暖后单轮4K/16K为5766.41/4048.28，准确率102/105；标题Draft且未合并。[原manifest](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/d79b7b1a012943dce867d1adcc29a45e0d7b79bf/docs/evidence/ragged-gqa-segments-20261024/service-final/manifest.json)与[acceptance](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/d79b7b1a012943dce867d1adcc29a45e0d7b79bf/docs/evidence/ragged-gqa-segments-20261024/service-final/acceptance.json)保留其边界。双方源码、SO、轮数及DB/KV不完全同条件，不直接算收益；#33/#36仍是局部探针，#37服务准确率仍待，#38仅调研，不当作新基线。

前序7596共同基点的两轮筛选继续保留：同KV546432与DB，4K+0.103%/+0.644%但无FULL覆盖，16K+4.728%/−0.493%；仅保留候选，不确认稳定收益，不把旧组合成绩赋给新main。
- **改动**：相关实现 [pr25-kv-current-pair.json](../../../analysis/pr25-kv-current-pair.json)；[result.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/result.json)；[archive-receipt.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds-control/archive-receipt.json)；[source-manifest.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/source-manifest.json)；[coverage.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/coverage.json)；[semantic-validation.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/model-path/semantic-validation.json)；[archive-receipt.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds/result.json)；[state.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/archive-receipt.json)；[coverage.json](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long-control/coverage.json)；[semantic-validation.json](../../../experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/model-path/semantic-validation.json)；[summary_20261025_001229.csv](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark_results/summary_20261025_001229.csv)；[state.json](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T171101Z-main0bf9-kv-official-four-rounds/result.json)；[audit.json](../../../experiments/framework/20261024T171101Z-main0bf9-kv-official-four-rounds-control/postfailure-cache-audit/audit.json)；[result.json](../../../experiments/framework/20261024T172742Z-main0bf9-kv-official-four-rounds/result.json)；[state.json](../../../experiments/framework/20261024T172742Z-main0bf9-kv-official-four-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T172742Z-main0bf9-kv-official-four-rounds-control/archive-receipt.json)；[evidence.json](../../../experiments/framework/20261024T172742Z-main0bf9-kv-official-four-rounds-control/failed-log-replay/model-path/evidence.json)；[raw_runs_20261025_014809.csv](../../../experiments/framework/20261024T174713Z-main0bf9-kv-official-four-rounds/benchmark_results/raw_runs_20261025_014809.csv)；[early-stop-decision.json](../../../experiments/framework/20261024T174713Z-main0bf9-kv-official-four-rounds-control/early-stop-decision.json)；[state.json](../../../experiments/framework/20261024T174713Z-main0bf9-kv-official-four-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T174713Z-main0bf9-kv-official-four-rounds-control/archive-receipt.json)；[results.json](../../../experiments/framework/20261024T183929Z-kv-staging-budget/results.json)；[state.json](../../../experiments/framework/20261024T183929Z-kv-staging-budget/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T183929Z-kv-staging-budget/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：4096/16384 / 1024 / 64 / 256/128 × 4。
- **结果**：官方两档各4轮、1536/0；第2–4轮4K5758.72/16K4045.20 tok/s，TTFT3626.85/124212.05ms；本实例该版本完整105仍待。
- **是否保留**：保留作当前性能对照基线；完整105仍待，不称最终合格基线，不跨队友条件算收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T161030Z-main0bf9-main-official-four-rounds",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T16:10:30Z",
  "profile_id": "pr25-kv-current",
  "phase": "official_four_rounds_baseline",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "4096/16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256/128 × 4",
  "profiler": "false",
  "status": "official_four_rounds_baseline_completed",
  "artifacts": "experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds",
  "conclusion": "本实例main0bf9官方四轮性能基线：4K/16K各4轮，1536成功0失败；按官方第2–4轮汇总5758.72/4045.20 total tok/s，平均TTFT3626.85/124212.05ms，全部首轮与原始CSV保留。源码main0bf9d2ef/tree8671e2ec、526文件、native SO14f4457a，KV547536、初始DBfb035397；17:11:01 UTC结束，source/native未变、原DB207f1b恢复。作为后续532候选的性能对照；本实例该版本完整105仍待，不称最终合格替代基线，不继承前序PR24准确率。队友PR31 e972997/SO271327a0为暖后单轮5766.41/4048.28及102/105、Draft标题且未合；源码、SO、轮数和DB/KV条件不完全相同，不跨条件算收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T161030Z-main0bf9-main-official-four-rounds](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark-command.json)；[command.txt](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261025_001229.csv](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark_results/raw_runs_20261025_001229.csv)；[summary_20261025_001229.csv](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark_results/summary_20261025_001229.csv)；[result.json](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
