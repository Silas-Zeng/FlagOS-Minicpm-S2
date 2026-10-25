<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T170235660423Z-prefill-one-kernel-counters

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #282 · 夜间单核硬件计数尝试

- **尝试**：尝试获取当前prefill单核计算/访存/发射硬件计数以支持后续设计。
- **改动**：仅增加ixkn包装、profiles目录和所属进程组收尾；复用已测worker，不把受profile影响的计时当复测。 版本、命令和源码见下方原件；[方法记录](../../methods/night-kernel-counters.md)。
- **怎么测**：原baseline prefill单核，ixkn SpeedOfLight/ComputeWorkload/Memory、launch-skip2/count1/kernel replay；worker保持旧组件，原manifest和命令保存。
- **结果**：wrapper exit -11；worker写完results并有61440B ixkn-rep，离线导入rc255/Unknown device name（空），CLI指标不可用；SQLite原事件只作有限来源核对。
- **是否保留**：保留工具失败，停止本次计数，不修不重跑；全部timing禁止作收益、官方成绩或新增组件资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T170235660423Z-prefill-one-kernel-counters",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-25T17:02:35.660423+00:00",
  "profile_id": "night-kernel-counters",
  "phase": "prefill硬件计数工具失败",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "true",
  "status": "ixkn_prefill_report_import_failed",
  "artifacts": "experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters",
  "conclusion": "仅对原baseline prefill单核进行ixkn硬件计数，复用旧组件worker，不是新候选验证。owner281413/ixkn281416于17:03:02结束，wrapper exit -11；results.status=component_only_passed并留下61440B ixkn-rep，但既有离线导入rc255，原文Error: Unknown device name:（名称为空）。未取得可归属、可读取的硬件计数，不猜测瓶颈；本run全部Event/wall禁止算收益、官方成绩或新增组件资格。DB207f/source/native/所属进程组/postflight清理通过。工具失败留证后跳过，不修驱动、不重跑。仅小原件已回收，大张量/IR/DB留远端，完整封包延期至夜间阶段结束。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T170235660423Z-prefill-one-kernel-counters](../../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/manifest.json)
- 原始结果：[results.json](../../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/results.json)
- 日志 / 采样：[worker.log](../../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/worker.log)；[gpu.csv](../../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/gpu.csv)；[exit-code](../../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
