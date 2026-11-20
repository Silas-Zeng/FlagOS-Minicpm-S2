<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T130418879497Z-lm-head-paired-gemv-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #268 · LM-head双行GEMV

- **尝试**：用双行GEMV减少M2 LM-head矩阵乘开销。
- **改动**：唯一BN32/BK256/w8，随机权重组件；未加载框架/native，不补造二者身份。 版本、命令和源码见下方原件；[方法记录](../../methods/lm-head-paired-gemv.md)。
- **怎么测**：随机BF16 M2/N130560/K2048，对照原FlagGems linear固定配置；CPU FP64参考及ABBA完整词表输出计时，不含分配/参考。未加载框架/native。
- **结果**：数值/变指针内容/guard/RNG通过；Event0.834885→2.045513ms、wall0.892245→2.076413ms，明显负。
- **是否保留**：停止唯一配置，不扩调参或接模型；保存负结果，不建优化PR。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T130418879497Z-lm-head-paired-gemv-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T13:04:18.879497+00:00",
  "profile_id": "lm-head-paired-gemv",
  "phase": "独立算子组件对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "lm_head_paired_gemv_negative",
  "artifacts": "experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component",
  "conclusion": "独立随机M2/N130560/K2048 BF16组件，对照原FlagGems linear固定配置与唯一BN32/BK256/w8 paired-GEMV。FP64参考、换指针内容、guard/RNG通过；ABBA Event0.834885→2.045513ms、wall0.892245→2.076413ms，明显更慢。未加载框架模型或native，不补造框架/native身份，不授予模型资格。DB恢复及清理通过；停止方案，不扩tiling或创建优化PR。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T130418879497Z-lm-head-paired-gemv-component](../../../experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
