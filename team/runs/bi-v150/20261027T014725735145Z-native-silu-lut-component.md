<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T014725735145Z-native-silu-lut-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #351 · BF16 SiLU精确查表

- **尝试**：完整gate慢10.37%，正确性通过，停止。
- **改动**：相关实现 [result.json](../../../experiments/framework/20261027T014725735145Z-native-silu-lut-component/result.json)；[archive-receipt.json](../../../experiments/framework/20261027T014725735145Z-native-silu-lut-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原始计时、实际SO与编译命令、环境和清理见原件。
- **结果**：真实layer20权重/M2048完整native gate：A实际14f SO、B同量化/GEMM及BF16舍入，仅以256KiB同设备精确表替SiLU expf和除法。65280有限BF16位型×12up逐位、12项真实gate/Graph/side及独立INT64、输入/表/RNG门全过。完整Graph ABBA 0.716412395239→0.790738135576
- **是否保留**：停止，不进入生产或官方测试。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T014725735145Z-native-silu-lut-component",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T01:47:25.735145+00:00",
  "profile_id": "native-silu-lut",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_silu_lut_negative",
  "artifacts": "experiments/framework/20261027T014725735145Z-native-silu-lut-component",
  "conclusion": "真实layer20权重/M2048完整native gate：A实际14f SO、B同量化/GEMM及BF16舍入，仅以256KiB同设备精确表替SiLU expf和除法。65280有限BF16位型×12up逐位、12项真实gate/Graph/side及独立INT64、输入/表/RNG门全过。完整Graph ABBA 0.716412395239→0.790738135576ms，耗时+10.374714%；额外gather成本计入，非只测尾核。停止该实现，不扫M或生产，不声称错误或近似；DB恢复/清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T014725735145Z-native-silu-lut-component](../../../experiments/framework/20261027T014725735145Z-native-silu-lut-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T014725735145Z-native-silu-lut-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261027T014725735145Z-native-silu-lut-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T014725735145Z-native-silu-lut-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T014725735145Z-native-silu-lut-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T014725735145Z-native-silu-lut-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
