<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T170831Z-main0915-prefill-stride-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #284 · Prefill stride常量特化

- **尝试**：检查stride常量特化的局部资源改善能否转为原官方吞吐。
- **改动**：仅旧main0915的normalized stride及Q-fragment/compute-order精确依赖闭合；实际603/tree1127346e，不混新main34942或PR51。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-stride.md)。
- **怎么测**：旧main0915/603/tree1127346e、native14f；原0813/RUNS4/SKIP_FIRST1，4K/16K各四轮，逐档弃首轮；日志/CSV及真实prefill、Q-fragment和compute-order激活保存。
- **结果**：原官方两档各4轮、1536成功，实际激活闭合；弃首轮5726.63/4052.78 tok/s，TTFT3637.47/124103.35ms。
- **是否保留**：相对旧完整参考观察−0.56%/+0.19%，KV不同不判因果；保留小信号，不合并、不升基线、不继承105资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T170831Z-main0915-prefill-stride-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-25T17:08:31+00:00",
  "profile_id": "prefill-stride",
  "phase": "Prefill stride原官方对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0915f01d5efc2b31af65182ddb87e2d2f62bab0c",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_stride_official_mixed_signal",
  "artifacts": "experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds",
  "conclusion": "团队旧main0915完整603/tree1127346e，只有normalized prefill的11项stride常量特化及Q-fragment/compute-order依赖闭合，native14f不变。原官方4K四轮5029.22/5744.70/5674.34/5760.86，16K3554.80/4052.99/4052.64/4052.71 tok/s；分别弃首轮均5726.633/4052.78，TTFT3637.47/124103.35ms，8轮1536 SUCCESS。实际prefill/Graph/Q-fragment/compute-order激活通过；18:08:51 completed=true，source/native/DB恢复及所属进程清理通过，原stage=running保留。相对旧完整参考5758.72/4045.20仅观察约-0.56%/+0.19%；KV547648对547536且非完全同条件，非严格因果，长输入只保留微小信号，无确认净收益、不合并、不授105资格或新比赛基线。不是已合PR51的新main34942的成绩。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T170831Z-main0915-prefill-stride-four-rounds](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_011033.csv](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/benchmark_results/raw_runs_20261026_011033.csv)；[summary_20261026_011033.csv](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/benchmark_results/summary_20261026_011033.csv)；[result.json](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
