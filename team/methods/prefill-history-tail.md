<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill历史区间与causal尾块分离

首run私有Q-hoist适配失败；v2实际消除loop Q读取及SGPR spill，但跨臂逐位门失败，未计时，停止该候选。FP64通过不覆盖数值不变要求。

相关代码：[source](../../experiments/framework/20261026T090943131971Z-prefill-history-tail-long-component/source)；[source](../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/source)；[results.json](../../experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/results.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T090943131971Z-prefill-history-tail-long-component](../runs/bi-v150/20261026T090943131971Z-prefill-history-tail-long-component.md)（登记#321）：完整历史loop＋至多两个causal尾块已编译；私有Q-hoist因allocation/loop/load顺序守卫fallback。两臂优化选中检查拒绝，尚未进入跨臂/FP64/Graph或计时；清理通过。 **是否保留：** 保留编译变换适配失败；只用实际IR定位最小修正，不放宽正确性门或修改生产数学。
- [20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component](../runs/bi-v150/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component.md)（登记#323）：v2按真实IR复用已有Q fragment，selected1/fallback0、两臂LLVM循环Q读0。SGPR104→90/spill6→0；两臂FP64门通过，但跨臂逐位失败，max_abs0.0001220703125。违反本方法数值不变要求，未计时，停止当前候选。 **是否保留：** 停止当前候选，不放宽逐位门、不继续修优化或进模型；不能称主线错误/准确率下降，保留首次失败。
