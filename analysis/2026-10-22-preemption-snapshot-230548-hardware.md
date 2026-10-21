# 230548真实快照：容量与请求进度专项

仅天数BI-V150当前16SM/32GiB实例、MiniCPM5-2B；不外推沐曦－曦云C500或团队总分。此次有证据支持下一阶段评估**一个受限victim候选**，尚无策略实现或收益证明。本批只核原始快照、保存中文解释，不增加设备任务或测试。

原件为 `experiments/framework/20261021T230548Z-preemption-snapshot-context16k-long/server.log`，第206行Engine240315的唯一完整快照。root封存包SHA为 `abe046f03d462d01fbd91bb69ff506bb19149e7969416190a406d150bcfe8cc9`。本owner独立逐行复算queued扣除、R、字节及候选描述，保存[专项JSON](source/preemption-snapshot/230548-hardware-request-review.json)；framework的[完整原件门](source/preemption-snapshot/230548-review.json)已单独通过，本owner没有重跑完整门。

## 容量由实际31条running填满

实际running为31条，prompt均16384token、合法最大输出均1024，已确认输出327..569；全部decode/nonstreaming。原失败对象index1，free0，原快路径推导新增需求1块。本schedule只登记index0的1token；旧queued另有一帧，每条均1token，两者不能混为同一个未完成窗口。

31行均无shared/null引用，ref1非null唯一页计数合计32620。启动日志KV为521936token，即32621池槽；冻结BlockPool源码另保留ID0作null，故 **32620+null1+free0=32621** 恰好对账。这依赖实际ref1/count和冻结null契约，不声称另做了未输出的物理ID全局并集验证。较早521840容量的32条条件例不适用于本快照。

R严格按 `max(0,min(issued−queued_span,known−1))//16*16` 复算，31行均一致，逻辑完整页覆盖与1GiB静态payload资格均真。每token43008B、完整16token块688128B已经包含42层，**释放页数不再乘42**。静态cap不证明主机pinned余量或SAVE成功。

## 有结构差异，但不是时间差

| 原running位置 | 已确认输出 | 合法剩余上界 | 安全R | ref1页 | payload字节 |
|---|---:|---:|---:|---:|---:|
| 0，保护集合 | 569 | 455 | 16944 | 1060 | 728727552 |
| 1，当前失败对象 | 560 | 464 | 16928 | 1059 | 728039424 |
| 2，动态进展规则的示例 | 552 | 472 | 16928 | 1059 | 728039424 |
| 30，原tail | 327 | 697 | 16704 | 1045 | 718405632 |

排除当前失败对象、已登记项、最小合法remaining/最高confirmed保护集合，并限原index大于failed后，描述集合有29条，含原tail；再要求进展严格高于tail，余 **28条，即本原件index2..29**。动态选最大confirmed会落到index2；index与请求ID只描述原件，绝不能写作实现规则。真正实现还要显式核三份当前schedule容器，日志单个 `current_scheduled_tokens` 不是对全部容器的独立采样证明。

示例比原tail多225已确认输出、合法剩余上界少225，但R只多224token。释放量与SAVE量同时增加14页/**9633792B=9.1875MiB**。这说明存在可区分对象，不说明节约225token执行时间，更不能换TPS。没有物理page IDs/runs、APC有效来源或阶段时间，不能判断新对象复制更快。

## 唯一后继判断与最强反证

建议保留framework的[唯一受限进展候选设计](2026-10-22-single-victim-progress-candidate.md)：保当前失败对象和保护集合，仅在尚未scheduled、原index>failed、原FULL空slot及其全部安全守卫内，最多一次主动替换尝试；其后原调度仍可能继续抢占tail。本批不实现、不修改原FULL/worker/事务或参数。

最强反证是快照没有WAITING/已完成全列表，31running不解释第32条当时状态，最终makespan长尾可能根本不是此次tail。较有进展的对象也可能更早释放大批页，暂停它会推迟容量回收；保护合法remaining最小者并不证明保住真实首完成者。更大的SAVE、碎片和后继抢占可能抵消任何尾部变化。16SM没有本实例batch服务曲线，6CPU只是配额；当前诊断页遍历/日志耗时不报性能。改变batch/采样行与公平性后必须有新准确率和复现门，旧字节恢复门与accuracy不能自动继承。

因此值得一次**后继独立候选的机制验证**，不值得凭本快照直接集成或宣称收益。最短门和失败处理只沿上述唯一设计，当前不再增加扫描、资料或测试。原FCFS/最新先抢占的公平目标见[PagedAttention原论文§4.5](https://arxiv.org/html/2309.06180v1)，不套其硬件吞吐结果。
