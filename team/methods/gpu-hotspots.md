<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 当前版本GPU热点

复用原轨迹并按需补短native诊断；GPU路径占比只用于选择下一实验，不作吞吐成绩。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T114435Z-current-mixed-native-diagnostic](../runs/bi-v150/20261022T114435Z-current-mixed-native-diagnostic.md)（登记#135）：可见kernel累计1063.156218ms：2D Attention640.380398ms/60.2339%，GEMM337.191759ms/31.7161%，3D2.6891%，reduce0.1245% **是否保留：** 待确认；通过某项检查不自动等于优化保留。
