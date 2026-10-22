<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T111804Z-hidden-row-gather-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #62 · 缓冲区 gather 与 token bucket

- **尝试**：输入几何、padding和缓冲区复用候选。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：8sourceSHAindependentlymatch
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T111804Z-hidden-row-gather-gate",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T11:18:04.305877+00:00",
  "profile_id": "hidden_row_gather",
  "phase": "fixture_copy_correctness_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "fixture_gate_pass_independent_review",
  "artifacts": "experiments/framework/20261021T111804Z-hidden-row-gather-gate",
  "conclusion": "8sourceSHAindependentlymatch;originale155runner/transformed e68d;4BF16cases259/952/2048/64rows62active bits/shapes/freshstorage/RNGallpass;int32dynamic1entry eachcase/int64bits/8fallbacks/private negative duplicates/crossstream pass;selectedlaunches6;no actualfullModelRunner/weights/LMhead/sampling/performance/accuracy;exit0 fullpost11:20:21.548652UTC68MiB0percentclosed"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T111804Z-hidden-row-gather-gate](../../../experiments/framework/20261021T111804Z-hidden-row-gather-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T111804Z-hidden-row-gather-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T111804Z-hidden-row-gather-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T111804Z-hidden-row-gather-gate/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T111804Z-hidden-row-gather-gate-control/postflight-full.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T111804Z-hidden-row-gather-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T111804Z-hidden-row-gather-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T111804Z-hidden-row-gather-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T111804Z-hidden-row-gather-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
