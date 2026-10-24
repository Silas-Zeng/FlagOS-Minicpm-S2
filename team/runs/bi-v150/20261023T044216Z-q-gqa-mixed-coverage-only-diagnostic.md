<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #186 · Attention 分流与 launch

- **尝试**：prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：末421execute/259metadata/250mixed，q1共3000，prefix外及未入plan均759（25.3%）
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T04:42:18.072144+00:00",
  "profile_id": "q_gqa_mixed_coverage_only",
  "phase": "current422_short_output_mixed_coverage",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "diagnostic_complete_no_performance_verdict",
  "artifacts": "experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic",
  "conclusion": "32成功0失败、exit0，487原件全核；原16K/128/c64/32req，显式coverage-only、无profiler/新算子。末421execute/259metadata/250mixed，q1共3000，prefix外及未入plan均759（25.3%）；unsupported/errors0。相比1024输出观测52/4032=1.28968%，证明排列机会依赖输出负载；计数非forward/确认decode、无K或耗时加权，不是25.3%性能收益。KV521840、DB554表/20517行三hash前后不变；原owner退出且68MiB/0。保留诊断证据，compute-order只进入成本评估/最小正确性实现准备，不直接集成或声明收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic/launch-command.json)；[command.txt](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261023-124524.json](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261023-124524.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic/server.log)；[gpu.csv](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
