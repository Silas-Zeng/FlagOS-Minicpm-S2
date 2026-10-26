<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T055057881154Z-prefill-lpt-causal-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #305 · Prefill序列内CTA调序

- **尝试**：验证本条所述固定形状和新增实现。
- **改动**：改动及精确命令见该run源码和manifest/command原件。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-lpt.md)。
- **怎么测**：复用真实生产ABI/原数值门，新增改动单独验证；不重复旧测试。
- **结果**：Q2048/KV2048原臂与候选输出有限、guard正常，但都被旧long-only FP64 max_abs≤5e-4拒绝：两臂同max_abs0.00352174、relative_l20.00095805。保存输出CPU后核整份逐位一致/max_diff0；不据此认定候选新增数值错，未计时。旧失败原件不改判，后继只以纯排列逐位对照另记，不放宽原FP64诊断阈值。
- **是否保留**：原臂/候选逐位一致；旧FP64拒绝不改判，后继逐位组件单列。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T055057881154Z-prefill-lpt-causal-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T05:50:57.881154+00:00",
  "profile_id": "prefill-lpt",
  "phase": "Prefill CTA调序短causal旧参考界不适用",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_lpt_reference_scope_mismatch",
  "artifacts": "experiments/framework/20261026T055057881154Z-prefill-lpt-causal-component",
  "conclusion": "Q2048/KV2048原臂与候选输出有限、guard正常，但都被旧long-only FP64 max_abs≤5e-4拒绝：两臂同max_abs0.00352174、relative_l20.00095805。保存输出CPU后核整份逐位一致/max_diff0；不据此认定候选新增数值错，未计时。旧失败原件不改判，后继只以纯排列逐位对照另记，不放宽原FP64诊断阈值。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T055057881154Z-prefill-lpt-causal-component](../../../experiments/framework/20261026T055057881154Z-prefill-lpt-causal-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T055057881154Z-prefill-lpt-causal-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T055057881154Z-prefill-lpt-causal-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T055057881154Z-prefill-lpt-causal-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T055057881154Z-prefill-lpt-causal-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T055057881154Z-prefill-lpt-causal-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
