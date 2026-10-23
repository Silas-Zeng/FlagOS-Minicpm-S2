<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 计算顺序与采样顺序分离

计算顺序与采样顺序分离：100604完整token逆排列、logits索引与原sample单次衔接通过；104132固定四题原judge4/4，但题目P outside覆盖0/4，记未覆盖，不改题/时序重试。085500单行独立参考下P/GQA更接近FP32，不能据单层或0P准确率证明新路径全模型正确。候选保留暂不集成，诊断段先收口，主线回到实际GPU热点。此前短筛表观+4.7989%受KV失配影响、gain=null；061500完整准确率101/105通过却未命中新路径；负结果一并保留，不调容差。

相关代码：[compute-order-math4-summary.json](../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../analysis/compute-order-first-layer.json)；[result.json](../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../docs/agent-work/compute_order_review.md)；[completion.json](../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)。

相关方法PR：未记录。

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
