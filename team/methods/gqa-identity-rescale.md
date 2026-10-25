<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA恒等rescale跳过

仅当同组8头的finite最大值严格不变时省去rescale，其他分支与原reducer保留。N33/B40/S16及B32/S4分别完成8组数值/Graph检查，Graph ABBA耗时观察分别+2.308%/+1.058%；未见收益，不推进模型/官方。B32首次空padding验证器异常单列，独立v3修验证器后重测，未修改候选数学。均为随机输入组件，非实际激活重放。

相关代码：[kernel.diff](../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/kernel.diff)；[worker.py](../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/worker.py)；[padding-source.json](../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/padding-source.json)；[worker.diff](../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/source/worker.diff)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T090542870699Z-gqa-identity-rescale-v2-b32-component](../runs/bi-v150/20261025T090542870699Z-gqa-identity-rescale-v2-b32-component.md)（登记#255）：B32无padding，验证器空切片.all()触发ZeroDivisionError；完整数值检查和计时未形成，不判候选数值失败。 **是否保留：** 保留验证器失败；独立v3只修空padding检查，后继结果另列。
- [20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component](../runs/bi-v150/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component.md)（登记#256）：N33/B40/S16：8组数值/Graph检查通过，event1.280913→1.310480ms（耗时+2.308%）；随机组件负信号。 **是否保留：** 保留负结果，不推进模型或官方测试；不将局部差异外推端到端。
- [20261025T091037578775Z-gqa-identity-rescale-v2-b32-component](../runs/bi-v150/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component.md)（登记#257）：v3仅修空padding检查；B32/S4的8组数值/Graph通过，event1.029569→1.040463ms（+1.058%），wall+0.949%。 **是否保留：** 两档均未见收益，收口保留原件，不推进模型或官方测试。
