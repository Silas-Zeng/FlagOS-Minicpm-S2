# 015315进展victim：动态前缀与真实搬运专项

仅天数BI-V150本实例/MiniCPM5-2B。`20261022T015315Z-kv-progress-victim-context16k-long` 的VERIFY1实际链已成立；这是机制诊断，不证明公平、采样等价、accuracy或性能收益。本owner直接读取实际server.log，未执行systems的完整b7ff后验或重复测试。

原包SHA `38c096b9b254ee9846364912503d197897f5357db357422813368adca493794b`；独立逐数组/事件核算见[专项JSON](source/preemption-snapshot/015315-hardware-transfer-review.json)。当前源417、runtime72942，启动KV521936token；没有6a启动内存观察器，不能给出本轮nonTorch分项归因。

## 选中对象确实完成原FULL与消费

Engine250261第205行动态选择原index2、已确认输出552、合法remaining上界472的请求，区别于原tail index30/output327和失败对象index1。候选28条，free0/derivedneed1；这些索引只描述本次事件，运行时规则没有硬编码它们。DECISION先输出、再递增selected计数，所以当行计数0，随后真实RPC计数1是原定时序。

| 实际事项 | 核实结果 |
|---|---|
| selected请求 | `cmpl-bench-30645957-3-0-af5095b5`，SAVE/FULL/runner/consumer同Key与rid |
| 安全R | 16928token，1058完整页，728039424B=694.3125MiB |
| 选中可释放页 | ref1 owned1059；不是将1059页全部保存，多出的owned页不在安全R前缀 |
| SAVE | 37个真实源段，42层×37=1554calls，真成功/settled ACK后原free |
| 目的页排序 | 原序1058run→65run，同页/同对象/同list证明保留；未来free顺序可改变 |
| RESTORE_FULL | 42层×65=2730calls，无ZERO，完整覆盖/目的绑定为真 |
| 真字节回读 | 728039424B、2730calls，全部42层通过 |
| 原消费 | runner六检查全真，原update后消费9个scheduled token；**不是声称新增9个输出token** |
| 生命周期 | 真SAVE→FULL→DROP serial1/2/3；host在DROP释放，fast reject/restore skip各454 |

这些是当次真ACK/回读/消费者证据，不自动证明新抢占轨迹下全局随机输出相同。静态1GiB cap不放宽；实际SAVE成功也不代表可镜像约20.9GiB全池到20GiB主机。

## 尾部碎片的实际比例

直接从本轮SAVE原逻辑页序列计算：

| 源范围，仅作几何分解 | 页数 | 字节 | 连续段 | 42层copy calls |
|---|---:|---:|---:|---:|
| 前1024页 | 1024 | 704643072（672MiB） | 3 | 126 |
| 后34页 | 34 | 23396352（22.3125MiB） | 34 | 1428 |
| 全安全R | 1058 | 728039424 | 37 | 1554 |

尾34页只占 **3.21361%字节，却占91.89189%调用**。这更新了旧[碎片感知前缀设计](2026-10-22-kv-fragment-aware-prefix-plan.md)的本地结构依据：当前不是旧200957的20尾页，也不是旧4个头部段。没有RPC分阶段时间，调用占比不等于耗时占比；不能据此承诺截去544token会更快，更不能把1024页写作固定策略。

后继若重评该既有设计，仍须保原安全R0/真实queued/known−1、完整token与digest、pending frame及原FULL proof，并由普通路径重算未保存的已知后缀。16SM上的长上下文后缀重算可能抵消6CPU/42storage的提交节省；当前FULL已无ZERO，不能再计算额外省ZERO收益。完整准入及随后suffix分配也可能仍需同样容量，不声称更短R必然提前恢复。当前不实现、不新增设备门。

## 本轮不能作性能对照

DB实际before为519表/19340行，after为523表/19474行；snapshot/schema/logical三SHA均改变。root另有[新形状DB解读](2026-10-22-progress-victim-db-shapes.md)，不能把首次学习、VERIFY1回读和选择日志混入策略收益。该诊断的32成功0失败与完整后态由systems唯一完整门负责；本专项不重复全门，也不拿耗时比旧FULL。

下一步只接受独立FULL1aff与72942、共同6a、VERIFY0、原参数和严格DB/KV匹配的包装审阅。其结果仍须实际选择、动态R/几何、真实恢复与原消费者成立；失配或负收益都保留，不追最好容量。
