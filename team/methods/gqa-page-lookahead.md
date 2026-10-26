<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA下一页号预取

原page16 while仅提前读取下一i32页号，N64/S2观测长度多重集、合成激活；原8类FP64/特殊值/Graph等门与跨臂逐位全部通过。完整producer＋原reducer Event0.542211056→0.542784363ms（慢0.105735%），wall快0.06134%，无可分辨正信号，停止不进模型。ASM下一页load后立即wait，未实现预期计算重叠；SGPR64→68、两臂spill0，源码/DB/native及清理通过。

相关代码：[results.json](../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/results.json)；[worker.py](../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/source/worker.py)；[archive-receipt.json](../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/archive-receipt.json)；[candidate.py](../../experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/source/candidate.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T102536253539Z-gqa-page-lookahead-hotspot-component](../runs/bi-v150/20261026T102536253539Z-gqa-page-lookahead-hotspot-component.md)（登记#326）：8类数值门与逐位通过；完整组件Event慢0.1057%、wall快0.0613%，无可分辨正信号，停止。 **是否保留：** 保留数值通过但无净收益的负结果，停止，不扫参、不进模型；不将微小Event/wall反向差异写成稳定因果退化。
