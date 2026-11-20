<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #256 · GQA恒等rescale跳过

- **尝试**：仅当同组8头的finite最大值严格不变时省去rescale，其他分支与原reducer保留。N33/B40/S16及B32/S4分别完成8组数值/Graph检查，Graph ABBA耗时观察分别+2.308%/+1.058%；未见收益，不推进模型/官方。B32首次空padding验证器异常单列，独立v3修验证器后重测，未修改候选数学。均为随机输入组件，非实际激活重放。
- **改动**：相关实现 [kernel.diff](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/kernel.diff)；[worker.py](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/worker.py)；[padding-source.json](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/padding-source.json)；[worker.diff](../../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/source/worker.diff)；本轮准确变体以原件源码清单为准。
- **怎么测**：固定16384随机输入，实际生产GQA＋reducer；8组边界及变输入Graph对fresh基线，关闭profiler的16-call Graph ABBA。
- **结果**：N33/B40/S16：8组数值/Graph检查通过，event1.280913→1.310480ms（耗时+2.308%）；随机组件负信号。
- **是否保留**：保留负结果，不推进模型或官方测试；不将局部差异外推端到端。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T09:03:02.472109+00:00",
  "profile_id": "gqa-identity-rescale",
  "phase": "GQA N33/B40/S16组件Graph ABBA",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_rescale_hotspot_negative",
  "artifacts": "experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component",
  "conclusion": "N33/bucket40/S16，严格finite max相等才跳过rescale，原GQA及reducer同输入Graph ABBA。8组逐位、非finite诊断、guard、padding、变Q/KV/页表及ragged零长度/尾块、Graph fresh对照均通过；event每调用1.280913→1.310480ms，耗时+2.308%，未见收益。使用固定16384随机输入，非原轨迹16646–16653长度或实际激活重放；仅组件信号，不是模型/官方成绩。保留负结果，不进入模型或官方测试；源码/native未变、DB恢复及清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
