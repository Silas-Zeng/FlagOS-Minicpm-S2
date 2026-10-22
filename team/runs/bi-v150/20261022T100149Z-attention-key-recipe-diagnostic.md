<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T100149Z-attention-key-recipe-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #122 · Attention热key复用

- **尝试**：复用绑定后的key/cache并保留原launch尾；未命中、实际命中及负结果都保留。
- **改动**：相关实现 [biv150_attention_key_recipe_v2.py](../../../patches/framework/candidates/biv150_attention_key_recipe_v2.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：独立诊断仍exit1、未计时
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T100149Z-attention-key-recipe-diagnostic",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T10:01:50.022464+00:00",
  "profile_id": "attention_key_recipe_scope_diagnostic",
  "phase": "actual_layer_fallback_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "failed_scope_diagnosed",
  "artifacts": "experiments/framework/20261022T100149Z-attention-key-recipe-diagnostic",
  "conclusion": "独立诊断仍exit1、未计时；实际launch enter/exit为非None HookChain对象，候选以is notNone拒绝，未放宽保护或更改数学。诊断原件保留；v2改为仅复用key/cache并保留原hook/launch尾，尚未上卡。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T100149Z-attention-key-recipe-diagnostic](../../../experiments/framework/20261022T100149Z-attention-key-recipe-diagnostic)
- 原命令：[command.txt](../../../experiments/framework/20261022T100149Z-attention-key-recipe-diagnostic-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T100149Z-attention-key-recipe-diagnostic-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T100149Z-attention-key-recipe-diagnostic/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T100149Z-attention-key-recipe-diagnostic/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T100149Z-attention-key-recipe-diagnostic/worker.log)；[gpu.csv](../../../experiments/framework/20261022T100149Z-attention-key-recipe-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261022T100149Z-attention-key-recipe-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
