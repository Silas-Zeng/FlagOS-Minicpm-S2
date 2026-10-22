<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T121838Z-prefill-visible-prefix-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #73 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：Independent15sourceSHA
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T121838Z-prefill-visible-prefix-gate",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T12:18:38.550745+00:00",
  "profile_id": "prefill_visible_prefix",
  "phase": "two_case_single_layer_correctness_timing",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "single_layer_small_signal_independent_review",
  "artifacts": "experiments/framework/20261021T121838Z-prefill-visible-prefix-gate",
  "conclusion": "Independent15sourceSHA;exit0 actualbackendbuilderKVwriter syntheticC3P2019KV16K+Q2048KV16K;alloutputbits/finite/padding/fullKV/RNG/1prefill/C2decodefallback pass;randomphysicalpages3negativeNaNpadding slots/reusedprefix16inPcase;onlyP2019timed32callsABBA wall12.594359734375to12.559617125ms0.27585848percent saved event12.491010189056396to12.434306144714355ms0.45395884percent saved;selected68fallback67/originalproxyrestored;retain smalllayersignal no graphfullrunneraccuracyserviceofficialclaim;fullpost12:25:01.258460UTC68MiB0closed"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T121838Z-prefill-visible-prefix-gate](../../../experiments/framework/20261021T121838Z-prefill-visible-prefix-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T121838Z-prefill-visible-prefix-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T121838Z-prefill-visible-prefix-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T121838Z-prefill-visible-prefix-gate/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T121838Z-prefill-visible-prefix-gate-control/postflight-full.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T121838Z-prefill-visible-prefix-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T121838Z-prefill-visible-prefix-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T121838Z-prefill-visible-prefix-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T121838Z-prefill-visible-prefix-gate/exit-code)
- 相关说明：[2026-10-22-visible-prefix-service](../../../analysis/2026-10-22-visible-prefix-service.md)；[2026-10-21-prefill-visible-prefix-implementation](../../../analysis/2026-10-21-prefill-visible-prefix-implementation.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
