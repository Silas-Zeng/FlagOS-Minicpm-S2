<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T204020Z-final-ffn-row-prune

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #235 · 末层FFN/o_proj选行与模型对照

- **尝试**：实际末层权重与原编译数学，比较全M后选行与先选行再FFN。
- **改动**：本轮源码、版本与原始结果见下方证据；方法边界见[方法记录](../../methods/final-ffn-row-prune.md)。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 独立组件；非模型请求。
- **结果**：实际mm_out logger未挂入记录链，守卫停止，无有效case；清理/DB恢复通过，不是数值或性能负结果。
- **是否保留**：保留首次失败；独立v2仅修日志，等待新run。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T204020Z-final-ffn-row-prune",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T20:40:20Z",
  "profile_id": "final-ffn-row-prune",
  "phase": "final_ffn_component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "独立组件；非模型请求",
  "profiler": "false",
  "status": "final_ffn_dispatch_recording_failed",
  "artifacts": "experiments/framework/20261024T204020Z-final-ffn-row-prune",
  "conclusion": "末层FFN前选行首次组件，实际mm_out模块logger为_iluvatar命名、不在flag_gems父链，执行记录守卫未见mm_out而停止；results没有有效case，原exit1保留。20:40:50 UTC清理/source和DB恢复通过。不是数学或性能负结果；仅日志挂载修复在独立v2准备，后续新run另验，不追溯赋予本轮数值或性能资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T204020Z-final-ffn-row-prune](../../../experiments/framework/20261024T204020Z-final-ffn-row-prune)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T204020Z-final-ffn-row-prune/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261024T204020Z-final-ffn-row-prune/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261024T204020Z-final-ffn-row-prune/worker.log)；[gpu.csv](../../../experiments/framework/20261024T204020Z-final-ffn-row-prune/gpu.csv)；[exit-code](../../../experiments/framework/20261024T204020Z-final-ffn-row-prune/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
