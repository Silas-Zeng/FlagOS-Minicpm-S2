<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 末层Query精确选行

仅末层Attention选择需要输出的Query，完整M行K/V仍保留；组件核P映射、metadata、全slot字节及独立参考差异，不是模型准确率或端到端收益。

相关代码：[candidate.diff](../../archive/candidates/20261025-final-rows/final-query-row-model-candidate/candidate.diff)；[state.json](../../experiments/framework/20261025T005351Z-final-query-row-component/state.json)；[state.json](../../experiments/framework/20261025T013820Z-final-query-row-component-v2/state.json)；[state.json](../../experiments/framework/20261025T014029Z-final-query-row-component-v3/state.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T005351Z-final-query-row-component](../runs/bi-v150/20261025T005351Z-final-query-row-component.md)（登记#242）：selected-Q首次组件在原526 native安装链因TP组未初始化而失败，无有效case或双臂数值。00:54:11 UTC源码/native保持、DB恢复、设备清理通过。保留原失败；不将初始化问题算作算法数值负结果。 **是否保留：** 原始证据和失败保留；是否进入模型/合并以本轮结论为准，不自动续测。
- [20261025T013820Z-final-query-row-component-v2](../runs/bi-v150/20261025T013820Z-final-query-row-component-v2.md)（登记#244）：selected-Q v2真实world1/TP1建立及finally清理成功，但首case在torch.tensor(numpy,pin_memory=True)构造处失败，双臂尚未执行，无数值结论。01:38:40 UTC源/native保持、DB恢复及设备清理通过。仅修缓冲分配在独立v3重试， **是否保留：** 原始证据和失败保留；是否进入模型/合并以本轮结论为准，不自动续测。
- [20261025T014029Z-final-query-row-component-v3](../runs/bi-v150/20261025T014029Z-final-query-row-component-v3.md)（登记#245）：selected-Q v3四shape双臂完整：S32/40/64、M2048及S5/M141；两臂均写完整M行K/V，全部slot逐字、guard、输出guard、P与请求顺序通过，真实GQA/Q路径有调用证据。输出均有限但非逐bit：maxabs依次0.001953125/0.001953125 **是否保留：** 原始证据和失败保留；是否进入模型/合并以本轮结论为准，不自动续测。
