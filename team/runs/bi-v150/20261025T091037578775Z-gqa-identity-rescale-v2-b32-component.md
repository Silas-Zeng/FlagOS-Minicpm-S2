<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T091037578775Z-gqa-identity-rescale-v2-b32-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #257 · GQA恒等rescale跳过

- **尝试**：仅当同组8头的finite最大值严格不变时省去rescale，其他分支与原reducer保留。N33/B40/S16及B32/S4分别完成8组数值/Graph检查，Graph ABBA耗时观察分别+2.308%/+1.058%；未见收益，不推进模型/官方。B32首次空padding验证器异常单列，独立v3修验证器后重测，未修改候选数学。均为随机输入组件，非实际激活重放。
- **改动**：相关实现 [kernel.diff](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/kernel.diff)；[worker.py](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/worker.py)；[padding-source.json](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/padding-source.json)；[worker.diff](../../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/source/worker.diff)；本轮准确变体以原件源码清单为准。
- **怎么测**：固定16384随机输入，实际生产GQA＋reducer；v3验证器保留原数学及16-call Graph ABBA。run后缀仍v2，源码pins识别v3。
- **结果**：v3仅修空padding检查；B32/S4的8组数值/Graph通过，event1.029569→1.040463ms（+1.058%），wall+0.949%。
- **是否保留**：两档均未见收益，收口保留原件，不推进模型或官方测试。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T091037578775Z-gqa-identity-rescale-v2-b32-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T09:10:37.578775+00:00",
  "profile_id": "gqa-identity-rescale",
  "phase": "GQA B32/S4组件Graph ABBA",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_rescale_b32_negative",
  "artifacts": "experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component",
  "conclusion": "v3仅修复验证器的空padding检查，原owner命名仍含v2，以source/asset-pins和worker42d864ba识别；candidate7bc22数学不变。B32/S4的8组数值及Graph边界均通过；Graph ABBA event每调用1.029569→1.040463ms（耗时+1.058%），wall1.035674→1.045499ms（+0.949%）。与N33/B40/S16同为局部负信号，不进入模型/官方；原090542验证器失败单列保留。源码/native未变、DB恢复及清理通过；随机输入组件不等于模型准确率或端到端收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T091037578775Z-gqa-identity-rescale-v2-b32-component](../../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
