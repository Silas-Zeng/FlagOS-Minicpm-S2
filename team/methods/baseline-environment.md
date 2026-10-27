<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 基线接续与容器环境复查

当前main241/native14f原官方4K/16K各四轮暖均5850.05/4487.49 tok/s，同身份105题104/105通过。105未覆盖Q32/C3，原owner覆盖检查失败单独保留。main594重启后4K首暖下降2.01%仅为两轮诊断，不证明容器因果；不同源码、KV和实验目的不混算。

相关代码：[archive-receipt.json](../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/archive-receipt.json)；[result.json](../../experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/result.json)；[archive-receipt.json](../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/archive-receipt.json)；[result.json](../../experiments/official/20261026T184110Z-main241-control-16k-four-rounds/result.json)；[comparison.json](../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../experiments/official/20261027T012646Z-main241-control-4k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../experiments/accuracy/20261027T021016Z-main241-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../experiments/accuracy/20261027T021016Z-main241-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../experiments/accuracy/20261027T021016Z-main241-native14f-math500/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T192108Z-main594-postrestart-4k-two-round-diagnostic](../runs/bi-v150/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic.md)（登记#347）：原main594/native14f/初始DB207f重启后4K两轮诊断：冷5612.30对4909.31（+14.32%），首暖5726.40对5843.85（−2.0098%），512请求全部成功。旧三暖5767.56–5931.59，本轮首暖比旧最小低0.714%；源码/DB/native与时 **是否保留：** 保留原件；不补大测，不更新正式四轮基线。
- [20261026T184110Z-main241-control-16k-four-rounds](../runs/bi-v150/20261026T184110Z-main241-control-16k-four-rounds.md)（登记#348）：新团队main241/native14f/初始DB207f原官方16K四轮3791.43/4489.43/4487.31/4485.73 tok/s，弃首暖均4487.49，512请求全部成功；对旧main594暖均4192.49观察+7.0364%；KV容量548288→548432多144tok **是否保留：** 保留新main同口径16K控制；4K和105资格独立。
- [20261027T012646Z-main241-control-4k-four-rounds](../runs/bi-v150/20261027T012646Z-main241-control-4k-four-rounds.md)（登记#350）：main241/native14f/初始DB207f原官方4K四轮[5632.05, 5833.56, 6000.87, 5715.73] tok/s，弃首暖均5850.053333；1024请求全SUCCESS，实际Q32/原栈、源码/native不变、DB恢复及清理通过。旧main594暖均58 **是否保留：** 保留本站main241完整4K控制，未取得105模型准确率资格。
- [20261027T021016Z-main241-native14f-math500](../runs/bi-v150/20261027T021016Z-main241-native14f-math500.md)（登记#354）：main241完整765源/native14f/DB207f，原Math500 Level3全105题、temperature1/top_p.95/max32768/batch8不变：104/105=99.047619%，valid/pass；105 stop，0请求错误/截断/空答案/空提取。34 **是否保留：** 保留当前main241原官方精度结果；不为覆盖门强改框架或重测105。
