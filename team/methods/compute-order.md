<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 计算顺序与采样顺序分离

075210自然混合shadow诊断出现原序/P logits大差：最大绝对差11.828125，top1仅12/17行一致；finite和采样前RNG相同不代表数值门通过。32成功0失败只说明服务结束，不计性能；当前不集成，停止性能大测，CPU定位诊断与候选根因。原0/1/16行bitexact、14个outside q1行全差只是线索。此前短筛表观+4.7989%受KV失配影响、gain=null；061500准确率101/105虽通过却未命中新排列路径，不能证明该路径正确，也不与旧422的103/105作升降统计。070816辅助答案基线仅4/32符合预设答案，提示门无判别力，候选侧未运行，不归因优化失败。

相关代码：[result.json](../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../docs/agent-work/compute_order_review.md)；[completion.json](../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261023T054306Z-compute-order-baseline-context16k](../runs/bi-v150/20261023T054306Z-compute-order-baseline-context16k.md)（登记#187）：32成功0失败、exit0，104.312939462s、5065.373507102 total tok/s **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261023T060425Z-compute-order-candidate-context16k](../runs/bi-v150/20261023T060425Z-compute-order-candidate-context16k.md)（登记#188）：吞吐表观+4.7989%、耗时表观减少4.5792%；KV容量不同（基线521936、候选521840），31门仅same_KV false、gain=null，不能归因收益；061500准确率pending，不继承422结果 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261023T061500Z-compute-order](../runs/bi-v150/20261023T061500Z-compute-order.md)（登记#189）：423候选完整Math500 Level3通过101/105（96.1905%），105成功、0transport/空答案；未出现COMPUTE_ORDER_FIRST_SELECTED，本轮不外推为新排列路径的准确率证明 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261023T070816Z-compute-order-answer-baseline](../runs/bi-v150/20261023T070816Z-compute-order-answer-baseline.md)（登记#192）：失败 **是否保留：** 未集成；失败或无收益记录保留。
- [20261023T075210Z-compute-order-shadow-context16k](../runs/bi-v150/20261023T075210Z-compute-order-shadow-context16k.md)（登记#193）：失败：原序/P logits最大绝对差11.828125，top1仅12/17行一致，停止性能大测；shadow重复forward属于诊断，不计性能、不报收益、不作为完整准确率 **是否保留：** 未集成；失败或无收益记录保留。
