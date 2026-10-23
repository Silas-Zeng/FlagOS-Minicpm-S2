<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T135558Z-q-shared-hardware-diagnostic-v2

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #146 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：RNG/输出有限及padding/重复Q输出检查通过，worker与controller均成功，绑定恢复及设备settle
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T135558Z-q-shared-hardware-diagnostic-v2",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T13:55:58.358486+00:00",
  "profile_id": "q_shared_hardware_diagnostic",
  "phase": "baseline_attention_hardware_metrics",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "true",
  "status": "complete_metrics_inconclusive",
  "artifacts": "experiments/framework/20261022T135558Z-q-shared-hardware-diagnostic-v2",
  "conclusion": "原C2/C3合成D1/P2047/KV16K诊断v2完成128次forward/384个kernel，真实路径/完整KV bits/RNG/输出有限及padding/重复Q输出检查通过，worker与controller均成功，绑定恢复及设备settle。8次预热后重复相同Q；窗口1401.418586ms仅用于定位trace，不是性能基线。每metric目标窗仅2样本，实际跨度约56.8ms和1347.1ms而非名义500Hz的2ms，global/shared bandwidth均0，不能据此断言瓶颈、带宽或吞吐。原2D编译65536B shared/102regs/0spill可保留为资源元数据。root34项seal全核复用；保留诊断及限制，无性能收益或DB一致性结论。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T135558Z-q-shared-hardware-diagnostic-v2](../../../experiments/framework/20261022T135558Z-q-shared-hardware-diagnostic-v2)
- 原命令：[command.txt](../../../experiments/framework/20261022T135558Z-q-shared-hardware-diagnostic-v2-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T135558Z-q-shared-hardware-diagnostic-v2-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T135558Z-q-shared-hardware-diagnostic-v2/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T135558Z-q-shared-hardware-diagnostic-v2/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T135558Z-q-shared-hardware-diagnostic-v2/worker.log)；[gpu.csv](../../../experiments/framework/20261022T135558Z-q-shared-hardware-diagnostic-v2/gpu.csv)；[exit-code](../../../experiments/framework/20261022T135558Z-q-shared-hardware-diagnostic-v2/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
