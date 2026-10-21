# 后继victim调度：最小改动路线与反证

2026-10-22，BI-V150，仅CPU设计，**未选评分、未写runtime、未更换victim或运行新门**。230548完整报告由framework唯一执行6eb45验收，本agent只读报告及pin源码，不重跑raw入口。报告SHA `06c16d26e8eee184269d46d09f488da5b63867f90e57900eaaf1484c23ae53e4`；该run32-0/413源/DB51919340三SHA同/idle通过，220.418993s仅诊断，不作性能对照。

## 真实快照能支持什么

首次缺页有31个RUNNING，prompt均16384/max1024、已确认output327..569；free0，exact fast path派生需1页，未直接调用allocator取需求。失败running index1，1个旧queued frame，各请求span1；index0本轮已排1token、output569/remaining上界455，是唯一最小上界请求。原tail index30 output327/remaining697，1045个owned私有页、shared0、hashed1044。31个请求的私有页范围1045..1060，均无shared。

若暂排除失败请求自身、保护index0，并仅检查“释放页数至少cover派生deficit1”，仍有running index2..30共29个结构候选，**原tail本身就在其中**。它们不是已选victim，也未证明save预算/成功、真实重算量或完成时间。remaining仅 `max(0,合法max_tokens−已确认output)`，不减未知placeholder、不使用benchmark编号/未来输出。这里实际看到31个prompt同16384，是snapshot子集证据，不能回填全部32请求逐条分词明细。

## 精确源码与最小变更清单

实际Scheduler `df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090`，KVmanager2e91、pool3fc5、single-type22e3677a；AsyncScheduler da6343d7继承schedule。后继若root授权实现，应在新隔离副本只新增FCFS实际失败分支，不切serve参数或把policy直接改PRIORITY（那会连waiting队列比较一起变）。

1. 仅原allocate_slots返回None后读取真实Request对象/epoch、合法max/output、真实owned/refcnt/null与free；保护至少一个最小剩余上界对象，仅列其它可释放够页者。资格/状态不完整就走原tail分支；候选排序或取舍尚未决定。defer_block_free=True时不能把ref1数量当即时free，首版拒绝此scope。hashed私有页可以回free但不等于hash丢失。每次实际free后仍用**原allocator**重试，不以快照算术代替准入。
2. df780:537–560的PRIORITY路径给出了撤回本轮已scheduled victim的必要账目：从scheduled_running_reqs移除、pop num_scheduled_tokens并返token_budget、pop req_to_new_blocks、spec映射及encoder映射/预算。新分支不能只换self.running.pop对象，也不能漏掉其本轮已新分配页。优先排除spec/encoder等未审scope，原收尾顺序保持。
3. 遍历索引按**移除前物理位置**修正：victim_index<req_index则req_index减1，后方不减；victim就是当前failed request则沿原break。原PRIORITY只在“已scheduled”分支减1，不能把它未经补充泛化到前方曾被cadence/placeholder/零预算skip、却未scheduled的victim，否则会跳过下一请求。无需为撤销本轮调度扣num_computed/placeholder：它们是在1130之后的_update_after_schedule中统一加，失败处本轮尚未发出；旧queued frame不是本轮账目，禁止倒改。
4. 保原_preempt_request:1107–1128（先由调用者移running，原free/encoder/inflight清理，PREEMPTED/computed0/计数，waiting.prepend_request），并保preempted_reqs记录。其后626条件使本轮有preempt就不新准入WAITING；1067原preempted_req_ids仍交worker。多个victim prepend会改变其waiting相对次序，不能另append、强制立即resume或删除计数；返还budget后也不扩大已算出的num_new_tokens。不改旧SchedulerOutput/FIFO/future，不调用提前result/wait，不借V2停放RUNNING绕协议。

存在PRIORITY路径只是可参考的原账目，不是新策略已通过异步/GPU证明。实际queued frame在此快照非空，不能偷加“queue必须空”让候选永远不激活；也不能据原分支存在就声称任意新victim在所有inflight状态都安全。未来最短门必须证明新选择及原consumer/输出状态实际通过。

## 最强反证与不作承诺的部分

- **保护最小remaining可能零改动**：原tail本来就是output最少327、remaining最多697的对象；它已经没有牺牲index0的最小上界455。只加保护不构成新策略，当前快照不能指定另一个victim更优。
- **释放不等于重算全前缀**：single22e:397–409保hash并逆序free；pool3fc5:614–635把无hash页prepend、hashed页append，随后分配才逐页evict。tail1045页中1044 hashed，当前仅需1页时可能先消耗唯一无hash页，让大段前缀仍可APC命中。真正后续命中/淘汰/长尾未采，不能把1045页或约16K prefix全部记成实际GPU浪费，也不能直接预报offload收益。
- **结构可行不等于makespan更好**：更靠近完成的请求可能释放稍多页，但撤掉它的本轮工作、延迟自然释放、改变未来APC/free顺序，也可能拉长最后一个请求。尚无评分/权重/窗口，不能预选“中间进展最佳”或据单快照预测收益。旧full-output-reserve、terminal-drain负例不重做。
- **不能沿用FCFS公平或逐token等价承诺**：新victim选择改变抢占优先性与反复等待风险，即使waiting容器仍FCFS；本设计没有证明防饿死。保持原采样参数、RNG调用及generator对象身份，但活跃集合/顺序改变可改变无独立generator的全局随机数归属，不承诺baseline逐token相同；最终仍需独立accuracy。

下一API可执行切口仅在root明确选择规则后：独立源transformer/纯CPU资格helper，保guard外原代码；一次定向CPU合同覆盖“前方已scheduled撤销、前方skip未scheduled索引、后方/当前victim、无合格者回原路、free不足原重试与队列”，不扩状态机/重跑KV copy套件。再由root决定唯一最短真卡门，证明实际选择/原tokens-consumer/source-DB-KV-post；先有证据再谈性能，不自动集成当前KV协议或任何未授权controller。
