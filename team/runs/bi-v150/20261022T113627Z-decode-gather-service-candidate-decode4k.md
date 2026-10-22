<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T113627Z-decode-gather-service-candidate-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #134 · 纯decode CPU gather跳过

- **尝试**：严格纯decode省略无消费者的CPU输入整理；正确性门通过，当前服务候选负收益，不集成。
- **改动**：相关实现 [biv150_decode_cpu_gather.py](../../../archive/ai/20261022-next-service-queue/next-decode-gather/biv150_decode_cpu_gather.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：吞吐-0.79831%，TTFT20339.6547ms
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T113627Z-decode-gather-service-candidate-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T11:36:29.383148+00:00",
  "profile_id": "decode_cpu_gather_service",
  "phase": "actual_service_comparison",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_no_service_gain",
  "artifacts": "experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k",
  "conclusion": "严格纯decode无用CPU gather跳过，实际EngineCore297896多请求步骤命中，64成功0失败。39.285442093s、6881.3276776 tok/s，较112548吞吐-0.79831%，TTFT20339.6547ms；同KV521840、同DB前后527表19608行、仅runner+helper差异。当前实现不集成，保留方法正确性门与负结果；停止CPU细项扩展，转当前GPU热点。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T113627Z-decode-gather-service-candidate-decode4k](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-193826.json](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-193826.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T113627Z-decode-gather-service-candidate-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
