<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T170652502004Z-gqa-one-kernel-counters

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #283 · 夜间单核硬件计数尝试

- **尝试**：尝试采集原GQA单核硬件计数，与prefill关键路径信息分开。
- **改动**：只加ixkn包装；launch-skip=0被工具拒绝，未运行数值或性能比较。 版本、命令和源码见下方原件；[方法记录](../../methods/night-kernel-counters.md)。
- **怎么测**：原page16 GQA单核计数入口，launch-skip0/count1；工具在参数阶段退出，DB/source/native及所属进程组清理通过。
- **结果**：ixkn立即exit255：launch-skip参数0无效；未生成results.json或报告，未进入采样。
- **是否保留**：记录工具参数拒绝后跳过，不修不重跑；不判候选数值或性能失败。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T170652502004Z-gqa-one-kernel-counters",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-25T17:06:52.502004+00:00",
  "profile_id": "night-kernel-counters",
  "phase": "GQA硬件计数参数拒绝",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "true",
  "status": "ixkn_gqa_argument_rejected",
  "artifacts": "experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters",
  "conclusion": "仅尝试GQA原page16 baseline单核ixkn计数；owner281694/ixkn281698于17:06:52.915971立即exit255，worker.log原文the argument ('0') for option '--launch-skip' is invalid。未进入采样，没有results.json或ixkn-rep，不是候选数值/性能失败。DB/source/native/所属进程组/postflight清理通过。原参数拒绝留证，不修、不重跑；本run任何计时不作收益或新增组件资格。仅小原件回收、DB留远端，完整封包留阶段结束后处理。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T170652502004Z-gqa-one-kernel-counters](../../../experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[worker.log](../../../experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters/worker.log)；[gpu.csv](../../../experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters/gpu.csv)；[exit-code](../../../experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
