<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T181739Z-bq16-chunk-chain-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #158 · BQ16 chunk 形状对齐

- **尝试**：复用现有 C2/C3 与原算子，比较七段恢复链的 chunk 形状；局部正信号保留，未实现调度器或接入服务。
- **改动**：相关实现 [validate_bq16_chunk_chain.py](../../../archive/ai/20261022-framework-kv/bq16-chunk-alignment/validate_bq16_chunk_chain.py)；[result-review.json](../../../archive/ai/20261022-framework-kv/bq16-chunk-alignment/result-review.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall60.169030→60.023055ms（缩短0.242608%），event60.029037→59.888794ms（缩短0.233626%），4窗cgroup throttle均0；decode起始KV16384为构造值，不外推端到端、准确率、C500或稳定统计收益
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T181739Z-bq16-chunk-chain-gate",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T18:17:40.100611+00:00",
  "profile_id": "bq16_chunk_alignment",
  "phase": "actual_layer_seven_chunk_chain_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_positive_signal_not_service",
  "artifacts": "experiments/framework/20261022T181739Z-bq16-chunk-chain-gate",
  "conclusion": "原C2/C3和原算子的D29七段合成恢复链，目标绝对tokens2944→16704；chunk从2019×6+1646改为2016×6+1664，不改scheduler或算子实现。25项strict bits/KV/RNG/新指针/非默认流/scale全过，target误差0。32chain每窗ABBA wall60.169030→60.023055ms（缩短0.242608%），event60.029037→59.888794ms（缩短0.233626%），4窗cgroup throttle均0。局部正信号保留，暂停scheduler实现且不接服务；root按实际全轮暴露量估算仅约0.003–0.004%的条件量级，非实测服务收益或严格上限。计时含builder/writer/forward，未含打包/分配/slot构造及GEMM/模型/采样；decode起始KV16384为构造值，不外推端到端、准确率、C500或稳定统计收益。32原件seal复用root验收，退出0及设备清理。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T181739Z-bq16-chunk-chain-gate](../../../experiments/framework/20261022T181739Z-bq16-chunk-chain-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T181739Z-bq16-chunk-chain-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T181739Z-bq16-chunk-chain-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T181739Z-bq16-chunk-chain-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T181739Z-bq16-chunk-chain-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T181739Z-bq16-chunk-chain-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T181739Z-bq16-chunk-chain-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T181739Z-bq16-chunk-chain-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
