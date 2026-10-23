<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T060425Z-compute-order-candidate-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #188 · 计算顺序与采样顺序分离

- **尝试**：075210自然混合shadow诊断出现原序/P logits大差：最大绝对差11.828125，top1仅12/17行一致；finite和采样前RNG相同不代表数值门通过。32成功0失败只说明服务结束，不计性能；当前不集成，停止性能大测，CPU定位诊断与候选根因。原0/1/16行bitexact、14个outside q1行全差只是线索。此前短筛表观+4.7989%受KV失配影响、gain=null；061500准确率101/105虽通过却未命中新排列路径，不能证明该路径正确，也不与旧422的103/105作升降统计。070816辅助答案基线仅4/32符合预设答案，提示门无判别力，候选侧未运行，不归因优化失败。
- **改动**：相关实现 [result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
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
