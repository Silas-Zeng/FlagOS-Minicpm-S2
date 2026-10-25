<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T085807255866Z-attention-next-k-register-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #254 · Attention next-K寄存器预取

- **尝试**：在已测affine＋Q-hoist组件上，提前加载下一tile的K以尝试覆盖PV计算。首次逐位/guard/KV/RNG/Q检查通过，原ASM定位门失败、未计时；CPU后核定位到真实load，但其8条路径均在首PV前遇wait/barrier，预期重叠机制不成立，停止本实现。不是数值或已测性能失败。
- **改动**：相关实现 [kernel.diff](../../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/source/kernel.diff)；[worker.py](../../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/source/worker.py)；[result.json](../../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/analysis/posthoc-cpu/result.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实affine＋Q-hoist对照；首次组件检查后在ASM定位门退出。CPU后核分析已回收IR，未启动GPU或换页复验。
- **结果**：首次逐位/guard/KV/RNG/Q通过；ASM定位门失败，未计时。CPU后核发现实际PV前wait/barrier，重叠机制NO-GO。
- **是否保留**：停止本实现；保留原失败与独立CPU后核，不宣称数值失败或性能回退。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T085807255866Z-attention-next-k-register-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T08:58:07.255866+00:00",
  "profile_id": "attention-next-k",
  "phase": "Attention next-K组件机制验证",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "next_k_mechanism_no_go",
  "artifacts": "experiments/framework/20261025T085807255866Z-attention-next-k-register-component",
  "conclusion": "next-K首次输出逐位/finite/guard、KV/RNG不变及双侧Q-hoist通过；原ASM定位器未识别跨行load源码位置而退出，未计时、未做换页复验。独立CPU后核修正定位范围后，真实8条load路径均在首PV前遇wait/barrier，预期访存重叠机制NO-GO。停止本实现，保留原exit1与posthoc CPU分析；这不是数值失败，也没有性能回退测量。源码/native未变、DB恢复及清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T085807255866Z-attention-next-k-register-component](../../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
