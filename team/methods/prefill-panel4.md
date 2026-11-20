<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 长prefill四面板完整Attention

旧main594 Q16组件省2.2226%；新main241 Q32/w16已合并，真实同配置panel4组合反而慢12.43337%，数值门通过但停止生产接入；旧边界准备保留未执行。

相关代码：[results.json](../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/results.json)；[archive-receipt.json](../../experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/archive-receipt.json)；[results.json](../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/results.json)；[archive-receipt.json](../../experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T180225915687Z-prefill-panel4-long-component](../runs/bi-v150/20261026T180225915687Z-prefill-panel4-long-component.md)（登记#344）：保留旧Q16组件证据；新main241 Q32组合已负，停止生产接入，原边界不再排队。 **是否保留：** 保留旧Q16组件证据；新main241 Q32组合已负，停止生产接入，原边界不再排队。
- [20261026T183816740050Z-prefill-q32-panel4-long-component](../runs/bi-v150/20261026T183816740050Z-prefill-q32-panel4-long-component.md)（登记#346）：停止panel4生产接入；旧Q16三项边界未启动且暂缓，新main241成为后续研究基础。 **是否保留：** 停止panel4生产接入；旧Q16三项边界未启动且暂缓，新main241成为后续研究基础。
