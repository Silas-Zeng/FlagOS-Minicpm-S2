<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Attention head-major分页读取

M2047/KV16K、page16三臂，当前GQA、原FlagGems head-major和新增page16 loader+N64均真实编译并通过独立FP64抽样及换值Graph。Event约8.366/29.733/82.944ms，候选明显负，停止。N64同时改变归约分块，非逐位保证，不拆成loader单项因果，不扩调参或创建优化PR。

相关代码：[candidate.diff](../../experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component/source/candidate.diff)；[worker.py](../../experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component/source/worker.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T130735173560Z-head-major-paged-prefill-component](../runs/bi-v150/20261025T130735173560Z-head-major-paged-prefill-component.md)（登记#269）：三臂编译及数值/Graph通过；Event当前8.366/原FlagGems29.733/新loader82.944ms，候选明显负。 **是否保留：** 停止该方法，不再调参、不创建优化PR；完整三臂结果保留。
