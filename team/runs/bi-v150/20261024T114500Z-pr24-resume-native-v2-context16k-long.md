<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T114500Z-pr24-resume-native-v2-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #213 · PR24 组合基线与 KV 抢占诊断

- **尝试**：本实例 SO 的9项检查通过，短服务32请求全成功。CPU观察确认抢占后的重复提交；修正探针后捕获完整GPU窗口，目标Attention恰168次（4×42）、约1.018秒。P在本轮自然decode前缀下无需重排；KV容量变化、M457冷调优及原owner失败/DB恢复证据均保留。这里只得到局部计算预算，尚无端到端收益；保留KV SAVE/FULL，下一步做一次新组合VERIFY1，暂不重复profile。
- **改动**：相关实现 [pr24-kv-diagnostic.json](../../../analysis/pr24-kv-diagnostic.json)；[pr24-resume-native-v2-114500.json](../../../analysis/pr24-resume-native-v2-114500.json)；[pr24-resume-native-failure.json](../../../analysis/pr24-resume-native-failure.json)；[pr24-resume-db-comparison.json](../../../analysis/pr24-resume-db-comparison.json)；[summary.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json)；[native-build-manifest.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json)；[operator-check.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/operator-check.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败；warmed种子仍有M457冷调优，窗口含同批decode，不报吞吐收益或完整可省预算
- **是否保留**：保留局部GPU预算，进入KV SAVE/FULL最短VERIFY1；尚未确认端到端收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T114500Z-pr24-resume-native-v2-context16k-long",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T11:45:02.454746+00:00",
  "profile_id": "pr24-main",
  "phase": "resume_native_diagnostic_v2",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "1ad9a708ee77323372f0fa5975a04a52d294852c",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "true",
  "status": "diagnostic_native_valid_p_uncovered_cleanup_recovered",
  "artifacts": "experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long",
  "conclusion": "v2修复原装饰器识别后driver0、32成功0失败；native窗口valid，4步target合计6481，M2048/2048/2048/457。Q/native命中，但P未实际重排，coverage不完整故owner1；另monitor sleep5超过宽限3使原cleanup未完成，root于11:52:35 UTC重新持锁复核仅Z并恢复DB207f1b，原失败与cleanup-recovery均保留。profile下KV546528，对非profile547600；warmed种子仍有M457冷调优，窗口含同批decode，不报吞吐收益或完整可省预算。目标2D Attention恰168次（4×42）、1018.292405ms；每步30个decode在前使P无需重排，无额外目标Attention调优次数。保留候选，进入最短VERIFY1，不重复profile；发布仅2改动源码与完整映射，full tar位置/SHA见同名-control/archive-receipt.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T114500Z-pr24-resume-native-v2-context16k-long](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long/manifest.json)；[purpose.json](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261024T114500Z-pr24-resume-native-v2-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
