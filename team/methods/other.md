<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 其它登记与控制记录

没有足够字段继续归类的登记；不补猜实验结论。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T121838Z-prefill-visible-prefix-gate](../runs/bi-v150/20261021T121838Z-prefill-visible-prefix-gate.md)（登记#73）：Independent15sourceSHA **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T121701Z-prefill-v-late-gate](../runs/bi-v150/20261022T121701Z-prefill-v-late-gate.md)（登记#137）：wall11.106083→11.267372ms（慢1.4523%），event10.993639→11.136706ms（慢1.3014%） **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T122216Z-current-combination-context16k-long-baseline](../runs/bi-v150/20261022T122216Z-current-combination-context16k-long-baseline.md)（登记#138）：输出/32请求/c64，32成功0失败，219.973985s、总2532.372182 tok/s、输出148.963070 tok/s、TTFT62352.5218ms **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261022T123334Z-last-layer-tail-gate](../runs/bi-v150/20261022T123334Z-last-layer-tail-gate.md)（登记#139）：失败：RowParallelLinear的disable_tp未免除ModelWeightParameter对TP组的依赖，真实TP组未初始化 **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T124358Z-last-layer-tail-v2-gate](../runs/bi-v150/20261022T124358Z-last-layer-tail-v2-gate.md)（登记#140）：123334失败与v2资产保留 **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T124857Z-biv150-resource-query](../runs/bi-v150/20261022T124857Z-biv150-resource-query.md)（登记#141）：实际SDK只读属性查询exit0：BI-V150/32GiB/16SM/warp64 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T125135Z-current-combination-context16k-long-baseline](../runs/bi-v150/20261022T125135Z-current-combination-context16k-long-baseline.md)（登记#142）：32成功0失败，219.995999768s、总2532.118768tok/s、输出148.948163tok/s、TTFT62317.2833ms **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261022T130038Z-prefill-v-late-cache-gate](../runs/bi-v150/20261022T130038Z-prefill-v-late-cache-gate.md)（登记#143）：失败，下一轮只修source pin **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T130457Z-prefill-v-late-cache-v2-gate](../runs/bi-v150/20261022T130457Z-prefill-v-late-cache-v2-gate.md)（登记#144）：wall慢0.27180%、event仅快0.02373%，不能认定收益，当前不集成；负结果不外推其他A+B **是否保留：** 未集成；失败或无收益记录保留。

## 未记录

- [20261021T035155Z-attention-control](../runs/unrecorded/20261021T035155Z-attention-control.md)（登记#7）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T035322Z-attention-control](../runs/unrecorded/20261021T035322Z-attention-control.md)（登记#8）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T035611Z-mixed-control](../runs/unrecorded/20261021T035611Z-mixed-control.md)（登记#9）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
