# 抢占对象与恢复长尾：只读研究，尚未实现

本轮限天数BI-V150、MiniCPM5-2B、原2048调度预算及原服务/负载参数。先完成capacity与FULL共同6a观察器的VERIFY0对照；本文只保留一个后继框架假设，不往该pair添加计数器，不改受测源码或请求内容。尚无新实现、设备门或收益。

## 实际证据支持什么

actual scheduler `df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090` 的RUNNING分配失败路径（522–572）在FCFS分支执行 `self.running.pop()`，抢占尾部请求。PRIORITY分支可以选择其它对象，且显式撤销该对象在本次schedule已登记的tokens/blocks/spec/encoder项、返还budget及修正index；不能只把pop替成任意remove而跳过这些工作。原 `_preempt_request` 再释放页、清computed、prepend waiting。当前协议的SAVE/原free/FIFO旧frame处理/恢复发布及cached-resume契约必须保留。

真实FULL214400曾保存R16704，首次RESTORE_DEFERRED中request_tokens16712、free1030<1044页，最后fast_rejects454后才恢复并由原consumer消费8token。它证明发生了等待，不证明454次均匀耗时、最终tail由该victim主导，或当时所有running请求的进展。既有181041只观察门确认本次失败没有确定终态回收机会，不能重新包装成terminal-drain。

context-long原命令指定random输入16384、输出1024、32请求/c64/ignore-eos；FULL214400汇总为524288输入/32768输出。**汇总不能独立证明每条输入长度完全相同**：当前未归档实际datasets采样实现或逐请求长度数组，也没有抢占瞬间的全running进展表。因此不能直接套SJF理论，或凭请求ID后缀猜最后一条就是剩余输出最多者。4K和16K官方是分档负载，不把它们伪装成同一个混合长度队列。

## 唯一新假设与反证

若一个长输入批次中，尾部victim确实进展最少且剩余输出最多，它在等待其它请求腾出容量后，可能仍需最多的串行decode步，成为最终makespan长尾。相反，抢占很接近完成的请求也可能推迟第一次页释放，使所有请求更晚恢复。必须同时评估这两者；“总选进展最多”没有安全或性能定理。

只作条件模型：令W(v)为抢占v后它真正可重新准入的等待、L(v)为其剩余服务、C(v)为SAVE/恢复/重算成本，保留集合最后完成时刻为T_other(v)。最终完成时间至少受 `max(T_other(v), W(v)+C(v)+L(v))` 约束。它不是可直接计算的预测器：EOS/共享页/逐步budget/placeholder和新抢占都会改变各项，合法max_tokens减已确认输出只提供上界。禁止用固定benchmark行号、prompt文本、未来真实输出或离线答案评分。

候选优先研究“保留至少一个最早可能释放容量的请求，再比较其它可释放足够私有页者的进展”，而非改WAITING准入FIFO、全面输出预留、暂停已RUNNING请求或强制batch大小。它改变原FCFS的victim优先级，**不再声称整个抢占策略与原FCFS相同**；是否实现须root另行决定。当前只分析，不选择具体阈值/打分或硬编码第二个请求。

最强反证包括：各请求进展接近、最早完成者无法可靠识别、选其它victim导致更多抢占/更慢首次释放、APC原本已复用大量前缀、受害者不是最终长尾、或saved/restore成本占主导。当前growth full-output reserve与terminal-drain已测反证仍有效，本文不重新实现它们。

## 唯一必要缺证与最短可否定入口

下一步若root选择，只需在原RUNNING `allocate_slots` **实际返回None之后、任何victim选择/原free之前**，仅首次失败记录一份CPU描述符快照，保持原调用结果和后续选择。与当前性能pair分开诊断：

- 本步token budget、req_index、原将选择的尾部对象、实际free及原需求；不提前调用allocate或cache lookup改变统计。
- 全running的原顺序、opaque请求ID/对象身份、num_prompt_tokens、合法max_tokens、已确认num_output_tokens、num_computed_tokens、placeholders、num_tokens/num_preemptions/next-eligible；不记录token内容。
- 本步已scheduled tokens与既有batch_queue对各请求的scheduled span，明确computed含乐观在途部分；只读队列元数据，不读future.done/result/wait。
- 各请求owned页数、ref1/private可释放页数和共享数量；若需要遍历页，明确这是一次诊断CPU成本，不放进性能计时。原free/allocator/hash/历史new_block_ids不变。

