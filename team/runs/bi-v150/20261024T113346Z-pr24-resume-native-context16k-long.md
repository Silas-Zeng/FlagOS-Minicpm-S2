<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T113346Z-pr24-resume-native-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #212 · PR24 组合基线与 KV 抢占诊断

- **尝试**：本实例 SO 的9项检查通过，短服务32请求全成功。CPU观察确认抢占后的重复提交；修正探针后捕获完整GPU窗口，目标Attention恰168次（4×42）、约1.018秒。P在本轮自然decode前缀下无需重排；KV容量变化、M457冷调优及原owner失败/DB恢复证据均保留。这里只得到局部计算预算，尚无端到端收益；保留KV SAVE/FULL，下一步做一次新组合VERIFY1，暂不重复profile。
- **改动**：相关实现 [pr24-kv-diagnostic.json](../../../analysis/pr24-kv-diagnostic.json)；[pr24-resume-native-v2-114500.json](../../../analysis/pr24-resume-native-v2-114500.json)；[pr24-resume-native-failure.json](../../../analysis/pr24-resume-native-failure.json)；[pr24-resume-db-comparison.json](../../../analysis/pr24-resume-db-comparison.json)；[summary.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json)；[native-build-manifest.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json)；[operator-check.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/operator-check.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：DB由8acaab58种子恢复207f1b，source/native未变，结束时GPU68MiB/0%且9031关闭
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T113346Z-pr24-resume-native-context16k-long",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T11:33:48.506410+00:00",
  "profile_id": "pr24-main",
  "phase": "resume_native_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "1ad9a708ee77323372f0fa5975a04a52d294852c",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "true",
  "status": "diagnostic_smoke_failed_scope_wrapper_no_performance",
  "artifacts": "experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long",
  "conclusion": "warmed恢复窗口诊断在smoke阶段HTTP500，计划的32请求未发出；helper误拒绝原生@managed_inference_mode的execute_model wrapper，未取得恢复窗口或性能结果，不是PR24数值或吞吐负结果。driver1/owner1原件保留；DB由8acaab58种子恢复207f1b，source/native未变，结束时GPU68MiB/0%且9031关闭。只保留诊断失败证据；v2精确修复待启动，未重复已通过的移植检查。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T113346Z-pr24-resume-native-context16k-long](../../../experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long)
- 原命令：[launch-command.json](../../../experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long/manifest.json)；[purpose.json](../../../experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261024T113346Z-pr24-resume-native-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
