<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 计算顺序与采样顺序分离

计算行重排以适配Attention路径，采样保持原请求顺序。当前适配队友normalized main328，仅改runner/helper两文件；代码4fca58ba/tree5c77。140324→141159短测表观约+6.59%，但KV521840→521936，gain=null。142019完整105题103正确（98.0952%）通过，但P分支0命中。144620原官方8轮全部成功，1536请求；原第2–4轮均值4K5116.68、16K3436.04 total tok/s，实际P N62/M2048/outside59。保留Draft方法候选：这是绝对性能，不能归因单项收益，也不能用吞吐命中弥补准确率P0。旧423的单pair+5.124857%、三题质量、结构映射与独立参考证据保留，不能替代新组合结果。

相关代码：[compute-order-current-main-official.json](../../analysis/compute-order-current-main-official.json)；[compute-order-current-main-accuracy.json](../../analysis/compute-order-current-main-accuracy.json)；[compute-order-current-main-pair.json](../../analysis/compute-order-current-main-pair.json)；[README.md](../../archive/ai/20261022-framework-kv/compute-order-main-profile/README.md)；[compute-order-math4-event-130351.json](../../analysis/compute-order-math4-event-130351.json)；[compute-order-math4-event-125330.json](../../analysis/compute-order-math4-event-125330.json)；[compute-order-service-retest-pair.json](../../analysis/compute-order-service-retest-pair.json)；[compute-order-math4-summary.json](../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../analysis/compute-order-first-layer.json)；[result.json](../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../docs/agent-work/compute_order_review.md)；[completion.json](../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)。

相关方法PR：[计算顺序 #21（草稿）](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/21)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261023T054306Z-compute-order-baseline-context16k](../runs/bi-v150/20261023T054306Z-compute-order-baseline-context16k.md)（登记#187）：32成功0失败、exit0，104.312939462s、5065.373507102 total tok/s **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261023T060425Z-compute-order-candidate-context16k](../runs/bi-v150/20261023T060425Z-compute-order-candidate-context16k.md)（登记#188）：吞吐表观+4.7989%、耗时表观减少4.5792%；KV容量不同（基线521936、候选521840），31门仅same_KV false、gain=null，不能归因收益；061500准确率pending，不继承422结果 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261023T061500Z-compute-order](../runs/bi-v150/20261023T061500Z-compute-order.md)（登记#189）：423候选完整Math500 Level3通过101/105（96.1905%），105成功、0transport/空答案；未出现COMPUTE_ORDER_FIRST_SELECTED，本轮不外推为新排列路径的准确率证明 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261023T070816Z-compute-order-answer-baseline](../runs/bi-v150/20261023T070816Z-compute-order-answer-baseline.md)（登记#192）：失败 **是否保留：** 未集成；失败或无收益记录保留。
- [20261023T075210Z-compute-order-shadow-context16k](../runs/bi-v150/20261023T075210Z-compute-order-shadow-context16k.md)（登记#193）：失败：原序/P logits最大绝对差11.828125，top1仅12/17行一致，停止性能大测；shadow重复forward属于诊断，不计性能、不报收益、不作为完整准确率 **是否保留：** 未集成；失败或无收益记录保留。
- [20261023T082246Z-compute-order-first-layer-context16k](../runs/bi-v150/20261023T082246Z-compute-order-first-layer-context16k.md)（登记#194）：原序/P首层实际IDs、positions、QKV、slots、seq及有效页表逐bit一致，Attention输出最大差0.05712890625（原row2）；仅诊断，候选暂不集成 **是否保留：** 保留诊断与候选；完整正确性尚未确认，暂不集成，不计性能。
- [20261023T085500Z-compute-order-oracle-context16k](../runs/bi-v150/20261023T085500Z-compute-order-oracle-context16k.md)（登记#195）：独立CPU FP32：原2D最大误差0.00838811696、P/GQA0.000767201185；本样本P更接近参考，不能据此证明全模型正确，候选继续保留不集成、不调容差 **是否保留：** 保留诊断与候选；完整正确性尚未确认，暂不集成，不计性能。
- [20261023T100604Z-compute-order-structure-context16k](../runs/bi-v150/20261023T100604Z-compute-order-structure-context16k.md)（登记#196）：未命中P的原105题流程 **是否保留：** 未集成；失败或无收益记录保留。
- [20261023T104132Z-compute-order-math4-mixed](../runs/bi-v150/20261023T104132Z-compute-order-math4-mixed.md)（登记#197）：固定原Level3 index0..3题身份/response ID/原judge已核，4/4正确 **是否保留：** 未集成；失败或无收益记录保留。
- [20261023T120949Z-compute-order-baseline-context16k](../runs/bi-v150/20261023T120949Z-compute-order-baseline-context16k.md)（登记#199）：吞吐变化+5.124857% **是否保留：** 保留作本轮可比对照基线。
- [20261023T121541Z-compute-order-candidate-context16k](../runs/bi-v150/20261023T121541Z-compute-order-candidate-context16k.md)（登记#200）：吞吐变化+5.124857% **是否保留：** 保留单pair正信号；稳定收益与目标路径质量尚待确认，暂不集成。
- [20261023T125330Z-compute-order-math4-event](../runs/bi-v150/20261023T125330Z-compute-order-math4-event.md)（登记#201）：客户端长度校验在发送前失败；背景0发送、四题未放行，本轮未评价优化。 **是否保留：** 保留客户端失败与修复证据；本轮未评价优化。
- [20261023T130351Z-compute-order-math4-event](../runs/bi-v150/20261023T130351Z-compute-order-math4-event.md)（登记#202）：原四题4/4正确，3题实际覆盖且在首完整答案框前；背景32/0。仅小样本诊断，不计性能或完整准确率。 **是否保留：** 保留小样本质量信号及候选，可准备独立Draft PR；暂不集成。
- [20261023T140324Z-current-main-baseline-context16k](../runs/bi-v150/20261023T140324Z-current-main-baseline-context16k.md)（登记#203）：吞吐+6.589830%，但KV容量不同（521840→521936），33项仅same_KV失败、gain=null，不能归因收益 **是否保留：** 保留基线与候选；KV容量不同，不计归因收益，组合准确率另验。
- [20261023T141159Z-current-main-compute-order-context16k](../runs/bi-v150/20261023T141159Z-current-main-compute-order-context16k.md)（登记#204）：吞吐+6.589830%，但KV容量不同（521840→521936），33项仅same_KV失败、gain=null，不能归因收益 **是否保留：** 保留基线与候选；KV容量不同，不计归因收益，组合准确率另验。
- [20261023T142019Z-current-main-compute-order](../runs/bi-v150/20261023T142019Z-current-main-compute-order.md)（登记#205）：103/105（98.0952%）达到原95%门 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261023T144620Z-current-main-compute-order-official](../runs/bi-v150/20261023T144620Z-current-main-compute-order-official.md)（登记#206）：两case各4轮全部SUCCESS，1536请求成功，原第2–4轮均值：4K5116.68、16K3436.04 total tok/s **是否保留：** 保留作候选，仍待确认；不等于默认启用。
