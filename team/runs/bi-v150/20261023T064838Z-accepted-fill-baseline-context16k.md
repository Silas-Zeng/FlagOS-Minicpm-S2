<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T064838Z-accepted-fill-baseline-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #190 · 省去无消费者的 accepted GPU fill

- **尝试**：固定非推测Full路径保留CPU fill，省略无消费者的accepted-count GPU fill。064838→065325两侧32成功0失败，吞吐表观−0.235046%，但KV521840→521936不同，31门仅same_KV失败、gain=null；当前不集成，保留小负及失配证据。冷ENABLED后同Engine原CPU_METADATA_FIRST_SELECTED只证明首次prepare，不证明全程/GPU数值或新准确率。
- **改动**：相关实现 [accepted-fill-service-pair.json](../../../analysis/accepted-fill-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：32成功0失败、exit0，104.147864725s、5073.402142188 total tok/s；与065325候选四端DB三SHA相同，但KV521840→521936不同，31门仅same_KV失败、gain=null
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T064838Z-accepted-fill-baseline-context16k",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T06:48:39.672961+00:00",
  "profile_id": "accepted_fill_baseline",
  "phase": "baseline_context16k_short_output",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "baseline_complete_kv_confounded",
  "artifacts": "experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k",
  "conclusion": "原422基线，32成功0失败、exit0，104.147864725s、5073.402142188 total tok/s；root已核560原件。原bc51/SERVER/context16K128/c64/32请求/seed721201，DB558表20651行前后不变。与065325候选四端DB三SHA相同，但KV521840→521936不同，31门仅same_KV失败、gain=null；保留为本次基线，不归因候选收益。详analysis/accepted-fill-service-pair.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T064838Z-accepted-fill-baseline-context16k](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261023-145141.json](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261023-145141.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261023T064838Z-accepted-fill-baseline-context16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
