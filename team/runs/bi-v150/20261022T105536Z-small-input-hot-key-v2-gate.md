<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T105536Z-small-input-hot-key-v2-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #128 · Attention热key复用

- **尝试**：复用绑定后的key/cache并保留原launch尾；未命中、实际命中及负结果都保留。
- **改动**：相关实现 [biv150_attention_key_recipe_v2.py](../../../patches/framework/candidates/biv150_attention_key_recipe_v2.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall从0.464890547到0.502826703ms，增加8.1602%；原件保留，不报服务收益或整模型accuracy
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T105536Z-small-input-hot-key-v2-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T10:55:36.829635+00:00",
  "profile_id": "attention_key_recipe_v2_small",
  "phase": "actual_layer_hot_key_small_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_no_wall_gain",
  "artifacts": "experiments/framework/20261022T105536Z-small-input-hot-key-v2-gate",
  "conclusion": "D29/P128/KV1024新增短形状真实hot命中且正确性通过，32次ABBA：wall从0.464890547到0.502826703ms，增加8.1602%；event增加22.1766%。长短形状均未见收益，放弃当前v2，不集成；原件保留，不报服务收益或整模型accuracy。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T105536Z-small-input-hot-key-v2-gate](../../../experiments/framework/20261022T105536Z-small-input-hot-key-v2-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T105536Z-small-input-hot-key-v2-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T105536Z-small-input-hot-key-v2-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T105536Z-small-input-hot-key-v2-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T105536Z-small-input-hot-key-v2-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T105536Z-small-input-hot-key-v2-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T105536Z-small-input-hot-key-v2-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T105536Z-small-input-hot-key-v2-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
