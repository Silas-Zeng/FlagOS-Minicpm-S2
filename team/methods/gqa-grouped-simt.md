<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA grouped SIMT页内归约

固定page16/N33/B40/S16/KV16K，把QK/PV改为FP32广播归约并保留P先BF16舍入与原reducer，尝试减少TCU填充/布局开销；增加SIMT算术及广播成本。8类数值、FP64抽样、Graph/输入RNG和实际w8无dot/MMA/无3D全局scratch机制通过。Event1.279744→44.634184ms（34.8774倍），wall1.286918→44.640352ms（34.6878倍），明显无净收益；SGPR/VGPR均无spill也不保证快。停止此路线、整模与扫参，预备模型入口不推进；旧0bf9/526组件不是新main34942的成绩。

相关代码：[candidate.py](../../experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component/source/candidate.py)；[results.json](../../experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component/results.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T181007536717Z-gqa-grouped-simt-hotspot-component](../runs/bi-v150/20261025T181007536717Z-gqa-grouped-simt-hotspot-component.md)（登记#285）：8类原数值/FP64/Graph及实际SIMT机制通过；Event1.279744→44.634184ms（34.8774倍），wall34.6878倍。 **是否保留：** 保留明显负结果，停止整模与扫参，不推进已准备的模型入口；非数值错误，不授官方/105资格。
