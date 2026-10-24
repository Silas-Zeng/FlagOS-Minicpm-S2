<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T121541Z-compute-order-candidate-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #200 · 计算顺序与采样顺序分离

- **尝试**：计算行重排以适配Attention路径，采样保持原请求顺序。PR15+PR21兼容组合已由PR22合入；142019完整105题102正确（97.1429%）通过，173454原官方8轮全部成功，第2–4轮均值4K5118.99、16K3436.17 total tok/s。该组合的官方16K KV为521936；这是组合绝对结果，不作两个方法的单项因果拆分。旧423短测、三题质量、结构映射与独立参考证据保留，不能替代新组合结果。
- **改动**：相关实现 [compute-order-current-main-official.json](../../../analysis/compute-order-current-main-official.json)；[compute-order-current-main-accuracy.json](../../../analysis/compute-order-current-main-accuracy.json)；[compute-order-current-main-pair.json](../../../analysis/compute-order-current-main-pair.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-main-profile/README.md)；[compute-order-math4-event-130351.json](../../../analysis/compute-order-math4-event-130351.json)；[compute-order-math4-event-125330.json](../../../analysis/compute-order-math4-event-125330.json)；[compute-order-service-retest-pair.json](../../../analysis/compute-order-service-retest-pair.json)；[compute-order-math4-summary.json](../../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../../analysis/compute-order-first-layer.json)；[result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：吞吐变化+5.124857%
- **是否保留**：保留单pair正信号；稳定收益与目标路径质量尚待确认，暂不集成。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T121541Z-compute-order-candidate-context16k",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T12:15:43.388748+00:00",
  "profile_id": "compute_order",
  "phase": "candidate_context16k_same_capacity_retest",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "comparable_single_pair",
  "artifacts": "experiments/framework/20261023T121541Z-compute-order-candidate-context16k",
  "conclusion": "原423计算顺序候选，原bc51/SERVER/context-screen/seed721201；32成功0失败、99.398900815s、5315.793189548 total tok/s、KV521936；484原件已核/485导入，源码与清理后态保留。31项可比门全通过，本轮吞吐变化+5.124857%。单pair不能证明稳定收益；实际P命中不等于新路径准确率通过，候选保留不集成，不改容量参数或循环重启。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T121541Z-compute-order-candidate-context16k](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261023-201843.json](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261023-201843.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261023T121541Z-compute-order-candidate-context16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
