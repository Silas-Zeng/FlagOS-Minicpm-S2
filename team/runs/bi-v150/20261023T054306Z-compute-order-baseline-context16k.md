<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T054306Z-compute-order-baseline-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #187 · 计算顺序与采样顺序分离

- **尝试**：计算行重排以适配Attention路径，采样保持原请求顺序。当前适配队友normalized main328，仅改runner/helper两文件；代码4fca58ba/tree5c77。140324→141159短测表观约+6.59%，但KV521840→521936，gain=null。142019完整105题103正确（98.0952%）通过，但P分支0命中。144620原官方8轮全部成功，1536请求；原第2–4轮均值4K5116.68、16K3436.04 total tok/s，实际P N62/M2048/outside59。保留Draft方法候选：这是绝对性能，不能归因单项收益，也不能用吞吐命中弥补准确率P0。旧423的单pair+5.124857%、三题质量、结构映射与独立参考证据保留，不能替代新组合结果。
- **改动**：相关实现 [compute-order-current-main-official.json](../../../analysis/compute-order-current-main-official.json)；[compute-order-current-main-accuracy.json](../../../analysis/compute-order-current-main-accuracy.json)；[compute-order-current-main-pair.json](../../../analysis/compute-order-current-main-pair.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-main-profile/README.md)；[compute-order-math4-event-130351.json](../../../analysis/compute-order-math4-event-130351.json)；[compute-order-math4-event-125330.json](../../../analysis/compute-order-math4-event-125330.json)；[compute-order-service-retest-pair.json](../../../analysis/compute-order-service-retest-pair.json)；[compute-order-math4-summary.json](../../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../../analysis/compute-order-first-layer.json)；[result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：32成功0失败、exit0，104.312939462s、5065.373507102 total tok/s
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T054306Z-compute-order-baseline-context16k",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T05:43:07.486932+00:00",
  "profile_id": "compute_order",
  "phase": "baseline_context16k_short_output",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "baseline_complete_candidate_not_deployed",
  "artifacts": "experiments/framework/20261023T054306Z-compute-order-baseline-context16k",
  "conclusion": "原422短负载基线，32成功0失败、exit0，104.312939462s、5065.373507102 total tok/s；560原件逐文件核对导入。原bc51/SERVER/seed721201、VERIFY0、finiteunset、无profiler；KV521936，DB554表/20517行三SHA前后不变。候选仍在CPU实现和互审，gain=null；后续先正确性并检查同DB/KV等可比条件，不与旧coverage诊断比较性能；设备68MiB/0、双栈9031关闭。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T054306Z-compute-order-baseline-context16k](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261023-134612.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261023-134612.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
