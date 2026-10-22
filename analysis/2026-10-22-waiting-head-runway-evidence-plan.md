# 天数BI-V150：下一框架切口只保留等待队头与容量跑道证据门

原FULL/progress首pair现已结束：A020721为218.3996s/KV521936，B021658为218.5134s/KV521840；DB四端相同，但B启动残差多4MiB、可用KV少6页，systems的3f1完整报告将收益置null。机制过且原件保留，**不重刷本pair、不从两数直接选优**。用户暂缓GitHub/PR，此研究仅本地中文记录。

目前没有足以批准新“大收益”调度实现的证据。唯一下一设计限于：**首次恢复队头被容量拒绝时，证明是否存在能在安全KV跑道内准入的其它等待请求**。先证据门，非立即实现skip-head、保留未来输出预算或改调度参数。若无满足条件的实际对象，关闭此切口，而非堆复杂准入器。

## 已有结果和资源约束先排除什么

已读CURRENT顶端、framework-research-closeout、next-framework-priority、scheduler-kv-innovation、prefill-graph及memory-lifecycle报告，并复核actual df780/2e91与原FULL/selector接口。旧full-outputreserve115950真实CHECKED/DEFERRED但无正吞吐；181041的terminal-drain必要条件为0；token bucket/growth/hidden gather/overlap/mapped及prefix服务反例均不重启。缩prefix不绕full-sequence准入的015315反证仍成立，不能换名为新容量收益。

root新资源窗口JSON `source/preemption-snapshot/progress-pair-resource-samples.json` SHA98543294…：约242.75/242.83s的metrics窗口含客户端准备，并非218s纯bench；48/49个约5秒样本的GPUutil中位96/95%、SM clock全1500，cgroup2428/2429 periods仅4次throttled。它反对仅凭6CPU就认定host大瓶颈；不是证明无微小GPU空洞，也不能把memory util87%作HBM带宽、throttled_time聚合当端到端损失。下一设计不以未测host瓶颈为收益预算。

## 原代码没有在队头失败时停止GPU全部工作

actual df780:434起先调RUNNING，625以后才调WAITING；本schedule已有preempt时直接不进WAITING。WAITING原allocate None在888以后break这个等待循环，**不会撤销前面已排的RUNNING工作**。原FULL的_try_restore在“Get already-cached tokens”前运行，恢复尝试拒绝后仍允许原普通路径；真正普通重算准入才DROP host。不能将restore_skips454/462直接解释为454/462次GPU空转。

原有running decode会继续增长KV并推进。若所有已排query都为1，原FULL_DECODE_ONLY已有相应uniform decode图分派；缺少prefill本身不等于待实现的图覆盖机会。当前没有完整逐步形状/时间证据，不能称整个阻塞区间均为同一个图，也不能把早期D29/P2019单层构造当实际关键路径。

## 反证：free1044能放1024页不构成安全越队条件

015315首RESTORE_DEFERRED已记录free1044、head known16937、full_sequence_must_fit=True。恢复head无owned/localhits时完整known需1059页；全新16K候选若无共享，完整prompt需1024页。后者只看这一瞬间能通过容量门，却只剩20页，并未为当前约30个active decode或该新请求的生成阶段提供保障。

一个不依赖每条页内余量的整数下界说明风险：若n=30条旧请求在无释放期间各再调度H=16个token，且无共享/特殊窗口，则每条即使开始时页内有最大15个空位，也至少新增1页，共至少30页，已超过20页。若新prefill分8个2048预算步推进，旧decode也继续；不能忽略其增长，再将prefill结束后20页当额外空闲跑道。**这是假设清楚的容量反证，不是原件已证明会在第16步抢占**；实际页内offset、prefill分块、完成/取消、APC共享和请求推进均影响结果。

