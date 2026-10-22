<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T104920Z-input-prep-timing-combined-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #127 · 输入准备成本诊断

- **尝试**：当前组合的真实输入等待与预处理累计；诊断耗时不作为性能收益。
- **改动**：相关实现 [prepare_input_prep_timing.py](../../../scripts/remote/input-prep-timing-combined/prepare_input_prep_timing.py)；[biv150_input_prep_timing.py](../../../scripts/remote/input-prep-timing-combined/biv150_input_prep_timing.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：EngineCore289848最后快照2048步，等待累计14.059984ms/max132.438us，预处理累计14.488006758s，占0.0970%；输入等待方向暂降优先级，诊断不报性能收益
- **是否保留**：保留诊断结论；当前不据此实施输入同步优化。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T104920Z-input-prep-timing-combined-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T10:49:22.358997+00:00",
  "profile_id": "input_prep_timing_combined_long",
  "phase": "context16k_long_wait_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_partial_diagnostic",
  "artifacts": "experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long",
  "conclusion": "6f918组合在16K输入/1024输出/32请求下32成功0失败，KV抢占一次。EngineCore289848最后快照2048步，等待累计14.059984ms/max132.438us，预处理累计14.488006758s，占0.0970%；快照非最终全负载。输入等待方向暂降优先级，诊断不报性能收益；DB前后同，413源及后态空闲已留证，关停EngineDeadError原日志保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T104920Z-input-prep-timing-combined-context16k-long](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-185418.json](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-185418.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T104920Z-input-prep-timing-combined-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
