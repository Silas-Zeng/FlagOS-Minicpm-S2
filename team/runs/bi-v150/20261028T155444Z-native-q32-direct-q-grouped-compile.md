<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T155444Z-native-q32-direct-q-grouped-compile

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #440 · CoreX原生Prefill Attention：Q32／Q64

- **尝试**：复核direct-Q＋grouped四行max组合是否具备开展一次纯组件测试的编译资格。
- **改动**：仅CPU编译和独立资源审阅；批准范围限一次pure2048组件A/B。 版本、命令和源码见下方原件；[方法记录](../../methods/native-q32-transfer.md)。
- **怎么测**：CPU编译＋独立FP DAG/资源审阅；SGPR99/VGPR107、shared64KiB、scalar spill 2、无VGPR/private spill。
- **结果**：独立CPU编译审阅GO，仅授权一次pure2048组件A/B；无GPU数值、性能、模型或生产资格。
- **是否保留**：保留CPU编译与审阅证据；只允许指定组件实验，不继承151702资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T155444Z-native-q32-direct-q-grouped-compile",
  "local_date": "2026-10-28",
  "utc_start": "20261028T155444Z",
  "profile_id": "directq-grouped-compile",
  "phase": "diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_q32_direct_q_grouped_compile_cpu_go",
  "artifacts": "experiments/diagnostics/20261028T155444Z-native-q32-direct-q-grouped-compile",
  "conclusion": "direct-Q＋grouped四行max通过CPU编译与独立FP DAG/资源审阅，批准仅一次pure2048增量组件A/B（A=direct-Q v2，B=组合）；SGPR99/VGPR107、64KiB shared、2处scalar spill、无VGPR/private spill。未跑GPU，无数值/性能/模型/生产/官方资格，也不继承151702资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T155444Z-native-q32-direct-q-grouped-compile](../../../experiments/diagnostics/20261028T155444Z-native-q32-direct-q-grouped-compile)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
