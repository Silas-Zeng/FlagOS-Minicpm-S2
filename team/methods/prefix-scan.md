<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 公共前缀扫描

在实际不支持cascade的后端中检查公共前缀统计成本；观察诊断与跳过扫描的真实服务结果分开记录。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T173203Z-prefix-cost-single16k-observe](../runs/bi-v150/20261022T173203Z-prefix-cost-single16k-observe.md)（登记#153）：1成功0失败 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T174402Z-no-cascade-prefix-candidate-single16k](../runs/bi-v150/20261022T174402Z-no-cascade-prefix-candidate-single16k.md)（登记#154）：吞吐+0.201392%、TTFT−0.290278%、TPOT−0.018328%不能认作因果或稳定收益 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T174712Z-no-cascade-prefix-baseline-single16k](../runs/bi-v150/20261022T174712Z-no-cascade-prefix-baseline-single16k.md)（登记#155）：1成功0失败 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