最短门沿已有context-long原参数一次，只回答：实际输入/输出上界分布有无差异、尾部victim进展是否明显落后、是否存在不牺牲最早释放者的其它可行victim。没有这样的对象或看不出优势即留负结果，不先造完整模拟器或跑官方全量。若以后实现，必须复用原PRIORITY已有撤销语义并对任意已scheduled victim精确处理，保旧FIFO/异步state/generator/恢复payload；改变batch与全局采样行分配，不能继承103/105准确率。

## 可直接接续的最小观察接入方案

当前只完成具体方案，**尚未新建观察模块或其builder**，不把本文算作已实现。优先使用精确source变换在内存中重建原 `Scheduler.schedule`，唯一插点是RUNNING内层 `while True` 中原 `new_blocks is not None: break` 之后、原“Preempt the lowest-priority request”之前。只有执行已跨过break、即原allocator真实None时，新增一条安全callback；不包装allocator、不额外调用predictor/cache lookup，也不使用frame/GC/trace取局部变量。callback直接接收原 `self/request/num_new_tokens/token_budget/req_index/num_scheduled_tokens`，避免重建预算或把已scheduled当已执行。

只对stable080656/e155/a129的精确init e043追加显式启用footer，默认install(False)无动作；新模块与wrapper不得叠当前capacity/FULL/6a。安装时只接受已自然加载的actual Core27b/Scheduler df780/Async da634/KV2e91/coordinator9dd/single22e/block3fc/Request06b/FullAttentionSpec7e3c和原未包装方法，验证其文件SHA/方法身份、原schedule无freevars。原函数文本必须唯一命中插点；删除新增一行须逐byte逆回原函数，compile只在内存中，不写installed或稳定树。

利用独立Core `step_with_batch_queue` 包装建立ContextVar（原方法恰一次/返回原样/异常原抛/finally reset），待真实constructor后用已审probe的同一MiniCPM BF16/42层/单卡/async V2/FCFS/FullAttention16/deferFreeFalse/no connector等scope核资格。旧probe只复用静态资格代码，**不安装旧probe**。snapshot读取失败单独记录error/completeFalse，原None之后仍执行原victim选择；每Engine最多一次尝试，不保存request/tensor强引用到跨步状态。

该callback拿到的是本次首个失败时刻，不能调用 `future.done/result/wait`，不声称FIFO已经完成。可释放页仅计真实 `ref_cnt==1` 且非null的唯一物理block，不能用owned总数或乘42代替；另独立报hashed/shared分布。每个候选的SAVE安全R按原已确认下界/queued span/至少保留一known token取整，仅记录整数长度与 `R*43008` 是否超过1GiB；不能为高进展请求漏掉host预算/更大SAVE成本。以上是hardware只读复核后补强，不改变当前协议或评分策略。

一个必要CPU合同足够：用元数据stub验证首次失败时callback位置、原方法调用/返回与同一异常、读失败仍走原pop、只一次/ContextVar复原，禁止触碰future或任何tensor值；真实类/源码与snapshot完整性必须由后续单次设备诊断核验。此合同、模块和设备门目前都**未执行/未实现**。

## 一手资料只作权衡，不搬收益

[PagedAttention原论文第4.5节](https://arxiv.org/abs/2309.06180)以公平和防饥饿解释FCFS/最新请求先抢占，并将恢复方式视为独立成本问题。它支持识别当前策略的目的，不证明本机换victim就更快。

[TRAIL原论文](https://proceedings.iclr.cc/paper_files/paper/2025/hash/9eb8b5ccb0de594a16548f7c058fdadf-Abstract-Conference.html)反而限制临近完成请求的抢占，提醒“进展多便优先抢占”可能适得其反。其训练预测器、M/G/1平均延迟目标和其它负载不直接适用本项目makespan，也不引入新模型或预测网络。本文没有使用论文收益数字作本站预测。

[CacheOPT原作者摘要](https://arxiv.org/abs/2503.13773)选择剩余时间长、抢占代价短且TBT约束宽松者，也与简单抢占进展多者相反；其预测/预留/平均服务指标不能作为本站替换victim的支持证据。[Microsoft Research的ICML2026摘要](https://www.microsoft.com/en-us/research/publication/beyond-prediction-tail-aware-scheduling-for-llm-inference/)强调分布变化下预测长度策略的局限和缓存/抢占联动，但其P99/SLO目标也不等于本比赛总耗时。两者仅加强上述反证和快照必要性，不改本轮无收益承诺的结论。
