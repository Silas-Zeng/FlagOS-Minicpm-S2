<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T183552Z-q-gqa-service-baseline-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #159 · Q-hoist + GQA 框架组合

- **尝试**：仅适配精确GQA包装的安装身份，保留两条算术路径与原服务参数；已获单pair正信号及独立101/105准确率通过，评测DB增长另列。
- **改动**：相关实现 [METHOD.md](../../../archive/ai/20261022-framework-kv/q-gqa-framework/METHOD.md)；[biv150_q_fragment_service.py](../../../archive/ai/20261022-framework-kv/q-gqa-framework/biv150_q_fragment_service.py)；[q-gqa-service-pair.json](../../../analysis/q-gqa-service-pair.json)；[accuracy-review.json](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/accuracy-review.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败
- **是否保留**：保留作GQA对照基线；组合单pair正信号与独立准确率另列。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T183552Z-q-gqa-service-baseline-context16k-long",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T18:35:54.114254+00:00",
  "profile_id": "q_gqa_framework",
  "phase": "real_service_baseline_context16k_long",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_baseline_matched_single_pair",
  "artifacts": "experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long",
  "conclusion": "原clean6f加队友PR12 cf1f448的exact GQA helper1a814及原footer，413源runnercc7f；原16K/1024out/32请求/c64，32成功0失败。耗时182.460600s、总吞吐3053.020761tok/s；与候选同KV521936、原SERVER/load/seed721201/driverbc51/benchmark0813/包/CPU配额，DB四端527表19702行三SHA一致。GQA原安装及FIRST_WIDTH有Engine记录，但它是startup/launch尝试而非逐步执行覆盖；本臂保持原PR12无观察器。保留单pair对照基线，不与旧clean6f跨轮叠算收益；组合accuracy正在独立运行。root逐460seal核验，退出0及后态空闲。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T183552Z-q-gqa-service-baseline-context16k-long](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-024018.json](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-024018.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
