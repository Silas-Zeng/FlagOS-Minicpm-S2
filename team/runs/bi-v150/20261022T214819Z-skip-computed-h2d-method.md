<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T214819Z-skip-computed-h2d-method

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #174 · 省去无消费者的 computed H2D

- **尝试**：CPU metadata成功时省略一次计数GPU副本提交，保留原回退和固定buffer/event；方法门与独立短服务单pair分别记录，不与KV组合收益相加。
- **改动**：相关实现 [pr15-computed-h2d-accuracy.json](../../../analysis/pr15-computed-h2d-accuracy.json)；[skip-computed-h2d-service-pair.json](../../../analysis/skip-computed-h2d-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：event/fixed graph消费者及RNG通过
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T214819Z-skip-computed-h2d-method",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T21:48:19+00:00",
  "profile_id": "skip_computed_h2d",
  "phase": "method_correctness",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "passed_actual_method_graph_fallback_no_model_accuracy",
  "artifacts": "experiments/framework/20261022T214819Z-skip-computed-h2d-method",
  "conclusion": "CPU metadata成功时跳过computed计数GPU副本；原runner只三小段变化cc442→97f41，helper拒绝仍先走原copy。固定461676方法门5cases、毒值、真实helper回退、连续4步event/fixed graph消费者及RNG通过；28原件全核。32call ABBA含drain局部median0.8119181875→0.792378703125ms仅描述，不是模型accuracy或端到端收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T214819Z-skip-computed-h2d-method](../../../experiments/framework/20261022T214819Z-skip-computed-h2d-method)
- 原命令：[command.txt](../../../experiments/framework/20261022T214819Z-skip-computed-h2d-method-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T214819Z-skip-computed-h2d-method-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T214819Z-skip-computed-h2d-method/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T214819Z-skip-computed-h2d-method/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T214819Z-skip-computed-h2d-method/worker.log)；[gpu.csv](../../../experiments/framework/20261022T214819Z-skip-computed-h2d-method/gpu.csv)；[exit-code](../../../experiments/framework/20261022T214819Z-skip-computed-h2d-method/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
