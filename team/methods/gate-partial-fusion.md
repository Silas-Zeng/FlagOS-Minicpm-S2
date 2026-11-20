<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# gate partial融合

实际opaque/F.linear默认FlagGems身份及GROUP_M8、BM256/BN256/BK32/w16/s2门通过；M2030的8项逐位/FP64/Graph/side stream通过，但完整Graph链慢14.8772%，停止M2048、8层工作集与模型。两臂均两个launch，partial_up shared64→128KiB、reg97→169；资源与退化同时观察，未隔离因果。单层合成激活，无生产/官方资格，不改主线。

相关代码：[result.json](../../experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/result.json)；[source](../../experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/source)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T075700478338Z-biv150-gate-partial-fusion-component](../runs/bi-v150/20261026T075700478338Z-biv150-gate-partial-fusion-component.md)（登记#317）：真实opaque/F.linear默认FlagGems身份与config门通过；M2030共8项output/gate逐位、FP64、换值Graph和side stream通过，RNG不变。完整Graph原linear＋SiLU对partial融合Event1.305488646→1.4997093 **是否保留：** 停止M2048、工作集和模型；不合并、不定基线，保留负结果。
