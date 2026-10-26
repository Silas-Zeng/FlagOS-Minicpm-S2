<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA动态for与二维span

根据main6971真实Graph热点，保持原page16/数学顺序/reducer，仅改变循环形式与合法跨度；N64/S2八类门通过，但完整组件慢75.05%，停止。

相关代码：[kernel.diff](../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/source/kernel.diff)；[results.json](../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/results.json)；[ir-candidate](../../experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/ir-candidate)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T095708239358Z-gqa-for-span-hotspot-component](../runs/bi-v150/20261026T095708239358Z-gqa-for-span-hotspot-component.md)（登记#324）：原page16/FP顺序的动态for＋二维span，N64/S2用真实4K观测长度多重集、合成激活。8类原数值/FP64/Graph/写入门通过，完整producer＋原reducer Event0.541187257→0.947350353ms，慢75.0504%，wall慢74.0019%。停止 **是否保留：** 停止本候选，不扩形状或模型，不合并；复用原负结果，不重跑。
