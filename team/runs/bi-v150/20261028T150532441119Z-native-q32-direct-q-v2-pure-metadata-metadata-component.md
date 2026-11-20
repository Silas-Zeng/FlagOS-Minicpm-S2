<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T150532441119Z-native-q32-direct-q-v2-pure-metadata-metadata-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #435 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：Event省3.67184%、wall省0.849919%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T150532441119Z-native-q32-direct-q-v2-pure-metadata-metadata-component",
  "local_date": "2026-10-28",
  "utc_start": "20261028T150532441119Z",
  "profile_id": "directq-v2-pure-component",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_q32_direct_q_v2_pure_component_positive",
  "artifacts": "experiments/framework/20261028T150532441119Z-native-q32-direct-q-v2-pure-metadata-metadata-component",
  "conclusion": "pure2048 metadata组件ABBA完整、15项硬门通过；Event省3.67184%、wall省0.849919%。仅组件信号，非混合/长上下文/模型/官方成绩。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T150532441119Z-native-q32-direct-q-v2-pure-metadata-metadata-component](../../../experiments/framework/20261028T150532441119Z-native-q32-direct-q-v2-pure-metadata-metadata-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
