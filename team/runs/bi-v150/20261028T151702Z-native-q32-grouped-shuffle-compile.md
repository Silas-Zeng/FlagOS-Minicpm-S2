<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T151702Z-native-q32-grouped-shuffle-compile

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #436 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：grouped四行max shuffle CPU编译检查通过、0 spill
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T151702Z-native-q32-grouped-shuffle-compile",
  "local_date": "2026-10-28",
  "utc_start": "20261028T151702Z",
  "profile_id": "grouped-shuffle-compile",
  "phase": "diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_q32_grouped_shuffle_compile_only",
  "artifacts": "experiments/diagnostics/20261028T151702Z-native-q32-grouped-shuffle-compile",
  "conclusion": "grouped四行max shuffle CPU编译检查通过、0 spill；仅编译/源码证明，无GPU数值或性能资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T151702Z-native-q32-grouped-shuffle-compile](../../../experiments/diagnostics/20261028T151702Z-native-q32-grouped-shuffle-compile)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
