<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T144620Z-current-main-compute-order-official

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #206 · 计算顺序与采样顺序分离

- **尝试**：计算行重排以适配Attention路径，采样保持原请求顺序。PR15+PR21兼容组合已由PR22合入；142019完整105题102正确（97.1429%）通过，173454原官方8轮全部成功，第2–4轮均值4K5118.99、16K3436.17 total tok/s。该组合的官方16K KV为521936；这是组合绝对结果，不作两个方法的单项因果拆分。旧423短测、三题质量、结构映射与独立参考证据保留，不能替代新组合结果。
- **改动**：相关实现 [compute-order-current-main-official.json](../../../analysis/compute-order-current-main-official.json)；[compute-order-current-main-accuracy.json](../../../analysis/compute-order-current-main-accuracy.json)；[compute-order-current-main-pair.json](../../../analysis/compute-order-current-main-pair.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-main-profile/README.md)；[compute-order-math4-event-130351.json](../../../analysis/compute-order-math4-event-130351.json)；[compute-order-math4-event-125330.json](../../../analysis/compute-order-math4-event-125330.json)；[compute-order-service-retest-pair.json](../../../analysis/compute-order-service-retest-pair.json)；[compute-order-math4-summary.json](../../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../../analysis/compute-order-first-layer.json)；[result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：4096/16384 / 1024 / 64 / 256/128 x4。
- **结果**：两case各4轮全部SUCCESS，1536请求成功，原第2–4轮均值：4K5116.68、16K3436.04 total tok/s
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T144620Z-current-main-compute-order-official",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T14:46:20.713826+00:00",
  "profile_id": "compute_order",
  "phase": "current_main_official_throughput",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "3283672b92fa30f93f652b242193999836a95f88",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096/16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256/128 x4",
  "profiler": "false",
  "status": "official_complete_absolute_results_no_causal_gain",
  "artifacts": "experiments/official/20261023T144620Z-current-main-compute-order-official",
  "conclusion": "原官方两case各4轮全部SUCCESS，1536请求成功，原第2–4轮均值：4K5116.68、16K3436.04 total tok/s；TTFT4580.19/152082.85ms，TPOT57.74/130.38ms。446源码tree5c77与103/105准确率相同；官方P实际N62/M2048/outside59，准确率评测P0，不能证明P分支完整精度。单臂gain=null，不与旧版本或队友PR16归因比较。725原件逐项核、726导入，DB567/20986→569/21053；68MiB/0、9031双栈关闭、服务/Engine/benchmark退出。保留Draft方法候选，不自动集成；详analysis/compute-order-current-main-official.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T144620Z-current-main-compute-order-official](../../../experiments/official/20261023T144620Z-current-main-compute-order-official)
- 原命令：[benchmark-command.json](../../../experiments/official/20261023T144620Z-current-main-compute-order-official/benchmark-command.json)；[command.txt](../../../experiments/official/20261023T144620Z-current-main-compute-order-official-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261023T144620Z-current-main-compute-order-official/manifest.json)；[postflight-full.json](../../../experiments/official/20261023T144620Z-current-main-compute-order-official/postflight-full.json)；[purpose.json](../../../experiments/official/20261023T144620Z-current-main-compute-order-official-control/purpose.json)；[source-sha256.json](../../../experiments/official/20261023T144620Z-current-main-compute-order-official-control/source-sha256.json)
- 原始结果：[raw_runs_20261023_224715.csv](../../../experiments/official/20261023T144620Z-current-main-compute-order-official/benchmark_results/raw_runs_20261023_224715.csv)；[summary_20261023_224715.csv](../../../experiments/official/20261023T144620Z-current-main-compute-order-official/benchmark_results/summary_20261023_224715.csv)；[result.json](../../../experiments/official/20261023T144620Z-current-main-compute-order-official/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261023T144620Z-current-main-compute-order-official/server.log)；[gpu.csv](../../../experiments/official/20261023T144620Z-current-main-compute-order-official/gpu.csv)；[exit-code](../../../experiments/official/20261023T144620Z-current-main-compute-order-official/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
