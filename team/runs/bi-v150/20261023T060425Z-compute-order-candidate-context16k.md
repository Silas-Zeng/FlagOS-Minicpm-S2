<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T060425Z-compute-order-candidate-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #188 · 计算顺序与采样顺序分离

- **尝试**：计算行重排以适配Attention路径，采样保持原请求顺序。当前适配队友normalized main328，仅改runner/helper两文件；代码4fca58ba/tree5c77。140324→141159短测表观约+6.59%，但KV521840→521936，gain=null。142019完整105题103正确（98.0952%）通过，但P分支0命中。144620原官方8轮全部成功，1536请求；原第2–4轮均值4K5116.68、16K3436.04 total tok/s，实际P N62/M2048/outside59。保留Draft方法候选：这是绝对性能，不能归因单项收益，也不能用吞吐命中弥补准确率P0。旧423的单pair+5.124857%、三题质量、结构映射与独立参考证据保留，不能替代新组合结果。
- **改动**：相关实现 [compute-order-current-main-official.json](../../../analysis/compute-order-current-main-official.json)；[compute-order-current-main-accuracy.json](../../../analysis/compute-order-current-main-accuracy.json)；[compute-order-current-main-pair.json](../../../analysis/compute-order-current-main-pair.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-main-profile/README.md)；[compute-order-math4-event-130351.json](../../../analysis/compute-order-math4-event-130351.json)；[compute-order-math4-event-125330.json](../../../analysis/compute-order-math4-event-125330.json)；[compute-order-service-retest-pair.json](../../../analysis/compute-order-service-retest-pair.json)；[compute-order-math4-summary.json](../../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../../analysis/compute-order-first-layer.json)；[result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：吞吐表观+4.7989%、耗时表观减少4.5792%；KV容量不同（基线521936、候选521840），31门仅same_KV false、gain=null，不能归因收益；061500准确率pending，不继承422结果
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T060425Z-compute-order-candidate-context16k",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T06:04:25+00:00",
  "profile_id": "compute_order",
  "phase": "candidate_context16k_short_output",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "confounded_no_performance_conclusion",
  "artifacts": "experiments/framework/20261023T060425Z-compute-order-candidate-context16k",
  "conclusion": "32成功0失败、exit0；99.536272152s、5308.456792453 total tok/s。相对054306基线104.312939462s/5065.373507102，吞吐表观+4.7989%、耗时表观减少4.5792%。KV容量不同（基线521936、候选521840），31门仅same_KV false、gain=null，不能归因收益；四端DB554表/20517行三hash一致。423仅四路径改动，Engine2350实际FIRST_SELECTED为N17/M2048/Dprefix1/Dall15/outside14/sampler_rows17，原forward返回、NONE，无SCOPE_REJECTED；标记不代表采样完成或数值等价。root已核484原件，不重跑reader；保留候选与失配记录，默认版本暂不采用。061500准确率pending，不继承422结果；单pair不证明稳定收益，不重启凑KV。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T060425Z-compute-order-candidate-context16k](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261023-140723.json](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261023-140723.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261023T060425Z-compute-order-candidate-context16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
