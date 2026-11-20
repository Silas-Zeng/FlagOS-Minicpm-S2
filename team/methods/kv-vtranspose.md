<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 纯BF16页内V布局

完整组件慢1.33%，停止当前实现。

相关代码：[archive-receipt.json](../../experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component](../runs/bi-v150/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component.md)（登记#355）：纯BF16页内V转置：K保持NHD，V改dim×slot；原GQA只改两处V维度寻址，并实作对应writer，未压缩或增持久容量。位型、8项数值/Graph及writer换值/换slot/负slot门通过，有限输入跨臂逐位一致。完整writer+GQA+reducer Graph ABBA Even **是否保留：** 停止当前实现，不进生产。
