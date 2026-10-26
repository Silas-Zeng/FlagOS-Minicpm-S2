<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #335 · GQA标量KV页基址与动态for组合

- **尝试**：scalar＋while慢0.38635%且SME未生效；for＋scalar＋一维i64 stages1实际SME8却慢10.73864%；stages2实际async-copy4/SME16仍慢27.63241%。三项原8门/逐位通过，均停止不接模型，机制生成不等于净收益。
- **改动**：相关实现 [kernel.diff](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/source/kernel.diff)；[results.json](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/archive-receipt.json)；[gqa-scalar-page-base-114133.json](../../../analysis/main6971-084521-nodes/gqa-scalar-page-base-114133.json)；[kernel.diff](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/source/kernel.diff)；[results.json](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/archive-receipt.json)；[gqa-for-scalar-i64-134937.json](../../../analysis/main6971-084521-nodes/gqa-for-scalar-i64-134937.json)；[kernel.diff](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/source/kernel.diff)；[results.json](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/results.json)；[archive-receipt.json](../../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/archive-receipt.json)；[gqa-for-scalar-i64-s2-141615.json](../../../analysis/main6971-084521-nodes/gqa-for-scalar-i64-s2-141615.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：复用main6971实际N64/S2、4K观察长度多重集的合成Q/KV组件；只组合三个编译条件，FP/页序/reducer/参数不变。计时前完成原数值检查，再完整producer＋reducer Graph 16-call ABBA，非官方性能或模型准确率。
- **结果**：8门/逐位通过；实际SME LLVM8/ASM8，完整Graph慢10.73864%，停止。资源下降不是收益证明，无官方/105。
- **是否保留**：停止本组合及模型扩展；保留真实SME已生成、数值通过与净性能负证据，不以指令成功或资源下降继续盲扫。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T13:49:37.447894+00:00",
  "profile_id": "gqa-for-scalar-i64",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_for_scalar_i64_negative_component",
  "artifacts": "experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component",
  "conclusion": "动态for＋标量页基址＋一维int64后expand，保持原NHD/page16/FP顺序与producer＋reducer；8类门、有限跨臂逐位硬门及非有限原语义诊断通过。完整Graph Event0.541995287→0.600198209ms，慢10.73864%，wall慢10.42853%，停止不接模型。LLVM/ASM实际SME指令均0→8，完整页路径启用而tail原路；VGPR93→81、SGPR64→84、spill均0、shared8192→10240，不能仅凭资源或指令认定收益/精确慢因。无官方、105或新基线，DB/source/native和清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
