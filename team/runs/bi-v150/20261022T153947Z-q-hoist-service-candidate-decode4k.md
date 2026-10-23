<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T153947Z-q-hoist-service-candidate-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #149 · Q fragment 循环外保留

- **尝试**：同一方法的KV16K/4K局部门与真实服务配对分别记录；保留单轮正信号，TTFT变化及准确率边界同时展示。
- **改动**：相关实现 [biv150_q_fragment_service.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py)；[compare_q_service_pair.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py)；[q-fragment-service-pair.json](../../../analysis/q-fragment-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：吞吐+1.711258%、wall缩短1.682467%、TTFT+1.318503%、TPOT-5.384107%；保留候选→基线一次配对的服务正信号，非稳定统计收益，不代表官方完整性能或模型准确率通过，TTFT本轮退化；不外推C500
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T153947Z-q-hoist-service-candidate-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T15:39:48.802464+00:00",
  "profile_id": "q_fragment_hoist",
  "phase": "real_service_candidate_decode4k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_positive_signal_pending_accuracy",
  "artifacts": "experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k",
  "conclusion": "同一Q fragment方法接入6f组合，helper77b489私有JIT仅exact ff64外提Q读，完整源仅runner+helper两路径变化。原decode-screen seed721201、4K输入/128输出/64并发64请求，64成功0失败；耗时38.338730307762s，total token吞吐7051.250728177380tok/s，TTFT20367.168871ms。Engine319325真实execute第37次N2/M2048首次marker增量42、累计168，仅证明该次命中，不代表全程或逐层覆盖；两份cold recipe均selected ff64，保原3D。KV521936；DB前后527表/19702行、物理/schema/逻辑三SHA相同，逻辑dd3c10ee。与154518干净6f配对，吞吐+1.711258%、wall缩短1.682467%、TTFT+1.318503%、TPOT-5.384107%；同args/load/seed、KV521936及DB四端三SHA一致，源只runner+helper两路径变化。保留候选→基线一次配对的服务正信号，非稳定统计收益，不代表官方完整性能或模型准确率通过，TTFT本轮退化；不外推C500。下一步准确率验证，不追加性能重复。root474项seal验收复用，退出0、端口双闭、设备68MiB/0%；复杂compile mock草稿未完成且未执行。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T153947Z-q-hoist-service-candidate-decode4k](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-234145.json](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-234145.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T153947Z-q-hoist-service-candidate-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
