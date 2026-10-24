<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T065325Z-accepted-fill-candidate-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #191 · 省去无消费者的 accepted GPU fill

- **尝试**：固定非推测Full路径保留CPU fill，省略无消费者的accepted-count GPU fill。064838→065325两侧32成功0失败，吞吐表观−0.235046%，但KV521840→521936不同，31门仅same_KV失败、gain=null；当前不集成，保留小负及失配证据。冷ENABLED后同Engine原CPU_METADATA_FIRST_SELECTED只证明首次prepare，不证明全程/GPU数值或新准确率。
- **改动**：相关实现 [accepted-fill-service-pair.json](../../../analysis/accepted-fill-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：吞吐表观−0.235046%、耗时表观增加0.235600%；KV521840→521936不同，31门仅same_KV失败、gain=null，不归因收益；不继承422准确率，保留代码与小负/失配证据
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T065325Z-accepted-fill-candidate-context16k",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T06:53:26.559674+00:00",
  "profile_id": "accepted_fill",
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
  "artifacts": "experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k",
  "conclusion": "仅422→422三路径省无消费者accepted GPU fill，32成功0失败、exit0，104.393237165s、5061.477298227 total tok/s；root已核482原件。吞吐表观−0.235046%、耗时表观增加0.235600%；KV521840→521936不同，31门仅same_KV失败、gain=null，不归因收益。DB558表20651行四端三SHA相同；Engine6346冷ENABLED后原CPU_METADATA_FIRST_SELECTED，同Engine且顺序成立，仅证明首次prepare经过该处，不证明全程/GPU数值。当前不集成，不追加大测/准确率或代码PR；不继承422准确率，保留代码与小负/失配证据。详analysis/accepted-fill-service-pair.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T065325Z-accepted-fill-candidate-context16k](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261023-145628.json](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261023-145628.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261023T065325Z-accepted-fill-candidate-context16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
