<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T055124182279Z-prefill-lpt-long-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #306 · Prefill序列内CTA调序

- **尝试**：验证本条所述固定形状和新增实现。
- **改动**：改动及精确命令见该run源码和manifest/command原件。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-lpt.md)。
- **怎么测**：复用真实生产ABI/原数值门，新增改动单独验证；不重复旧测试。
- **结果**：当前stride/Q-hoist上仅反转序列内query块，Q2047/KV16384初始及换值跨臂逐位、独立FP64、writer/Graph/输入RNG均过。完整Attention Event 8.168149→8.460097ms，慢3.57%，wall同向。长上下文无净益，不推进该范围；短causal另记。source/native/DB/清理通过。
- **是否保留**：长上下文不进模型；短causal单独完成有界验证。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T055124182279Z-prefill-lpt-long-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T05:51:24.182279+00:00",
  "profile_id": "prefill-lpt",
  "phase": "Prefill CTA调序长上下文组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_lpt_component_negative",
  "artifacts": "experiments/framework/20261026T055124182279Z-prefill-lpt-long-component",
  "conclusion": "当前stride/Q-hoist上仅反转序列内query块，Q2047/KV16384初始及换值跨臂逐位、独立FP64、writer/Graph/输入RNG均过。完整Attention Event 8.168149→8.460097ms，慢3.57%，wall同向。长上下文无净益，不推进该范围；短causal另记。source/native/DB/清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T055124182279Z-prefill-lpt-long-component](../../../experiments/framework/20261026T055124182279Z-prefill-lpt-long-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T055124182279Z-prefill-lpt-long-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T055124182279Z-prefill-lpt-long-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T055124182279Z-prefill-lpt-long-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T055124182279Z-prefill-lpt-long-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T055124182279Z-prefill-lpt-long-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
