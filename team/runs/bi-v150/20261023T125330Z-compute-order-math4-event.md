<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T125330Z-compute-order-math4-event

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #201 · 计算顺序与采样顺序分离

- **尝试**：将计算行重排以适配现有Attention路径，采样仍按原请求顺序。120949→121541原短负载对照31项可比门全过，同KV521936及DB561/20721，吞吐5056.65→5315.79 tok/s（+5.124857%）；两侧32/0且候选实际命中，仅单pair正信号。130351事件质量诊断原四题4/4正确，index0/1/2三题在token index94实际outside、首完整boxed前，index3位于row0未覆盖；背景32/0，DB561/20721→565/20919。仅4题诊断，不计性能、105题或稳定收益；保留候选，可推进独立Draft PR，仍不自动集成。100604结构接线及085500单行参考分别保留；061500完整准确率101/105和104132四题4/4均未覆盖新路径，125330另为发送前客户端长度校验失败，不是优化负结果。旧KV失配、负结果和未覆盖证据均保留，不调容差。
- **改动**：相关实现 [compute-order-math4-event-130351.json](../../../analysis/compute-order-math4-event-130351.json)；[compute-order-math4-event-125330.json](../../../analysis/compute-order-math4-event-125330.json)；[compute-order-service-retest-pair.json](../../../analysis/compute-order-service-retest-pair.json)；[compute-order-math4-summary.json](../../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../../analysis/compute-order-first-layer.json)；[result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：mixed / 128/32768 / 64/8 / 36。
- **结果**：客户端长度校验在发送前失败；背景0发送、四题未放行，本轮未评价优化。
- **是否保留**：保留客户端失败与修复证据；本轮未评价优化。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T125330Z-compute-order-math4-event",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T12:53:31.497732+00:00",
  "profile_id": "compute_order",
  "phase": "fixed_math4_event_client_validation",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "mixed",
  "output_len": "128/32768",
  "concurrency": "64/8",
  "num_prompts": "36",
  "profiler": "false",
  "status": "client_validation_failed_before_requests",
  "artifacts": "experiments/framework/20261023T125330Z-compute-order-math4-event",
  "conclusion": "客户端新增prompt_len==16384误拒原benchmark扣special后的16383，在发送前exit1；背景original_requests=0/entered=0，Math4仅ready4、未go，目标outside与题目质量均未评估，不是优化负结果。原425源码与五PID/两客户端组清理通过，489原件+seal共490已回收；DB561/20721三hash不变、68MiB/0、9031双栈关闭。修正客户端另run130351在途，保留原失败，不计性能/准确率。详analysis/compute-order-math4-event-125330.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T125330Z-compute-order-math4-event](../../../experiments/framework/20261023T125330Z-compute-order-math4-event)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T125330Z-compute-order-math4-event/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T125330Z-compute-order-math4-event/launch-command.json)；[command.txt](../../../experiments/framework/20261023T125330Z-compute-order-math4-event-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T125330Z-compute-order-math4-event/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T125330Z-compute-order-math4-event/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T125330Z-compute-order-math4-event-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T125330Z-compute-order-math4-event-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T125330Z-compute-order-math4-event/server.log)；[gpu.csv](../../../experiments/framework/20261023T125330Z-compute-order-math4-event/gpu.csv)；[exit-code](../../../experiments/framework/20261023T125330Z-compute-order-math4-event/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
