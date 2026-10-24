<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T110545Z-current-main-pr24-resume-cpu-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #211 · PR24 组合基线与 KV 抢占诊断

- **尝试**：复用队友已合并的 INT8 gate/up、PR15/PR21 与 Q fragment 组合；本实例 SO 的9项检查通过，短服务32请求全成功。长输出观察覆盖1次抢占，重复提交与旧CPU已提交前缀重叠5446 tokens；M1441冷调优影响CPU计时，尚不能推算GPU收益。原收尾失败及DB恢复证据保留，下一步仅采一次已调优的恢复窗口。
- **改动**：相关实现 [pr24-kv-diagnostic.json](../../../analysis/pr24-kv-diagnostic.json)；[pr24-resume-db-comparison.json](../../../analysis/pr24-resume-db-comparison.json)；[summary.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json)；[native-build-manifest.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json)；[operator-check.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/operator-check.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败，真实抢占1次
- **是否保留**：保留抢占证据；KV SAVE/FULL仍为候选，GPU开销待一次已调优窗口确认。

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
  "status": "diagnostic_covered_service_pass_cleanup_recovered",
  "artifacts": "experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long",
  "conclusion": "32成功0失败，真实抢占1次；victim已提交16982，首次APC16800分配失败，准入降至11536，3段q2018/2018/1411重新提交到16983；重叠旧CPU前缀5446，不证明GPU完成。M1441发生新调优，6.265秒非GPU收益；保留SAVE/FULL候选，下一步warmed窗口诊断。driver0/owner1（monitor sleep瞬态），复核退出后恢复207f1b，源码与native未变；原失败及cleanup-recovery保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T110545Z-current-main-pr24-resume-cpu-context16k-long](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/manifest.json)；[purpose.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
