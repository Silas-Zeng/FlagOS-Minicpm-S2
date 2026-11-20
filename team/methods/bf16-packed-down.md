<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# BF16 down权重微块布局

真实F.linear同配置的BF16位重排；首次停在SME假设，v2保留全部正确性后通过8项，但M2030完整Graph慢71.89%，停止。

相关代码：[source](../../experiments/framework/20261026T090924033923Z-biv150-packed-down-component/source)；[source](../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/source)；[result.json](../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/result.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T090924033923Z-biv150-packed-down-component](../runs/bi-v150/20261026T090924033923Z-biv150-packed-down-component.md)（登记#320）：真实F.linear选BM256/BN256/BK32/w16/s2；pack/unpack及首normal逐位一致。B dot useSme2→0，shared64→48KiB/reg97→98，在机制检查停止；未完成全部正确性、未计时。 **是否保留：** 原机制假设未实现；不当数学错误或性能负。后继独立v2保留数值门，以一次计时判断净效果。
- [20261026T092809453391Z-biv150-packed-down-component](../runs/bi-v150/20261026T092809453391Z-biv150-packed-down-component.md)（登记#322）：v2仅将SME机制要求改诊断，candidate字节不变；8项数值/FP64/Graph/side检查通过。M2030完整GEMM Graph ABBA原F.linear0.564831406→packed0.970907092ms，慢71.89%，停止M2048/权重环/模型。DB/source/ **是否保留：** 停止该布局，不合并、不定基线；局部负结果保留。
