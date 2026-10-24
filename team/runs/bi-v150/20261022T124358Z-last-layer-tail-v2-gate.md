<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T124358Z-last-layer-tail-v2-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #140 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：123334失败与v2资产保留
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T124358Z-last-layer-tail-v2-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:43:58.125520+00:00",
  "profile_id": "last_layer_tail_v2",
  "phase": "actual_class_tail_gate_with_real_tp",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "failed_local_tolerance_no_timing",
  "artifacts": "experiments/framework/20261022T124358Z-last-layer-tail-v2-gate",
  "conclusion": "真实world1/TP1初始化及销毁成功；默认输入hidden/residual bitwise，换值新指针非默认流maxabs0.0234375/0.017578125未过原atol/rtol0.01，finite/输入/RNG过，无计时。不能区分形状相关BF16差异与stream因素，不放宽门或继续试。412基点和9源码未变；DB527/19608→527/19702新增94行，schema同而physical/logical变。后态68MiB0/双栈闭，root evidence-seal 482项（含原controller seal）逐SHA全核复用；旧123334失败与v2资产保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T124358Z-last-layer-tail-v2-gate](../../../experiments/framework/20261022T124358Z-last-layer-tail-v2-gate)
- 原命令：[launch-command.json](../../../experiments/framework/20261022T124358Z-last-layer-tail-v2-gate-control/launch-command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T124358Z-last-layer-tail-v2-gate/manifest.json)；[source-sha256.json](../../../experiments/framework/20261022T124358Z-last-layer-tail-v2-gate-control/source-sha256.json)；[postflight.json](../../../experiments/framework/20261022T124358Z-last-layer-tail-v2-gate-control/postflight.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T124358Z-last-layer-tail-v2-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T124358Z-last-layer-tail-v2-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T124358Z-last-layer-tail-v2-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T124358Z-last-layer-tail-v2-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
