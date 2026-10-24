<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T124000Z-pr24-main-fullsize-two-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #215 · PR24 真实路径复验与 KV 诊断

- **尝试**：131603同源码隔离编译缓存后，实际新图有34个native调用（layer4..37），完整Math500 Level3为100/105通过；0请求错误/0空最终，83/99/101达到输出上限，101无可提取答案。该结果仅证明本轮路径与准确率，不报吞吐或精度提升。105037至124000六轮仍因旧AOT图失配撤回PR24模型资格；standalone9、CPU/trace观察与VERIFY1字节事实保留，旧Attention1.018秒不能作有效PR24预算，也不追溯恢复旧性能资格。默认缓存修复和PR25复验另记。
- **改动**：相关实现 [CURRENT_WORK.md](../../../CURRENT_WORK.md)；[accuracy-review.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/accuracy-review.json)；[active-graph-typed-assignment-check.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/active-graph-typed-assignment-check.json)；[computation_graph.py](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/active-graph/computation_graph.py)；[environment-overrides.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/environment-overrides.json)；[archive-receipt.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/archive-receipt.json)；[loaded-computation-graph.py](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/loaded-computation-graph.py)；[early-stop-request.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/early-stop-request.json)；[state.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/result.json)；[coverage.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/coverage.json)；[state.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/state.json)；[observer-manifest.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/observer-manifest.json)；[archive-receipt.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/archive-receipt.json)；[pr24-kv-diagnostic.json](../../../analysis/pr24-kv-diagnostic.json)；[pr24-resume-native-v2-114500.json](../../../analysis/pr24-resume-native-v2-114500.json)；[pr24-resume-native-failure.json](../../../analysis/pr24-resume-native-failure.json)；[pr24-resume-db-comparison.json](../../../analysis/pr24-resume-db-comparison.json)；[summary.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json)；[native-build-manifest.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json)；[operator-check.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/operator-check.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：4096/16384 / 1024 / 64 / 256/128。
- **结果**：旧AOT图失配使完整规模对照异常中止：4K两轮2915.46/2941.09 tok/s、各256请求成功；16K首轮未完成，KV候选未启动，不计收益或有效PR24成绩。
- **是否保留**：保留异常中止、两轮4K原值及缓存失配原件；撤回PR24模型路径资格，不作有效基线、完整模型正确性或净收益预算。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T124000Z-pr24-main-fullsize-two-rounds",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T12:40:01.348005+00:00",
  "profile_id": "pr24-main",
  "phase": "fullsize_two_rounds_stopped",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "1ad9a708ee77323372f0fa5975a04a52d294852c",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096/16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256/128",
  "profiler": "false",
  "status": "model_path_invalidated_stale_aot_screen_stopped",
  "artifacts": "experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds",
  "conclusion": "旧AOT图失配使完整规模对照异常中止：4K两轮2915.46/2941.09 tok/s、各256请求成功；16K首轮未完成，KV候选未启动，不计收益或有效PR24成绩。原两轮duration449.58/445.66秒，input/output各1048576/262144；不丢首轮、不计算官方均值，请求成功或吞吐不代表模型正确。当前缓存图42层旧gate linear、native调用0，SHA ab75722cd9edd5cbd33a2bb72d3f17f090eb2796ec86386d777a852f8e9cd69c；13:00:52 UTC对driver104652发SIGTERM，driver/owner原exit1保留。13:01:33 UTC完成清理与DB恢复207f1b，source/native未变；该后态仅属本轮，不代表当前设备空闲。保留失败、两轮原始metrics及loaded图/缓存身份，先修复缓存再验证真实模型路径。467个重复源码及5个SQLite二进制从发布副本省略，完整映射和原包SHA/路径见同名-control/archive-receipt.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T124000Z-pr24-main-fullsize-two-rounds](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds)
- 原命令：[command.txt](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_screen.csv](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/raw_runs_screen.csv)；[result.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
