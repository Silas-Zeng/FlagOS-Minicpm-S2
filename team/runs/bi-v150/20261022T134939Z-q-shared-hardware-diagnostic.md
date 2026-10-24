<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T134939Z-q-shared-hardware-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #145 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：失败后返回0，v1外层controller误报0，均不能算诊断成功
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T134939Z-q-shared-hardware-diagnostic",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T13:49:39.499161+00:00",
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
  "status": "failed_before_profile_window",
  "artifacts": "experiments/framework/20261022T134939Z-q-shared-hardware-diagnostic",
  "conclusion": "原C2/C3合成D1/P2047/KV16K硬件诊断在原compiled观察为空时停止：worker failed、compiled=[]、profile={}，未启动128次采样窗；ixsys吞掉worker失败后返回0，v1外层controller误报0，均不能算诊断成功。原件保留，root已核33项seal；设备settle、入口绑定恢复。无硬件瓶颈/吞吐结论，不声称DB一致。v2仅恢复config先于模块导入/安装的旧门顺序、加真实绑定断言，并聚合worker完成结果与ixsys退出码；不放宽空捕获拒绝。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T134939Z-q-shared-hardware-diagnostic](../../../experiments/framework/20261022T134939Z-q-shared-hardware-diagnostic)
- 原命令：[command.txt](../../../experiments/framework/20261022T134939Z-q-shared-hardware-diagnostic-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T134939Z-q-shared-hardware-diagnostic-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T134939Z-q-shared-hardware-diagnostic/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T134939Z-q-shared-hardware-diagnostic/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T134939Z-q-shared-hardware-diagnostic/worker.log)；[gpu.csv](../../../experiments/framework/20261022T134939Z-q-shared-hardware-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261022T134939Z-q-shared-hardware-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
