<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T154518Z-cpu-combination-combined-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #150 · Q fragment 循环外保留

- **尝试**：把唯一BF16 prefill Attention的Q local_load移到唯一K循环外并保持fragment活跃。默认由提交代码启用，保留normal fallback与精确源码/ABI/IR检查；PR23已合入main。官方1536请求、两档各4轮验证中4K/16K为5313.59/3764.67 total tok/s，较PR15+PR21旧基线+3.80%/+9.56%；完整Math500 L3为100/105通过。实际选中且fallback0，shared65536→32768、循环内Q read0。DB种子相同但KV521840对521936，不包装为严格等KV单项因果。
- **改动**：相关实现 [qfragment-pr15-pr21-final.json](../../../analysis/qfragment-pr15-pr21-final.json)；[qfragment-adaptation.json](../../../analysis/qfragment-adaptation.json)；[biv150_q_fragment_service.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py)；[compare_q_service_pair.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py)；[q-fragment-service-pair.json](../../../analysis/q-fragment-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：吞吐+1.711258%、wall缩短1.682467%，TTFT+1.318503%、TPOT−5.384107%，非稳定统计或官方/准确率结论
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T154518Z-cpu-combination-combined-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T15:45:19.629205+00:00",
  "profile_id": "q_fragment_hoist_baseline",
  "phase": "matched_service_baseline_decode4k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_baseline",
  "artifacts": "experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k",
  "conclusion": "干净6f组合作为Q fragment服务配对基线；原decode-screen seed721201、4K输入/128输出/64并发64请求，64成功0失败。耗时38.994805017952s、total token吞吐6932.615764472896tok/s、TTFT20102.121702ms。KV521936；与153947候选DB四端527表/19702行、物理/schema/逻辑三SHA相同；同args/load/seed，源仅runner+Q helper两路径差异。保留作配对基线，不单独计方法收益；候选吞吐+1.711258%、wall缩短1.682467%，TTFT+1.318503%、TPOT−5.384107%，非稳定统计或官方/准确率结论。root451项seal验收复用，退出0、端口双闭、设备68MiB/0%。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T154518Z-cpu-combination-combined-decode4k](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-234712.json](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-234712.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T154518Z-cpu-combination-combined-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
