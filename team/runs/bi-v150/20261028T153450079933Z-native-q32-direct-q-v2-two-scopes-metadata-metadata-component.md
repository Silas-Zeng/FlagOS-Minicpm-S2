<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T153450079933Z-native-q32-direct-q-v2-two-scopes-metadata-metadata-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #438 · Attention 分流与 launch

- **尝试**：prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：Event分别省0.967076%/3.375566%，mixed wall慢1.110675%，long wall省4.768338%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T153450079933Z-native-q32-direct-q-v2-two-scopes-metadata-metadata-component",
  "local_date": "2026-10-28",
  "utc_start": "20261028T153450079933Z",
  "profile_id": "directq-v2-mixed-long-component",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_q32_direct_q_v2_mixed_long_component_positive_wall_mixed_negative",
  "artifacts": "experiments/framework/20261028T153450079933Z-native-q32-direct-q-v2-two-scopes-metadata-metadata-component",
  "conclusion": "mixed-step125与long2047/KV16384共34硬门、完整ABBA通过；Event分别省0.967076%/3.375566%，mixed wall慢1.110675%，long wall省4.768338%。组件信号，不称官方收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T153450079933Z-native-q32-direct-q-v2-two-scopes-metadata-metadata-component](../../../experiments/framework/20261028T153450079933Z-native-q32-direct-q-v2-two-scopes-metadata-metadata-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
