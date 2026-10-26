<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# BF16 down N方向分组布局

同一N128 BF16无损格式：M64单层省10.5534%，新M32单层省约3.63%；M2048为适应格式BN256→128后慢约61.60%，停止该大M候选。42真实权重GPU helper/opaque/Graph接线门通过，但不是完整模型安装链或官方成绩。原W/P双份1008MiB及KV容量代价未消除；不叠加各M收益。

相关代码：[result.json](../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/result.json)；[worker.py](../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/worker.py)；[archive-receipt.json](../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/archive-receipt.json)；[candidate.py](../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/candidate.py)；[result.json](../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/result.json)；[worker.py](../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/source/worker.py)；[archive-receipt.json](../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/archive-receipt.json)；[result.json](../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/result.json)；[worker.py](../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/source/worker.py)；[archive-receipt.json](../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/archive-receipt.json)；[result.json](../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/result.json)；[worker.py](../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/source/worker.py)；[archive-receipt.json](../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T102808704037Z-biv150-nonly-down-component](../runs/bi-v150/20261026T102808704037Z-biv150-nonly-down-component.md)（登记#327）：M64单层9类检查通过，完整GEMM Event省10.5534%；保留组件候选，42层显存成本与模型净收益未测。 **是否保留：** 保留单层组件候选；先解决或验证42层额外1008MiB/24576 KV token容量成本及真实交织，不能直接合并或宣称模型收益。
- [20261026T105246722313Z-biv150-nonly-down-integration](../runs/bi-v150/20261026T105246722313Z-biv150-nonly-down-integration.md)（登记#328）：42真实权重helper/opaque、pack逐位、FP64、换值Graph及M32回退通过；不是完整Llama加载链，无计时或官方资格。 **是否保留：** 保留新增helper/opaque/Graph接线证据；完整模型加载链和官方净性能不继承，原W/P双份容量成本未消除。
- [20261026T105528588827Z-biv150-nonly-down-M32-component](../runs/bi-v150/20261026T105528588827Z-biv150-nonly-down-M32-component.md)（登记#329）：M32单层8门通过，同配置完整Graph Event省约3.63%；保留组件信号，非模型收益，双份权重成本未消除。 **是否保留：** 保留M32组件正信号，和M64分别记录；单次ABBA不能写稳定模型收益，42层及实际Attention/KV交织尚未测。
- [20261026T105751336178Z-biv150-nonly-down-M2048-component](../runs/bi-v150/20261026T105751336178Z-biv150-nonly-down-M2048-component.md)（登记#330）：M2048单层8门通过；P128使BN256→128，完整Graph Event慢约61.60%，停止；不能归因纯pack，不否定M32/M64。 **是否保留：** 停止当前N128大M候选，保留负证据；不扩模型、不混入M32/M64收益。若研究保留原BN256的P256，应作为新独立方法验证。
