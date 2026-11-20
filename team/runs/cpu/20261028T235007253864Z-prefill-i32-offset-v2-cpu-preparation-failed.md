<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #472 · Prefill i32 offset 组件筛查

- **尝试**：用i32相对offset候选尝试重现171100的normal编译配置并检查编译门。
- **改动**：set_arg_attr因attrs值解码为list而停止；旧guard的BM128/BQ16/page32与目标BM256/BQ32/page16不符。 版本、命令和源码见下方原件；[方法记录](../../methods/prefill-i32-offset.md)。
- **怎么测**：仅CPU、CUDA API未调用；真实编译trace显示set_arg_attr收到错误的list值。目标BM256/BQ32/page16，旧guard为BM128/BQ16/page32。
- **结果**：i32-offset v2 CPU-only编译在set_arg_attr失败：ABI attrs把整数值解成list，Triton拒绝；未进入正常kernel编译。静态7项guard通过但锁定BM128/BQ16/page32，和目标BM256/BQ32/page16不符。
- **是否保留**：保留编译接口失败，不称kernel数值/性能负；guard不适用于实际目标形状。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T23:50:07.253864+00:00",
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
  "status": "prefill_i32_v2_compile_attrs_failed",
  "artifacts": "experiments/bundles/20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed",
  "conclusion": "i32-offset v2 CPU-only编译因set_arg_attr attrs类型错误停止；静态guard通过但其BM128/BQ16/page32范围与实际目标BM256/BQ32/page16不符。无CUDA调用或性能结论。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed](../../../experiments/bundles/20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
