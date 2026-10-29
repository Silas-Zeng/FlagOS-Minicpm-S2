<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #474 · Prefill i32 offset CPU 编译筛查

- **尝试**：验证v5按生产模块名修正后的A normal编译身份。
- **改动**：A仍未匹配171100 selected hash；严格拒绝，无GPU或性能结论。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-i32-offset.md)。
- **怎么测**：CPU-only；A normal identity不匹配，未授予生产或设备资格。
- **结果**：i32-offset v5 CPU-only完成A normal编译，但身份仍未匹配171100 selected kernel；保留严格身份门拒绝。
- **是否保留**：保留为CPU身份失败；无GPU、模型数值、吞吐或生产资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T00:06:55.051332+00:00",
  "profile_id": "prefill-i32-offset",
  "phase": "cpu_compile",
  "device": "CPU",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "prefill_i32_v5_normal_identity_mismatch",
  "artifacts": "experiments/bundles/20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed",
  "conclusion": "i32-offset v5 CPU-only正常编译后，A normal身份仍未匹配171100目标，按原门拒绝；无GPU、准确率或性能结果。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed](../../../experiments/bundles/20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
