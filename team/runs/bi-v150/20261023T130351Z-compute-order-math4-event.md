<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T130351Z-compute-order-math4-event

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #202 · 计算顺序与采样顺序分离

- **尝试**：将计算行重排以适配现有Attention路径，采样仍按原请求顺序。120949→121541原短负载对照31项可比门全过，同KV521936及DB561/20721，吞吐5056.65→5315.79 tok/s（+5.124857%）；两侧32/0且候选实际命中，仅单pair正信号。130351事件质量诊断原四题4/4正确，index0/1/2三题在token index94实际outside、首完整boxed前，index3位于row0未覆盖；背景32/0，DB561/20721→565/20919。仅4题诊断，不计性能、105题或稳定收益；保留候选，可推进独立Draft PR，仍不自动集成。100604结构接线及085500单行参考分别保留；061500完整准确率101/105和104132四题4/4均未覆盖新路径，125330另为发送前客户端长度校验失败，不是优化负结果。旧KV失配、负结果和未覆盖证据均保留，不调容差。
- **改动**：相关实现 [compute-order-math4-event-130351.json](../../../analysis/compute-order-math4-event-130351.json)；[compute-order-math4-event-125330.json](../../../analysis/compute-order-math4-event-125330.json)；[compute-order-service-retest-pair.json](../../../analysis/compute-order-service-retest-pair.json)；[compute-order-math4-summary.json](../../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../../analysis/compute-order-first-layer.json)；[result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：mixed / 128/32768 / 64/8 / 36。
- **结果**：原四题4/4正确，3题实际覆盖且在首完整答案框前；背景32/0。仅小样本诊断，不计性能或完整准确率。
- **是否保留**：保留小样本质量信号及候选，可准备独立Draft PR；暂不集成。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T130351Z-compute-order-math4-event",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T13:03:52.887994+00:00",
  "profile_id": "compute_order",
  "phase": "fixed_math4_event_answer_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "mixed",
  "output_len": "128/32768",
  "concurrency": "64/8",
  "num_prompts": "36",
  "profiler": "false",
  "status": "limited_math4_quality_signal_three_outside_questions",
  "artifacts": "experiments/framework/20261023T130351Z-compute-order-math4-event",
  "conclusion": "固定原Level3 index0..3原judge4/4正确，背景32/0；index0/1/2三题在输出token0基索引94实际outside且首完整boxed前，总长1123/744/1651；index3原row0未覆盖、总733。Engine18855实际N5/outside3并关联同一次原sample。仅有限质量诊断，不计性能/105题或稳定收益；保留候选，可推进独立Draft PR，仍不自动集成。531原件+seal共532已回收，425源码/清理通过；DB561/20721→565/20919如实保留。125330客户端失败不评价优化。详analysis/compute-order-math4-event-130351.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T130351Z-compute-order-math4-event](../../../experiments/framework/20261023T130351Z-compute-order-math4-event)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T130351Z-compute-order-math4-event/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T130351Z-compute-order-math4-event/launch-command.json)；[command.txt](../../../experiments/framework/20261023T130351Z-compute-order-math4-event-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T130351Z-compute-order-math4-event/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T130351Z-compute-order-math4-event/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T130351Z-compute-order-math4-event-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T130351Z-compute-order-math4-event-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T130351Z-compute-order-math4-event/server.log)；[gpu.csv](../../../experiments/framework/20261023T130351Z-compute-order-math4-event/gpu.csv)；[exit-code](../../../experiments/framework/20261023T130351Z-compute-order-math4-event/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
