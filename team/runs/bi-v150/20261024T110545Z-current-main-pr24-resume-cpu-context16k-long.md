<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T110545Z-current-main-pr24-resume-cpu-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #211 · PR24 移植失配与 KV 诊断

- **尝试**：本实例复用了旧AOT图：42层旧gate linear、native调用0；类绑定/SO检查不能证明真实模型路径，105037至124000六轮的PR24模型资格统一撤回。保留standalone 9项、CPU/trace原始观察和VERIFY1每方向729415680字节一致事实，均不替代完整模型正确性。Attention约1.018秒不再作为有效PR24净预算；先修复缓存身份，相关完整规模对照已停止且候选未启动。旧结论以本修正为准，原件不改。
- **改动**：相关实现 [CURRENT_WORK.md](../../../CURRENT_WORK.md)；[loaded-computation-graph.py](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/loaded-computation-graph.py)；[early-stop-request.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/early-stop-request.json)；[state.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/result.json)；[coverage.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/coverage.json)；[state.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/state.json)；[observer-manifest.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/observer-manifest.json)；[archive-receipt.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/archive-receipt.json)；[pr24-kv-diagnostic.json](../../../analysis/pr24-kv-diagnostic.json)；[pr24-resume-native-v2-114500.json](../../../analysis/pr24-resume-native-v2-114500.json)；[pr24-resume-native-failure.json](../../../analysis/pr24-resume-native-failure.json)；[pr24-resume-db-comparison.json](../../../analysis/pr24-resume-db-comparison.json)；[summary.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json)；[native-build-manifest.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json)；[operator-check.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/operator-check.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：后验修正：本实例旧AOT图失配，PR24真实模型路径资格撤回；保留32成功0失败和1次抢占的CPU观察，不作为有效PR24模型的重算或收益预算。
- **是否保留**：保留CPU抢占及失败/恢复原件；撤回PR24模型路径资格，不作有效基线、完整模型正确性或净收益预算。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T110545Z-current-main-pr24-resume-cpu-context16k-long",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T11:05:45Z",
  "profile_id": "pr24-main",
  "phase": "resume_cpu_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "1ad9a708ee77323372f0fa5975a04a52d294852c",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "model_path_invalidated_stale_aot_cpu_observation",
  "artifacts": "experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long",
  "conclusion": "后验修正：本实例旧AOT图失配，PR24真实模型路径资格撤回；保留32成功0失败和1次抢占的CPU观察，不作为有效PR24模型的重算或收益预算。原victim已提交16982，首次APC16800分配失败，准入11536，3段q2018/2018/1411到16983；重叠CPU前缀5446不证明GPU完成。M1441新调优，6.265秒非GPU收益。原driver0/owner1（monitor sleep瞬态），复核退出后恢复207f1b、源码/native未变，原失败及cleanup-recovery保留。当前先修复缓存身份，不能沿旧图预算继续对照；见CURRENT_WORK.md。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T110545Z-current-main-pr24-resume-cpu-context16k-long](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/manifest.json)；[purpose.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261024-191149.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261024-191149.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