合法max减confirmed只给剩余输出上界，不能无条件当“至少还要455步才完成”。同样，没有真实每条ignore_eos/stop/状态与调度cadence证明，也不能把benchmark参数转成通用实现中的未来完成时间。即使有严格的最晚释放上界，也不能由其得出实际更早EOS或墙钟时间。

## 唯一可证明的新条件：容量证书，先筛除机会而非实现预算器

若要支持一次越队，至少需要一个明示的无新抢占容量证书：对拟准入q，在允许的有限推进区间h内，任意前缀步t都满足

```text
现有free + 已由原生命周期真实释放的页
  ≥ q累计实际需要的私有新页
    + 全部保留RUNNING在该前缀的新增页上界
    + 其它已inflight/原watermark等必要占用。
```

逐请求当前owned、页内剩余位置、issued/queued真实跨度和合法输出上界必须参与；共享页按实际refcount/唯一物理集合，不把ref0 APC命中当免费。尚未消费的Future、placeholder或预测EOS不作已释放页。h必须有可证明的终点：例如原已提交且可证达到合法max的有限FIFO消费，或严格scope下保留请求持续被调度到合法max的上界；不能设任意“等几个step就会释放”。后者要连同所有其它活跃请求在h内的增长一起计入。

该式可用来**否定**“只因1024<1059就跳head”的解释；当前不推荐把它实现成另一个growth-reserve。full-outputreserve对所有未来输出的常态预留已经失败，复杂短期影子也曾暂停。若新证书要反复模拟整个调度器或无法从固定源码给出有限边界，应直接降级，无须再上5分钟门。

对于本阶段同长目标输入/输出预算，等待集合甚至可能全无更便宜对象；现有快照只含running31，不能据32总数或opaque ID推断所有WAITING状态、前缀共享和最终长尾。即使能安全准入，也只证明不立即重抢占，**不证明在16SM上插入prefill会缩短makespan**：它可能拖慢较早完成的decodes、增加MM提交和破坏现有uniform图机会。

## 唯一下一证据设计，尚未编码或排设备

若root选择继续，先只在首次真实HOST_RESIDENT head容量拒绝的位置保一份CPU描述符：原head身份/known/R/队列状态，free/严格full-sequence需求；全部RUNNING的当前进展、owned/ref共享/页内余量、queued spans；原等待顺序内其它对象的prompt/known/合法max/状态、已有owned、本地已产生可用描述（不额外prefix查询）、可否构成上述必要证书。只记录长度/身份/标量，不token内容、不Future方法、不GPU操作。

精确切点可在独立协议副本的 `_capacity_fast_reject` 原返回True之后、原_try_restore返回前，仅首次观察；原返回/状态/allocator调用顺序一字不改。此位置给真实head而非根据requests字典猜FIFO头。实际RequestQueue源码目前不在本次已核归档清单，**未读前不能假设其内部deque名、可迭代顺序或pop/reinsert无副作用**；若要读完整等待次序或实现越队，这是唯一需要先核实的接口缺口，不先写“已ready”的collector。

目前不要求新设备诊断：先由root判断这些尚缺字段是否足以改变决策。如另行授权采集，最短仍是一个独立原context-long观察run，不能混入已完成失配pair，不做新策略/完整accuracy或额外profiling。无真实较低私有需求、无证书、只短暂容量窗口或现有GPU工作已充分时，保留负结论并停止此切口；只有非空且源码生命周期可证，才另审实际选择/公平/RNG/原输出协议风险。

本轮结论是有明确反证和缺证的框架入口，**没有已证可实现的大收益策略、没有新runtime/合同/上卡或收益**。原FULL/selector、所有small/negative原件持续保留。

root收口决定：目前瞬时fit已被页增长反证，补完整WAITING队列未必改变动作，**暂不排另一个纯观察5分钟门**。本文作为未实施设计保留，不新增collector/测试。root后继优先由hardware核完整前缀的等差页段2D合并API，保持R/victim/全KV；这不是本文已实施候选或本owner的新设备任务。
