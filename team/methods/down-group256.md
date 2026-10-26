<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# down K256分组INT8探索

独立W8A8原型首个CPU INT64精确整数门失败，未计时；保留exit1，不推进依赖该门的gate融合，不放宽容差或改框架凑过。不是完整量化/模型方案，也不泛化其它INT8实现。

相关代码：[result.json](../../experiments/framework/20261026T062610126686Z-biv150-down-group256-component/result.json)；[source](../../experiments/framework/20261026T062610126686Z-biv150-down-group256-component/source)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T062610126686Z-biv150-down-group256-component](../runs/bi-v150/20261026T062610126686Z-biv150-down-group256-component.md)（登记#313）：独立down K256分组W8A8原型在group_integer_probe对CPU INT64精确参考失败，原报错为INT8 dot ABI/布局失败、精确否决；cases/timings为空，立即停止，不进入性能/整模，不推进依赖该门的gate融合。使用layer20 down真实权重与合成激 **是否保留：** 停止当前错误实现；不推进依赖融合、不放宽容差。
