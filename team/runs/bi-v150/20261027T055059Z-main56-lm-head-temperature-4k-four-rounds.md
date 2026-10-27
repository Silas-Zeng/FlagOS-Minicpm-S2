<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T055059Z-main56-lm-head-temperature-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #362 · LM-head温度epilogue融合

- **尝试**：组件完整head+Sampler Event省17.31%；生产同main56/native14f/DB/KV原官方4K本组暖均5921.12对5902.77 tok/s，观察+0.3109%。保留小收益信号，尚待16K/105，不把局部组件收益迁移为模型结论。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方4轮弃首；同main56/native14f/DB/KV，CSV对比见原件。
- **结果**：head温度epilogue原官方4K暖均5921.12对A5902.77 tok/s，本组+0.3109%；同KV/native/DB，1024请求及实际启用/清理通过。保留小信号，待16K/105。
- **是否保留**：保留单组4K小收益，待16K和105；非稳定净收益结论。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T055059Z-main56-lm-head-temperature-4k-four-rounds",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T05:50:59+00:00",
  "profile_id": "lm-head-temperature",
  "phase": "official_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "lm_head_temperature_4k_positive_observation",
  "artifacts": "experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds",
  "conclusion": "LM-head温度epilogue生产候选809文件/5差分，main56/native14f/原初始DB/KV548432与本次A一致。原官方4K四轮[5081.15, 5778.04, 5988.09, 5997.24] tok/s，弃首暖均5921.123333对A 5902.770000，本组观察+0.3109%；1024请求SUCCESS，实际READY/SELECTED/SAMPLED、原stack/provider、source/native不变、DB恢复与清理通过。首回执不证明命中占比；仅保留单组小收益，待16K/105，不能把请求成功当模型准确率。CSV TPOT/TTFT/耗时对比见comparison.json，不外推组件收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T055059Z-main56-lm-head-temperature-4k-four-rounds](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261027_135310.csv](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/benchmark_results/raw_runs_20261027_135310.csv)；[summary_20261027_135310.csv](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/benchmark_results/summary_20261027_135310.csv)；[result.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
