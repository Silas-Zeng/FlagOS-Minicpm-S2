<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T203032Z-rope-kv-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #233 · RoPE与KV写入融合

- **尝试**：42层RoPE＋KV原数学融合组件首次验证。
- **改动**：本轮源码、版本与原始结果见下方证据；方法边界见[方法记录](../../methods/rope-kv-fusion.md)。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 独立组件；非模型请求。
- **结果**：configs=None导致记录器TypeError，无有效case；原失败保留，不作数值或性能负结果。
- **是否保留**：保留失败；仅修记录器后另开v2，不追溯改判。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T203032Z-rope-kv-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T20:30:32Z",
  "profile_id": "rope-kv-fusion",
  "phase": "rope_kv_component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "独立组件；非模型请求",
  "profiler": "false",
  "status": "rope_component_recording_failed",
  "artifacts": "experiments/framework/20261024T203032Z-rope-kv-component",
  "conclusion": "RoPE→KV首次独立42层组件在记录launcher configs时遇None不可迭代TypeError，results没有有效case、原exit1保留。20:30:51 UTC清理/source检查通过。是记录器故障，不是数值或性能负结果；v2只修记录后另开新run，不能追溯改判本轮。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T203032Z-rope-kv-component](../../../experiments/framework/20261024T203032Z-rope-kv-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T203032Z-rope-kv-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261024T203032Z-rope-kv-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261024T203032Z-rope-kv-component/worker.log)；[gpu.csv](../../../experiments/framework/20261024T203032Z-rope-kv-component/gpu.csv)；[exit-code](../../../experiments/framework/20261024T203032Z-rope-kv-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
