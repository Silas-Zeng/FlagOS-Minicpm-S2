<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T165525Z-resume-native-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #152 · 抢占请求选择与进展

- **尝试**：抢占瞬间观察、请求选择及其对照；失配结果也保留。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：3696可见kernel合计3430.398ms：2D Attention58.1271%、GEMM22.6206%、3D Attention15.5462%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T165525Z-resume-native-diagnostic",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T16:55:26.957051+00:00",
  "profile_id": "preemption_snapshot_resume_native",
  "phase": "actual_resume_gpu_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "true",
  "status": "complete_diagnostic_valid",
  "artifacts": "experiments/framework/20261022T165525Z-resume-native-diagnostic",
  "conclusion": "原6f唯一追加诊断，32请求成功0失败，首次实际被抢占同rid恢复窗口7步有效。payload computed2944→16704，目标调度13760tokens、全批13963；CPUknown不是GPU完成floor，不能将调度量全部称为已证实重算。3696可见kernel合计3430.398ms：2D Attention58.1271%、GEMM22.6206%、3D Attention15.5462%；首末跨度3476.593ms含29个伴随decode请求/步，不全归victim或折算吞吐收益。保留诊断；原args/412源及DB527表19702行三SHA一致，461原件逐seal核验、设备清理。累计decode1838步以N30/31/2为主，相同GEMM tile和空Attention早返支持暂不加图档位；结合旧KV恢复负结果继续筛具体框架收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T165525Z-resume-native-diagnostic](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic/launch-command.json)；[command.txt](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-010026.json](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-010026.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic/server.log)；[gpu.csv](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261022T165525Z-resume-native-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
