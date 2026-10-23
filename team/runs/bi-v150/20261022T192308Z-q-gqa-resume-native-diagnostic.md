<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T192308Z-q-gqa-resume-native-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #163 · KV 生命周期观察

- **尝试**：分配失败、抢占与恢复的观察原件，不自动等于可回收机会。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T192308Z-q-gqa-resume-native-diagnostic",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T19:23:09.987080+00:00",
  "profile_id": "q_gqa_resume_native",
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
  "artifacts": "experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic",
  "conclusion": "当前已过准确率的Q+GQA414源追加原恢复窗口诊断，原参数32成功0失败；root逐481seal验收复用，DB529表19769行三SHA前后同、后态空闲。Engine345934同rid首次恢复payload2944→16704，7步目标调度13760tokens（前6步D29/P2019/M2048，末D29/P1646/M1675），CPUknown不是GPU完成floor；不与191047的13672tokens当成同请求或同轨迹。唯一reader得到3696可见kernel合计2807.462ms，首末跨度2855.520ms：2D1587.201/GQA-decode319.574/GQA-reduce2.529/GEMM776.657ms，包含同批29旁路decode，不全归victim或换算吞吐收益。既有稀疏hist端点只给恒N计数cadence参考：N2为477计数/21.152ms，N1为331计数/27.893ms（含shutdown/drain），不是GPU步时或两者因果边际；此轮为profiler诊断，不作性能pair。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T192308Z-q-gqa-resume-native-diagnostic](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/launch-command.json)；[command.txt](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-032720.json](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-032720.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/server.log)；[gpu.csv](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
