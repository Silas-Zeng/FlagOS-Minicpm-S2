<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T122551Z-w8a8-mitigation-arms

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #130 · int8 与 W8A8 决策测量

- **尝试**：真实形状上的 int8 GEMM、W8A16、_int_mm+融合 epilogue 及 QDQ 精度模拟；负结果与候选并存，不混用证据级别。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：准确率门；输入 / 输出 / 并发 / 请求数：0 / 0 / 8 / 24。
- **结果**：缓解臂同协议（24 题、1024 token、greedy、bf16 参考臂在本 run 内）：去掉 down_proj（252 层）与只量化 MLP（126 层）都是 gold 13/24、最终答案一致率 0.95833、各 1 题翻转，与“只量化权重”同级
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T122551Z-w8a8-mitigation-arms",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:25:51+00:00",
  "profile_id": "int8_decision",
  "phase": "accuracy_offline_greedy",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "0",
  "output_len": "0",
  "concurrency": "8",
  "num_prompts": "24",
  "profiler": "false",
  "status": "complete_offline_mitigation_screen",
  "artifacts": "experiments/operator/20261022T122551Z-w8a8-mitigation-arms",
  "conclusion": "缓解臂同协议（24 题、1024 token、greedy、bf16 参考臂在本 run 内）：去掉 down_proj（252 层）与只量化 MLP（126 层）都是 gold 13/24、最终答案一致率 0.95833、各 1 题翻转，与“只量化权重”同级；权重分组 64 全层（294 层）仍 gold 11/24、一致率 0.875。3 次翻转里 2 次是该臂没有产出答案（no_final_answer 由 bf16 的 7 升至 9），1 次输出模板占位 ANSWER，均属截断/格式中断而非算错。据此把自研 W8A8 补丁默认层集定为 qkv_proj,o_proj,gate_up_proj，down_proj 与 lm_head 保持 bf16。本目录 int8-shapes.json 是 #127 引用的完整形状数据（同一次运行产出）。端到端与官方 Level-3 未跑，不据此声称可提交。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T122551Z-w8a8-mitigation-arms](../../../experiments/operator/20261022T122551Z-w8a8-mitigation-arms)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
