<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T063949247282Z-prefill-lpt-graph-middle-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #311 · Prefill序列内CTA调序

- **尝试**：验证4K第二chunk是否同样改善拖尾。
- **改动**：CTA调序不改变context与K遍历。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-lpt.md)。
- **怎么测**：Q2048/KV4096、context2048，完整Graph ABBA及初始/换值逐位、原FP64硬门。
- **结果**：Q2048/KV4096、context2048对应4K第二chunk，完整Attention Graph Event1.755975→1.655632ms省5.7144%，wall1.759074→1.658530ms省5.7157%。初始/换值跨臂逐位、自臂Graph及原FP64硬门通过；DB/source/native和清理通过。保留已测早期chunk范围；旧Q2047/
- **是否保留**：保留已测第二chunk范围；不推广long或任意形状。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T063949247282Z-prefill-lpt-graph-middle-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T06:39:49.247282+00:00",
  "profile_id": "prefill-lpt",
  "phase": "LPT第二chunk完整Graph replay组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_lpt_middle_graph_positive_component",
  "artifacts": "experiments/framework/20261026T063949247282Z-prefill-lpt-graph-middle-component",
  "conclusion": "Q2048/KV4096、context2048对应4K第二chunk，完整Attention Graph Event1.755975→1.655632ms省5.7144%，wall1.759074→1.658530ms省5.7157%。初始/换值跨臂逐位、自臂Graph及原FP64硬门通过；DB/source/native和清理通过。保留已测早期chunk范围；旧Q2047/KV16384慢3.57%，long保持原核，不泛化任意prefix/形状，不定官方新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T063949247282Z-prefill-lpt-graph-middle-component](../../../experiments/framework/20261026T063949247282Z-prefill-lpt-graph-middle-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T063949247282Z-prefill-lpt-graph-middle-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T063949247282Z-prefill-lpt-graph-middle-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T063949247282Z-prefill-lpt-graph-middle-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T063949247282Z-prefill-lpt-graph-middle-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T063949247282Z-prefill-lpt-graph-middle-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
