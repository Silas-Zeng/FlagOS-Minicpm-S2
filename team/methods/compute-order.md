<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 计算顺序与采样顺序分离

仅在合格混合步骤重排模型计算序，保留原请求及采样序。054306→060425两侧均32成功0失败，候选真实命中；单pair吞吐表观+4.7989%，但KV容量521936→521840不同，31项仅same_KV不通过、gain=null，不能归因收益。保留候选与失配证据，默认版本暂不采用。061500完整Math500 Level3为101/105、通过既定门，但未出现COMPUTE_ORDER_FIRST_SELECTED，不能证明新排列路径正确；2个max_tokens、DB554/20517→558/20651及覆盖限制单列，不与旧422的103/105解释为精度退化统计。

相关代码：[compute-order-service-pair.json](../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../docs/agent-work/compute_order_review.md)；[completion.json](../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261023T054306Z-compute-order-baseline-context16k](../runs/bi-v150/20261023T054306Z-compute-order-baseline-context16k.md)（登记#187）：32成功0失败、exit0，104.312939462s、5065.373507102 total tok/s **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261023T060425Z-compute-order-candidate-context16k](../runs/bi-v150/20261023T060425Z-compute-order-candidate-context16k.md)（登记#188）：吞吐表观+4.7989%、耗时表观减少4.5792%；KV容量不同（基线521936、候选521840），31门仅same_KV false、gain=null，不能归因收益；061500准确率pending，不继承422结果 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261023T061500Z-compute-order](../runs/bi-v150/20261023T061500Z-compute-order.md)（登记#189）：423候选完整Math500 Level3通过101/105（96.1905%），105成功、0transport/空答案；未出现COMPUTE_ORDER_FIRST_SELECTED，本轮不外推为新排列路径的准确率证明 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
