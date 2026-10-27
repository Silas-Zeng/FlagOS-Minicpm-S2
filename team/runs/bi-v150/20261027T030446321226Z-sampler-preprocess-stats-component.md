<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T030446321226Z-sampler-preprocess-stats-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #357 · 采样转换与首遍统计融合

- **尝试**：保留原启动失败，只修入口源码路径后单独重试；无收益或数值结论。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：完整原件、精确命令、环境与收尾证据已回收。
- **结果**：首包f3e99d0a在候选执行前失败：入口PYTHONPATH只包含assets，导入安装旧vllm_fl，缺biv150_runtime，ImportError。cases/timings均空，尚无数值或性能结论，也不是生产框架报错。保留原包和26原件；下一包仅绑定main241765源码路径及复用既有身份检查，数学和候选不改。原owner已恢复DB并清理自有进程。
- **是否保留**：保留原启动失败，只修入口源码路径后单独重试；无收益或数值结论。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T030446321226Z-sampler-preprocess-stats-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T030446321226Z",
  "profile_id": "sampler-preprocess-stats",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "sampler_preprocess_entry_import_failure",
  "artifacts": "experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component",
  "conclusion": "首包f3e99d0a在候选执行前失败：入口PYTHONPATH只包含assets，导入安装旧vllm_fl，缺biv150_runtime，ImportError。cases/timings均空，尚无数值或性能结论，也不是生产框架报错。保留原包和26原件；下一包仅绑定main241765源码路径及复用既有身份检查，数学和候选不改。原owner已恢复DB并清理自有进程。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T030446321226Z-sampler-preprocess-stats-component](../../../experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
