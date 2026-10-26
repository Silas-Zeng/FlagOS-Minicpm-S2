<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# BF16 down N方向分组布局

真实生产opaque/F.linear的M64 down单层组件，仅改N方向BF16无损权重布局，保留实际BM64/BN128/BK64/w8/s2与SME；9类逐位/独立FP64/Graph及RNG门通过。完整GEMM Graph Event0.085926324→0.076858178ms，省10.5534%，仅保留组件正信号。原W与packed两份各24MiB；若42层重复保留将多1008MiB、等价24576 KV token，容量风险及42层交织未测。无模型/官方/105资格，未定新基线；DB/source与清理通过。

相关代码：[result.json](../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/result.json)；[worker.py](../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/worker.py)；[archive-receipt.json](../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/archive-receipt.json)；[candidate.py](../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/candidate.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T102808704037Z-biv150-nonly-down-component](../runs/bi-v150/20261026T102808704037Z-biv150-nonly-down-component.md)（登记#327）：M64单层9类检查通过，完整GEMM Event省10.5534%；保留组件候选，42层显存成本与模型净收益未测。 **是否保留：** 保留单层组件候选；先解决或验证42层额外1008MiB/24576 KV token容量成本及真实交织，不能直接合并或宣称模型收益。
