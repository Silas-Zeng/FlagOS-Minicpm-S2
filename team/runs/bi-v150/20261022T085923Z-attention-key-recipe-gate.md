<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T085923Z-attention-key-recipe-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #121 · Attention热key复用

- **尝试**：复用绑定后的key/cache并保留原launch尾；未命中、实际命中及负结果都保留。
- **改动**：相关实现 [biv150_attention_key_recipe_v2.py](../../../patches/framework/candidates/biv150_attention_key_recipe_v2.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：失败源码和原件保留
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T085923Z-attention-key-recipe-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T08:59:23.226738+00:00",
  "profile_id": "attention_key_recipe_v1",
  "phase": "actual_layer_hot_key_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "failed_scope_not_activated",
  "artifacts": "experiments/framework/20261022T085923Z-attention-key-recipe-gate",
  "conclusion": "首个P2019 case的数值/KV/RNG/新指针及非默认流检查通过，但热路径与bootstrap均为0、fallbacks6，不能证明候选热路径正确；门exit1，未进入ABBA，无性能或整模型准确率结论。后续100149诊断定位hook资格误判，失败源码和原件保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T085923Z-attention-key-recipe-gate](../../../experiments/framework/20261022T085923Z-attention-key-recipe-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T085923Z-attention-key-recipe-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T085923Z-attention-key-recipe-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T085923Z-attention-key-recipe-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T085923Z-attention-key-recipe-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T085923Z-attention-key-recipe-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T085923Z-attention-key-recipe-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T085923Z-attention-key-recipe-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
