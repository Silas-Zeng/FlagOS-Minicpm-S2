<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T183816740050Z-prefill-q32-panel4-long-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #346 · 长prefill四面板完整Attention

- **尝试**：旧main594 Q16组件省2.2226%；新main241 Q32/w16已合并，真实同配置panel4组合反而慢12.43337%，数值门通过但停止生产接入；旧边界准备保留未执行。
- **改动**：相关实现 [results.json](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/archive-receipt.json)；[results.json](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：精确命令、源码、原始CSV/日志和清理见本轮原件。
- **结果**：停止panel4生产接入；旧Q16三项边界未启动且暂缓，新main241成为后续研究基础。
- **是否保留**：停止panel4生产接入；旧Q16三项边界未启动且暂缓，新main241成为后续研究基础。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T183816740050Z-prefill-q32-panel4-long-component",
  "local_date": "2026-10-27",
  "utc_start": "2026-10-26T18:38:16.740050+00:00",
  "profile_id": "prefill-panel4",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "main241_q32_panel4_negative",
  "artifacts": "experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component",
  "conclusion": "PR47合并后以main241真实Q32/w16为A，Q2047/KV16384；B同tile/warp加入四个K panel及完整reducer。实际Policy/Manager/hash绑定、初始与换值独立FP64/fullclose、Graph及输入/RNG/guard通过；非逐位。暖JIT完整双核ABBA 6.559703588→7.375295639ms，耗时增加12.43337%，wall增加13.98933%；68124160B scratch读写及reducer计入。source/native/DB/9031清理通过。停止该组合，不扫参数或进生产。旧Q16组件2.2226%仅保留历史，不能覆盖新Q32或继承到组合。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T183816740050Z-prefill-q32-panel4-long-component](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
