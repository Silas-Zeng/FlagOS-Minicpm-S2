<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T121541Z-compute-order-candidate-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #200 · 计算顺序与采样顺序分离

- **尝试**：将计算行重排以适配现有Attention路径，采样仍按原请求顺序。120949→121541原短负载对照31项可比门全过，同KV521936及DB561/20721，吞吐5056.65→5315.79 tok/s（+5.124857%）；两侧32/0且候选实际命中，仅单pair正信号。130351事件质量诊断原四题4/4正确，index0/1/2三题在token index94实际outside、首完整boxed前，index3位于row0未覆盖；背景32/0，DB561/20721→565/20919。仅4题诊断，不计性能、105题或稳定收益；保留候选，可推进独立Draft PR，仍不自动集成。100604结构接线及085500单行参考分别保留；061500完整准确率101/105和104132四题4/4均未覆盖新路径，125330另为发送前客户端长度校验失败，不是优化负结果。旧KV失配、负结果和未覆盖证据均保留，不调容差。
- **改动**：相关实现 [compute-order-math4-event-130351.json](../../../analysis/compute-order-math4-event-130351.json)；[compute-order-math4-event-125330.json](../../../analysis/compute-order-math4-event-125330.json)；[compute-order-service-retest-pair.json](../../../analysis/compute-order-service-retest-pair.json)；[compute-order-math4-summary.json](../../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../../analysis/compute-order-first-layer.json)；[result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
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
