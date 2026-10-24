<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T181134Z-async-bookkeeping-service-baseline-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #157 · 异步输出 CPU 批量记账

- **尝试**：将有效单 token 异步输出的逐行 CPU 数组更新合并，保留请求历史、事件与回退；服务对照的 KV 失配单列。
- **改动**：相关实现 [biv150_async_bookkeeping.py](../../../archive/ai/20261022-framework-kv/async-bookkeeping/biv150_async_bookkeeping.py)；[compare_service_pair.py](../../../archive/ai/20261022-framework-kv/async-bookkeeping/compare_service_pair.py)；[async-bookkeeping-service-pair.json](../../../analysis/async-bookkeeping-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：吞吐+0.058650%不认作收益；基线KV521840与候选521936不同，不能形成严格性能配对；非稳定或官方性能结论
- **是否保留**：保留作对照基线；KV失配，不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T181134Z-async-bookkeeping-service-baseline-decode4k",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T18:11:36.342189+00:00",
  "profile_id": "async_cpu_bookkeeping",
  "phase": "real_service_baseline_decode4k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_baseline_unmatched_kv",
  "artifacts": "experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k",
  "conclusion": "干净6f、原4K/128out/64并发64请求，64成功0失败；耗时38.996212260798s、吞吐6932.365590tok/s、TTFT20103.044362ms、TPOT134.312967ms。基线KV521840与候选521936不同，不能形成严格性能配对；候选表观吞吐+0.058650%不认作收益。保留作原始对照基线，DB四端527表19702行三SHA一致，原SERVER/load/seed/benchmark/driver相同，源仅候选runner+helper两路径变化。412源、457原件seal复用root验收，退出0及设备清理；非稳定或官方性能结论。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T181134Z-async-bookkeeping-service-baseline-decode4k](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261023-021332.json](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261023-021332.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
