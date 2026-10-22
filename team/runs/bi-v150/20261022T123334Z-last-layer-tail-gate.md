<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T123334Z-last-layer-tail-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #139 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：失败：RowParallelLinear的disable_tp未免除ModelWeightParameter对TP组的依赖，真实TP组未初始化
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T123334Z-last-layer-tail-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:33:34.405596+00:00",
  "profile_id": "last_layer_tail",
  "phase": "actual_class_tail_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "failed_before_timing",
  "artifacts": "experiments/framework/20261022T123334Z-last-layer-tail-gate",
  "conclusion": "末层Attention后O投影/MLP尾段裁剪首个局部门在权重构造阶段失败：RowParallelLinear的disable_tp未免除ModelWeightParameter对TP组的依赖，真实TP组未初始化。无correctness case或计时，不能判断方法性能；GPU已settled且空闲、412基点/归档源未变，480原件逐项核验。保留失败，下一门只补真实world1进程组初始化/销毁，不伪造rank或修改尾段算法。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T123334Z-last-layer-tail-gate](../../../experiments/framework/20261022T123334Z-last-layer-tail-gate)
- 原命令：[launch-command.json](../../../experiments/framework/20261022T123334Z-last-layer-tail-gate-control/launch-command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T123334Z-last-layer-tail-gate/manifest.json)；[source-sha256.json](../../../experiments/framework/20261022T123334Z-last-layer-tail-gate-control/source-sha256.json)；[postflight.json](../../../experiments/framework/20261022T123334Z-last-layer-tail-gate-control/postflight.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T123334Z-last-layer-tail-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T123334Z-last-layer-tail-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T123334Z-last-layer-tail-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T123334Z-last-layer-tail-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
