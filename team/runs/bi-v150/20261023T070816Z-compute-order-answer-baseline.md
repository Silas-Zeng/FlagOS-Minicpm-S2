<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T070816Z-compute-order-answer-baseline

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #192 · 计算顺序与采样顺序分离

- **尝试**：计算顺序与采样顺序分离：100604完整token逆排列、logits索引与原sample单次衔接通过；104132固定四题原judge4/4，但题目P outside覆盖0/4，记未覆盖，不改题/时序重试。085500单行独立参考下P/GQA更接近FP32，不能据单层或0P准确率证明新路径全模型正确。候选保留暂不集成，诊断段先收口，主线回到实际GPU热点。此前短筛表观+4.7989%受KV失配影响、gain=null；061500完整准确率101/105通过却未命中新路径；负结果一并保留，不调容差。
- **改动**：相关实现 [compute-order-math4-summary.json](../../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../../analysis/compute-order-first-layer.json)；[result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：失败
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T070816Z-compute-order-answer-baseline",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T07:08:17.256099+00:00",
  "profile_id": "compute_order",
  "phase": "auxiliary_answer_baseline",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "inconclusive_auxiliary_baseline_failed",
  "artifacts": "experiments/framework/20261023T070816Z-compute-order-answer-baseline",
  "conclusion": "原422辅助答案基线：32请求均成功、实际长度均16K/128，仅4/32符合首个answer标签真值，原owner exit1；因此提示门无判别力，停止423候选侧，不归因优化失败。无COMPUTE_ORDER命中；不作官方准确率/性能。578原件逐SHA导入，DB558/20651三hash前后相同，最后68MiB/0、9031双栈关闭。保留原请求、响应、失败和源代码；不改原exit1，不重试提示凑通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T070816Z-compute-order-answer-baseline](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/launch-command.json)；[command.txt](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/server.log)；[gpu.csv](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/gpu.csv)；[exit-code](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
