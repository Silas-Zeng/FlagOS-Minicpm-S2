<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T090439643177Z-gqa-fused-append-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #366 · GQA尾段append融合

- **尝试**：只对私有尾slot省独立writer启动，不改BF16/页序/归约。实际编译VGPR增51超过预设预算后停止；数值和计时尚未运行，不称错误或实测慢，不扩展或放宽阈值。
- **改动**：相关实现 [comparison.json](../../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/archive-receipt.json)；[candidate.py](../../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/source/candidate.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：唯一N64/S2；完整链ABBA尚未开始，69原件保留。
- **结果**：尾段append融合编译成功；VGPR93→144超预设+16预算，SGPR spill0→50，shared8KiB不变。数值/计时均未运行，清理通过。
- **是否保留**：停止冻结实现，不放宽预算或扫参；非数值错误/实测慢。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T090439643177Z-gqa-fused-append-hotspot-component",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-27T09:04:39.643177+00:00",
  "profile_id": "gqa-fused-append",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_fused_append_resource_budget_stopped",
  "artifacts": "experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component",
  "conclusion": "私有尾slot的BF16 append并入GQA producer，拟省旧writer启动，原while/page16/FP/reducer不动。main56/807/native14f唯一N64/S2组件：实际候选编译成功，原baseline身份匹配；VGPR93→144（+51）超预设+16工程预算，SGPR64→99/spill0→50，shared8192B不变，于原checks/timings空时停止。数值/Graph与ABBA未运行，不称数值错误或实测慢，不据资源断言occupancy。原DB恢复、source/native不变及清理通过；69原件逐SHA回收。当前冻结实现停止，不调阈值/扫参，不接生产。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T090439643177Z-gqa-fused-append-hotspot-component](../../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
