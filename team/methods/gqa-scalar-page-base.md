<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA标量KV页基址

标量KV页基址＋二维span，保原while/page16/FP顺序；8类门及跨臂逐位通过，完整组件Event慢0.38635%，停止。SGPR spill75为lane保存，非HBM；实际SME传输仍0。for＋scalar组合机制尚未验证。

相关代码：[kernel.diff](../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/source/kernel.diff)；[results.json](../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/results.json)；[archive-receipt.json](../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/archive-receipt.json)；[gqa-scalar-page-base-114133.json](../../analysis/main6971-084521-nodes/gqa-scalar-page-base-114133.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T114133003627Z-gqa-scalar-page-base-hotspot-component](../runs/bi-v150/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component.md)（登记#333）：8类门及跨臂逐位通过；Event0.542196542→0.544291317ms，慢0.38635%，停止。SGPR spill75为lane保存非HBM；实际SME仍0，for＋scalar未验证。 **是否保留：** 停止当前scalar-page-base实现，不进模型或合并；保留正确性通过及小幅负结果，不把一次ABBA写稳定因果。for＋scalar尚未实现验证，不自动列为已获益组合。
