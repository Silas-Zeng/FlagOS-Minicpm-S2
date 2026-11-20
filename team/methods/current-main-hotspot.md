<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 当前main526热点分析

16K自然mixed4/FULL8独立诊断，原runner/P/Q/native和服务参数保留。mixed后2步Attention约68.08%可见GPU；FULL只见整图，不能拆内部占比。用于选择优化方向，不报吞吐收益。

相关代码：[072151-analysis-v2.json](../../analysis/current-main-hotspot-20261025/072151-analysis-v2.json)；[072151-attribution-check.json](../../analysis/current-main-hotspot-20261025/072151-attribution-check.json)；[analyze.py](../../analysis/current-main-hotspot-20261025/analyze.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T072151Z-current-main-hotspot-16384](../runs/bi-v150/20261025T072151Z-current-main-hotspot-16384.md)（登记#251）：mixed4中2D Attention总763.40ms，后2步均236.74ms/约68.08%可见GPU，GEMM稳定80.26ms/步 **是否保留：** 保留有效当前轨迹；优先验证prefill Attention候选，不把FULL图壳或几步比例外推成全负载预算。
