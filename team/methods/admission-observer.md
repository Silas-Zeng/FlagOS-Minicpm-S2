<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 有限增长准入观察

当前Q+GQA上的稀疏CPU准入与失败状态诊断；不实现预留策略，不把页预算反事实当作吞吐收益。

相关代码：[biv150_admission_observer.py](../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long-control/biv150_admission_observer.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T191047Z-q-gqa-admission-observe-context16k-long](../runs/bi-v150/20261022T191047Z-q-gqa-admission-observe-context16k-long.md)（登记#162）：32成功0失败；诊断有临时O(N)状态复制开销，不报吞吐或预算反事实收益，有限窗口与晚尾代价由后继实际诊断判断 **是否保留：** 保留作准入状态诊断；尚未实现预留策略，不提供性能收益结论。
