<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T161135828367Z-prefill-stride-constexpr-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #281 · Prefill stride常量特化

- **尝试**：把长期活跃的stride常量化，减少分页整数计算和参数资源开销。
- **改动**：仅11项stride constexpr＋原int64寻址，不叠加log2/.cg；SGPR spill30→6、mul103→30，代价为布局编译变体。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-stride.md)。
- **怎么测**：M2047/KV16K、原normalized+Q-hoist，完整2D producer单ABBA/每窗16次；固定FP64门、自臂换值Graph与合法5项stride切换回原布局17项检查。单序列未覆盖非零页表行偏移。
- **结果**：旧数值/FP64/Graph与alternate17项通过，跨臂初始/换值逐位；Event8.371886→8.328763ms省0.5151%，wall慢0.5676%。
- **是否保留**：保留小GPU候选，生产官方入口准备中；模型收益未确认，不授105资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T161135828367Z-prefill-stride-constexpr-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-25T16:11:35.828367+00:00",
  "profile_id": "prefill-stride",
  "phase": "Prefill stride常量特化组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_stride_small_signal",
  "artifacts": "experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component",
  "conclusion": "当前normalized+Q-hoist中仅11项stride改constexpr并保留int64寻址，原浮点表达式/tile/页序不变，增加合法布局对应编译变体。M2047/KV16K，旧FP64/writer/换值Graph/输入RNG及alternate17项通过；初始/换值跨臂bits=true、maxabs0。alternate只改变原eligible允许的5项，单序列页表行stride仅身份覆盖，未数值覆盖非零行偏移。实际SGPR spill30→6、整数mul103→30、VGPR114不变，非所有spill为零。Event8.371886→8.328763ms省0.5151%，wall8.469649→8.517722ms慢0.5676%；候选第二次submit CPU4.34ms、其余1.3–1.5ms，原值保留。16:12:08 clean exit0，source/native未变、DB恢复。仅小GPU候选，模型/官方收益未确认；生产官方入口准备中，不借组件获得105资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T161135828367Z-prefill-stride-constexpr-component](../../../experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
