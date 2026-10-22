<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T121701Z-prefill-v-late-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #137 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall11.106083→11.267372ms（慢1.4523%），event10.993639→11.136706ms（慢1.3014%）
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T121701Z-prefill-v-late-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:17:01.200367+00:00",
  "profile_id": "prefill_v_late",
  "phase": "actual_layer_2d_v_load_lifetime",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_no_wall_gain",
  "artifacts": "experiments/framework/20261022T121701Z-prefill-v-late-gate",
  "conclusion": "仅将2D普通BF16指针路径V读取/转换后移，BM128/T64/w8/s1、原3D及数学顺序不变；D1/P2047/KV16K上界，严格bits/全KV/RNG/scale/新指针/非默认流门通过，selected68/fallback0/原3D68。32ABBA wall11.106083→11.267372ms（慢1.4523%），event10.993639→11.136706ms（慢1.3014%）；regs102→100/shared65536→49152，双方spills0。放弃当前V-late，保留原V读取顺序，不接服务或扩扫描；资源下降不证明关键路径改善，无stall/驻留证据不定因。单层上界fixture非实测逐步seq_len，不作整模型准确率或吞吐结论。原绑定已恢复，35原件封存核验通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T121701Z-prefill-v-late-gate](../../../experiments/framework/20261022T121701Z-prefill-v-late-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T121701Z-prefill-v-late-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T121701Z-prefill-v-late-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T121701Z-prefill-v-late-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T121701Z-prefill-v-late-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T121701Z-prefill-v-late-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T121701Z-prefill-v-late-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T121701Z-prefill-v-late-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
