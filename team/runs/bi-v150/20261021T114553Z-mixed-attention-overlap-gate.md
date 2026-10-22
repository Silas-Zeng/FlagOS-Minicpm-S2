<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T114553Z-mixed-attention-overlap-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #68 · Attention 分流与 launch

- **尝试**：prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：Independent14sourceSHA
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T114553Z-mixed-attention-overlap-gate",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T11:45:53.497320+00:00",
  "profile_id": "mixed_attention_overlap",
  "phase": "single_layer_amortized_check",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "one_layer_gate_pass_no_serving_integration",
  "artifacts": "experiments/framework/20261021T114553Z-mixed-attention-overlap-gate",
  "conclusion": "Independent14sourceSHA;exit0 allcorrectness true/pending0peak9;v2methodEventconstructionoutsidewall64loopsABBA;wall12.460649to12.417108ms0.349429percent saved;event12.409186to12.414136ms flatandslightlyslower;no hardwareconcurrencyorE2Egainproof;retainsmallprototype no serviceintegration;fullpost11:47:13.030618UTC68MiB0percentclosed"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T114553Z-mixed-attention-overlap-gate](../../../experiments/framework/20261021T114553Z-mixed-attention-overlap-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T114553Z-mixed-attention-overlap-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T114553Z-mixed-attention-overlap-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T114553Z-mixed-attention-overlap-gate/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T114553Z-mixed-attention-overlap-gate-control/postflight-full.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T114553Z-mixed-attention-overlap-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T114553Z-mixed-attention-overlap-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T114553Z-mixed-attention-overlap-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T114553Z-mixed-attention-overlap-gate/exit-code)
- 相关说明：[2026-10-21-overlap-timing-review](../../../analysis/2026-10-21-overlap-timing-review.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
