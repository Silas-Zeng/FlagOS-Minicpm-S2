<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #336 · GQA标量KV页基址与动态for组合

- **尝试**：scalar＋while慢0.38635%且SME未生效；for＋scalar＋一维i64 stages1实际SME8却慢10.73864%；stages2实际async-copy4/SME16仍慢27.63241%。三项原8门/逐位通过，均停止不接模型，机制生成不等于净收益。
- **改动**：相关实现 [kernel.diff](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/source/kernel.diff)；[results.json](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/archive-receipt.json)；[gqa-scalar-page-base-114133.json](../../../analysis/main6971-084521-nodes/gqa-scalar-page-base-114133.json)；[kernel.diff](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/source/kernel.diff)；[results.json](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/archive-receipt.json)；[gqa-for-scalar-i64-134937.json](../../../analysis/main6971-084521-nodes/gqa-for-scalar-i64-134937.json)；[kernel.diff](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/source/kernel.diff)；[results.json](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/archive-receipt.json)；[gqa-for-scalar-i64-s2-141615.json](../../../analysis/main6971-084521-nodes/gqa-for-scalar-i64-s2-141615.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：复用main6971实际N64/S2及4K观察长度的合成Q/KV组件；原8门后完整producer＋reducer 16-call Graph ABBA，baseline stages1、candidate stages2，单项非参数扫描。
- **结果**：8门/逐位通过；实际stages2、async-copy4/SME16，完整Graph慢27.63241%，停止不扫stage。
- **是否保留**：停止当前SME流水路线并保留数值通过、机制生成与净负结果；不以异步指令数或低寄存器替代收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T14:16:15.226388+00:00",
  "profile_id": "gqa-for-scalar-i64-s2",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_for_scalar_i64_s2_negative_component",
  "artifacts": "experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component",
  "conclusion": "在已测for＋标量页基址＋一维int64组合上仅candidate num_stages=2；原生产A保持1，reducer/数学/页序/布局不变。8类原门及跨臂逐位通过，完整producer＋reducer Graph Event0.541960925→0.691717803ms，慢27.63241%，wall慢27.18074%。实际软件流水生成TTGIR async-copy4、LLVM/ASM SME各16条，shared8192→18432，仍无净益；停止stages2，不扫stages3/不接模型。DB/source/native及设备清理通过，无官方/105或新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
