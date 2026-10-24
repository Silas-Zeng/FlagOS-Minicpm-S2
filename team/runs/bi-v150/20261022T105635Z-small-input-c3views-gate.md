<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T105635Z-small-input-c3views-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #129 · C3重复视图清理

- **尝试**：复用mixed Attention中的视图，减少重复slice/unbind；短输入信号与大输入、真实服务结果分别记录。
- **改动**：相关实现 [biv150_c3_view_reuse.py](../../../patches/framework/candidates/biv150_c3_view_reuse.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall从0.460218219到0.432736688ms，耗时降低5.9714%；仅单层短形状信号，不外推整体吞吐或整模型accuracy
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T105635Z-small-input-c3views-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T10:56:35.240823+00:00",
  "profile_id": "c3_view_reuse_small",
  "phase": "actual_layer_c3_view_small_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_correctness_positive_signal",
  "artifacts": "experiments/framework/20261022T105635Z-small-input-c3views-gate",
  "conclusion": "D29/P128/KV1024新增短形状真实selected68，正确性/新指针/非默认流/KV/RNG/scale门通过。32次ABBA：wall从0.460218219到0.432736688ms，耗时降低5.9714%；event降低0.6663%，提交CPU中位13.267037到12.2902745ms/32次，降低7.3623%。保留作候选，下一步真实服务对照；仅单层短形状信号，不外推整体吞吐或整模型accuracy。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T105635Z-small-input-c3views-gate](../../../experiments/framework/20261022T105635Z-small-input-c3views-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T105635Z-small-input-c3views-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T105635Z-small-input-c3views-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T105635Z-small-input-c3views-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T105635Z-small-input-c3views-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T105635Z-small-input-c3views-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T105635Z-small-input-c3views-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T105635Z-small-input-c3views-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
