<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Attention next-K寄存器预取

在已测affine＋Q-hoist组件上，提前加载下一tile的K以尝试覆盖PV计算。首次逐位/guard/KV/RNG/Q检查通过，原ASM定位门失败、未计时；CPU后核定位到真实load，但其8条路径均在首PV前遇wait/barrier，预期重叠机制不成立，停止本实现。不是数值或已测性能失败。

相关代码：[kernel.diff](../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/source/kernel.diff)；[worker.py](../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/source/worker.py)；[result.json](../../experiments/framework/20261025T085807255866Z-attention-next-k-register-component/analysis/posthoc-cpu/result.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T085807255866Z-attention-next-k-register-component](../runs/bi-v150/20261025T085807255866Z-attention-next-k-register-component.md)（登记#254）：首次逐位/guard/KV/RNG/Q通过；ASM定位门失败，未计时。CPU后核发现实际PV前wait/barrier，重叠机制NO-GO。 **是否保留：** 停止本实现；保留原失败与独立CPU后核，不宣称数值失败或性能回退。
