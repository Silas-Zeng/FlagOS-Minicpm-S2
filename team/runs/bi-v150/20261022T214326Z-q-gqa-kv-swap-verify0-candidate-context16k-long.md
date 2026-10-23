<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #173 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：吞吐+0.846849%、时长−0.839738%、TTFT+0.043841%、TPOT−1.438678%；保留单次正信号，未证明稳定收益或新accuracy
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T21:43:26+00:00",
  "profile_id": "q_gqa_kv_swap",
  "phase": "current_combination_verify0_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "comparable_single_pair_positive_signal_retained",
  "artifacts": "experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long",
  "conclusion": "当前QGQA+KV保存恢复单pair吞吐+0.846849%、时长−0.839738%、TTFT+0.043841%、TPOT−1.438678%；保留单次正信号，未证明稳定收益或新accuracy。本侧candidate为168.399855358s/3307.936332935 total tok/s、32成功0失败。30项门全过，同KV521936、DB540/20112四端三SHA及原bc51/参数/seed；完整414→422只init+8旧KV文件。候选VERIFY0真实SAVE/FULL/DROP、R16704/1044页/718405632B、consumer8、0回读。root核563原件，详analysis/q-gqa-kv-swap-verify0-pair.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-054733.json](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-054733.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T214326Z-q-gqa-kv-swap-verify0-candidate-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
