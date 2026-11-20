<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T053309258487Z-biv150-down-small-integration-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #301 · BI-V150特定形状GEMM

- **尝试**：验证本条所述固定形状和新增实现。
- **改动**：改动及精确命令见该run源码和manifest/command原件。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：复用真实生产ABI/原数值门，新增改动单独验证；不重复旧测试。
- **结果**：生产接线已通过down M1/2/8、M9和O/QKV等8项；测试读取checkpoint不存在的gate_up合并键后KeyError停止，原权重实际分gate/up保存。这是测试构造错误，不是框架或候选数值错误；修测试后另run，不改原日志。DB207f/设备清理通过。
- **是否保留**：修读取器后另run，保留原件；不当框架数值错误。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T053309258487Z-biv150-down-small-integration-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T05:33:09.258487+00:00",
  "profile_id": "shape-gemm",
  "phase": "SplitK8接线首次测试读取器失败",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "five_test_weight_lookup_error",
  "artifacts": "experiments/framework/20261026T053309258487Z-biv150-down-small-integration-component",
  "conclusion": "生产接线已通过down M1/2/8、M9和O/QKV等8项；测试读取checkpoint不存在的gate_up合并键后KeyError停止，原权重实际分gate/up保存。这是测试构造错误，不是框架或候选数值错误；修测试后另run，不改原日志。DB207f/设备清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T053309258487Z-biv150-down-small-integration-component](../../../experiments/framework/20261026T053309258487Z-biv150-down-small-integration-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T053309258487Z-biv150-down-small-integration-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T053309258487Z-biv150-down-small-integration-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T053309258487Z-biv150-down-small-integration-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T053309258487Z-biv150-down-small-integration-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T053309258487Z-biv150-down-small-integration-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
