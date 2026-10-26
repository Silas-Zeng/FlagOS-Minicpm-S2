<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T180225915687Z-prefill-panel4-long-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #344 · 长prefill四面板完整Attention

- **尝试**：旧main594 Q16组件省2.2226%；新main241 Q32/w16已合并，真实同配置panel4组合反而慢12.43337%，数值门通过但停止生产接入；旧边界准备保留未执行。
- **改动**：相关实现 [results.json](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/archive-receipt.json)；[results.json](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：精确命令、版本及原始结果见本轮manifest/state、source和日志。
- **结果**：保留旧Q16组件证据；新main241 Q32组合已负，停止生产接入，原边界不再排队。
- **是否保留**：保留旧Q16组件证据；新main241 Q32组合已负，停止生产接入，原边界不再排队。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T180225915687Z-prefill-panel4-long-component",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-26T18:02:25.915687+00:00",
  "profile_id": "prefill-panel4",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "594ae2a9d17aadc4587ad54ade2b34e17f4af990",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "prefill_panel4_long_positive",
  "artifacts": "experiments/framework/20261026T180225915687Z-prefill-panel4-long-component",
  "conclusion": "main594长prefill Q2047/KV16384/ctx14337，原BM128/Q16/T64/w8s1分四个K panel，split-major FP32 partial及8-head reducer。原writer、初始/换值独立FP64、全输出close、双核Graph换值、输入/RNG/guard通过；归约树改变，非逐位。直接暖JIT唯一ABBA完整双核Event 8.304069→8.119503ms，单组省2.222603%，wall省2.086496%。新增68124160B workspace及全部读写/归约计入；分配在计时外，不声称生产容量或L2命中已证。DB/source/native及设备清理通过。保留，先补新分界边界和单workspace生产接线；尚无模型/105/官方资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T180225915687Z-prefill-panel4-long-component](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
