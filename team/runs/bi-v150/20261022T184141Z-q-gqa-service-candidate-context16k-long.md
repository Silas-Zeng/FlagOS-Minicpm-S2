<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T184141Z-q-gqa-service-candidate-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #160 · Q-hoist + GQA 框架组合

- **尝试**：仅适配精确GQA包装的安装身份，保留两条算术路径与原服务参数；已获单pair正信号及独立101/105准确率通过，评测DB增长另列。
- **改动**：相关实现 [METHOD.md](../../../archive/ai/20261022-framework-kv/q-gqa-framework/METHOD.md)；[biv150_q_fragment_service.py](../../../archive/ai/20261022-framework-kv/q-gqa-framework/biv150_q_fragment_service.py)；[q-gqa-service-pair.json](../../../analysis/q-gqa-service-pair.json)；[accuracy-review.json](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/accuracy-review.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：吞吐+7.466632%、wall省6.947861%、TTFT−9.416976%、TPOT−6.786409%；单pair正信号保留，非稳定统计或完整官方性能，组合accuracy pending不继承单项
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T184141Z-q-gqa-service-candidate-context16k-long",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T18:41:42.751299+00:00",
  "profile_id": "q_gqa_framework",
  "phase": "real_service_candidate_context16k_long",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_service_positive_signal_accuracy_pending",
  "artifacts": "experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long",
  "conclusion": "只对Q安装身份守卫兼容exact GQA wrapper，保C2→C3→GQA→ctorQ及两operator算术；414源runnercc442、Qhelper51fc。原16K/1024out/32请求/c64，32成功0失败，耗时169.783491s、总吞吐3280.978592tok/s；相对GQA基线单pair吞吐+7.466632%、wall省6.947861%、TTFT−9.416976%、TPOT−6.786409%。Engine339894同一次execute43 N2/M2048原返回后Q/GQA各增42，证据齐后撤观察；不代表全程或graph replay覆盖/GPU完成。KV521936、DB四端527表19702行三SHA/原参数环境均同，21项可比门通过；单pair正信号保留，非稳定统计或完整官方性能，组合accuracy pending不继承单项。root逐478seal核验，退出0及后态空闲。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T184141Z-q-gqa-service-candidate-context16k-long](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-024553.json](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-024553.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
