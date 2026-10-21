# 天数BI-V150：首次RUNNING分配失败真实快照

独立诊断 `20261021T230548Z-preemption-snapshot-context16k-long` 已完成。冻结验收入口6eb45只执行一次，exit0/1.465s；无解析修复、重复设备或旧套件。完整报告 [`230548-review.json`](source/preemption-snapshot/230548-review.json)，SHA **06c16d26e8eee184269d46d09f488da5b63867f90e57900eaaf1484c23ae53e4**；执行回执 [`230548-execution-receipt.json`](source/preemption-snapshot/230548-execution-receipt.json)，SHA **a63180798d9be08b2f3c1a27f88214888e2e855d61c0210bcb8e6c55918eadfb**。本轮只观察，没有实现新victim策略。

## 实际生命周期与输入

Engine PID240315同PID按次序出现CORE_HOOKED、SCHEDULE_ARMED（固定87a方法逐byte逆回true）、FIRST_CHECKED eligible=True、恰一FIRST_RUNNING_FAILURE complete=True。前端PID240147因Core尚未自然加载REJECTED另列，不是Engine失败。所有事件均声明无GPU值读取、Future就绪查询或victim策略变更。

失败瞬间全running共31个请求，**这31条实际prompt均16384、合法max输出均1024**，全为非streaming decode，已确认输出327至569。此结论仅属于该瞬间31条真实元数据；不凭benchmark总token量推断未出现在快照中的第32条长度或完整到达轨迹。

旧batch_queue有1帧，其原SchedulerOutput对每个相关请求已issued 1 token；每条placeholder也是1，二者概念分别记录。当前schedule只先排了另一条请求的1 token，剩余budget2047，重构总budget2048；当前尚未issued项不再从稳定R扣一次。

## 容量与请求进展

实际free=0，失败请求index1本次newtoken=1。固定FullAttention RUNNING cached-key快路径推导需新增1页，和实际None一致；该值明确是源码公式推导，未额外调用allocator。

| 快照位置 | 已确认输出 | 合法剩余上界 | owned页 | 稳定完整R | payload字节 |
|---|---:|---:|---:|---:|---:|
| 进展最高index0 | 569 | 455 | 1060 | 16944 | 728727552 |
| 分配失败index1 | 560 | 464 | 1059 | 16928 | 728039424 |
| 原FCFS尾部index30 | 327 | 697 | 1045 | 16704 | 718405632 |

所有running页均为非null唯一ref1，无共享；owned范围1045至1060，大多数页已有hash（1044至1059）。**ref1可释放与fresh/unhashed恢复资格不同**。全部逻辑R覆盖和1GiB payload cap成立，只是静态结构条件，不证明实际host余量、SAVE成功或传输run数；本快照无页ID、copy碎片分布、APC查询或host实际额度。

单次快照确实显示尾部进展比最高者少242个已确认输出。改变victim可能缩短尾部重算/恢复长尾，也可能延后一个本来更早释放资源的请求；合法剩余上界不是EOS或真实完成时间预测。验收只列需后续考察的结构行，排除失败请求自身和合法剩余上界最小者，不实际选victim，不将任一行宣称最优。容量机会的条件是保留当前失败请求继续；抢占它自身是另一种调度结果，不能混算。

这组数据足以否定“仅凭同长prompt就没有进展差异”的假设，但不足以直接批准新评分策略。下一步若继续此方向，应先明确保留近完成者、真实可释放页和恢复长尾的权衡，严格处理原PRIORITY撤销、异步旧frame与随机采样顺序；不硬编码request ID、行号或benchmark内容。

## 原负载与后态

原bc51/context-long/seed721201/SERVER参数及完整413源/live通过；原32/0、524288输入/32768输出，220.41899300506338s、2527.259526982793 total tok/s、TTFT62506.0147101176ms。**这些仅是带一次CPU快照的诊断负载记录，不计算性能收益或accuracy。** KV521936、CPU配额6核、物理显存32768MiB，preempt0→1。

DB519表/19340行，前后物理89743b…、schema29d740…、logical71ac19…三SHA相同；报告保完整哈希。finish23:10:54.058246Z，post23:11:57.075293Z确认68MiB/0%、无GPU进程、9031双栈关闭。测前ERROR为空，shutdown的EngineDeadError与force-kill WARNING原样保留，不称完全无警告。原始raw SHA07e249fa9bcdad6f2350229e51be9018d9b8b80664abd0c783da778d76ada845；root封存tgz SHAabe046f03d462d01fbd91bb69ff506bb19149e7969416190a406d150bcfe8cc9。

hardware按分工只作独立机制/解释审阅，不重复完整验收；登记由systems维护。本人未SSH、上GPU、修改已部署源或共享代码库。
