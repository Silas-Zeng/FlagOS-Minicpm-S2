<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T112338Z-decode-cpu-gather-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #131 · 纯decode CPU gather跳过

- **尝试**：严格纯decode省略无消费者的CPU输入整理；正确性门通过，当前服务候选负收益，不集成。
- **改动**：相关实现 [biv150_decode_cpu_gather.py](../../../archive/ai/20261022-next-service-queue/next-decode-gather/biv150_decode_cpu_gather.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：RNG门通过，selected metadata11/async16，gather skip6/fallback5
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T112338Z-decode-cpu-gather-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T11:23:38.529281+00:00",
  "profile_id": "decode_cpu_gather",
  "phase": "strict_pure_decode_correctness",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_correctness_pass",
  "artifacts": "experiments/framework/20261022T112338Z-decode-cpu-gather-gate",
  "conclusion": "严格纯decode跳过死CPU gather；7种情况、4步graph、完整有效GPU输入/地址/RNG门通过，selected metadata11/async16，gather skip6/fallback5。仅正确性门，随后真实服务113627出现负结果，当前方法不集成。25原件逐项核验。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T112338Z-decode-cpu-gather-gate](../../../experiments/framework/20261022T112338Z-decode-cpu-gather-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T112338Z-decode-cpu-gather-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T112338Z-decode-cpu-gather-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T112338Z-decode-cpu-gather-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T112338Z-decode-cpu-gather-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T112338Z-decode-cpu-gather-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T112338Z-decode-cpu-gather-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T112338Z-decode-cpu-gather-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
