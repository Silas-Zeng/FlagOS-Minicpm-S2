<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA stride常量折叠

仅将5个K/V stride参数声明为constexpr，保留原cache策略、数学和reducer。N33/B40/S16、KV16K原8组数值/换值Graph边界和alternate-stride13项通过；总整数乘法27→13、页地址关联乘法12→0。Event省−0.0410%、wall省+0.0454%，无净收益，停止，不扩形状或进入模型。

相关代码：[kernel.diff](../../experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component/source/kernel.diff)；[worker.py](../../experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component/source/worker.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T134407482450Z-gqa-kv-stride-main-hotspot-component](../runs/bi-v150/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component.md)（登记#272）：8组数值/Graph及alternate-stride13项通过；整数mul27→13，Event1.277992→1.278517ms，wall1.284104→1.283520ms，无净收益。 **是否保留：** 保留机制和无收益结果，收口；不扩形状或进入模型，不创建优化PR。
