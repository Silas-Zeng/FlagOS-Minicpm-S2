<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T130038Z-prefill-v-late-cache-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #143 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：失败，下一轮只修source pin
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T130038Z-prefill-v-late-cache-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T13:00:38.456563+00:00",
  "profile_id": "prefill_v_late_cache",
  "phase": "actual_layer_cache_preference_isolation",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "failed_before_mutation",
  "artifacts": "experiments/framework/20261022T130038Z-prefill-v-late-cache-gate",
  "conclusion": "Vlate＋函数cache偏好三臂首门在source身份核验时停止：actual模块为已审iluvatar spec，而准备稿误pin了base源码；尚未调用setter、无数值或计时结论，原绑定已恢复。保留失败，下一轮只修source pin。38原件evidence-seal逐项核验。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T130038Z-prefill-v-late-cache-gate](../../../experiments/framework/20261022T130038Z-prefill-v-late-cache-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T130038Z-prefill-v-late-cache-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T130038Z-prefill-v-late-cache-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T130038Z-prefill-v-late-cache-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T130038Z-prefill-v-late-cache-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T130038Z-prefill-v-late-cache-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T130038Z-prefill-v-late-cache-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T130038Z-prefill-v-late-cache-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
