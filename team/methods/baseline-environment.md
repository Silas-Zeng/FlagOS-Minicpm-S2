<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 基线接续与容器环境复查

同版本main594 4K首暖观察下降2.01%，只作两轮诊断；新main241独立16K四轮暖均4487.49。两种源码和实验目的分别保留，不混算。

相关代码：[archive-receipt.json](../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/archive-receipt.json)；[result.json](../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/result.json)；[archive-receipt.json](../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/archive-receipt.json)；[result.json](../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/result.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T192108Z-main594-postrestart-4k-two-round-diagnostic](../runs/bi-v150/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic.md)（登记#347）：原main594/native14f/初始DB207f重启后4K两轮诊断：冷5612.30对4909.31（+14.32%），首暖5726.40对5843.85（−2.0098%），512请求全部成功。旧三暖5767.56–5931.59，本轮首暖比旧最小低0.714%；源码/DB/native与时 **是否保留：** 保留原件；不补大测，不更新正式四轮基线。
- [20261026T184110Z-main241-control-16k-four-rounds](../runs/bi-v150/20261026T184110Z-main241-control-16k-four-rounds.md)（登记#348）：新团队main241/native14f/初始DB207f原官方16K四轮3791.43/4489.43/4487.31/4485.73 tok/s，弃首暖均4487.49，512请求全部成功；对旧main594暖均4192.49观察+7.0364%；KV容量548288→548432多144tok **是否保留：** 保留新main同口径16K控制；4K和105资格独立。
