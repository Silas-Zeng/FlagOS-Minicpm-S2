# 天数BI-V150：015315碎片前缀的反证与接口审阅，仅文档

当前原FULL/progress首个A/B的A为root独占运行的020721/runner252046、实际KV521936。本文不改它或任何runtime，不新增套件/设备；先完成当前pair，再由root决定是否探索较短保存前缀。用户暂缓GitHub/PR，本轮无外部写入。

已读[旧fragment计划](2026-10-22-kv-fragment-aware-prefix-plan.md)、冻结FULL事务84be的plan_snapshot/Snapshot/绑定/发布、worker5d9a的完整页命令/预算/FULL覆盖，以及实际015315 SAVE/RESTORE_DEFERRED/consumer原日志。旧计划基于200957且当时尚无恢复；这里仅更新实际证据与接口边界，不将旧计划误记为实现。

## 真实几何与能否推收益

015315已通过同selected对象的FULL字节/原consumer机制。直接从其SAVE实际逻辑页数组计算：

| 实际逻辑范围 | token数 | 页数 | 源递增段 | 42层SAVE调用 | payload |
|---|---:|---:|---:|---:|---:|
| 最大安全前缀R0 | 16928 | 1058 | 37 | 1554 | 728039424B / 694.3125MiB |
| 前1024页 | 16384 | 1024 | 3 | 126 | 704643072B / 672MiB |
| 后34页 | 544 | 34 | 34 | 1428 | 23396352B / 22.3125MiB |

这里16384仅是**本次源页图前三个连续段末端**，不是按prompt长度、benchmark行号或16K档位构造策略。未来若选择，只能从本请求实际安全页图/动态段边界与经证明的预算选择k；无时间成本依据时不能指定J=126或固定1024页。原页号次序不可排序来改变host逻辑内容。

后34页占约3.2% payload却占约91.9% SAVE调用，说明调用几何值得研究，**不证明已省时间**。减少SAVE源调用1554→126的几何准确；pin/producer device fence/ACK固定成本不随页数同比下降。未来RESTORE目的数组未生成，不能承诺少1428个H2D调用。015315实际目的65runs/FULL2730calls也不是截短后的预测。

额外544 token是带完整历史上下文的**已知后缀重算**，不是544个新输出或544次独立decode。可能增加42层MM/Attention成本、触发新shape调优、改变batch与采样路径；当前没有相应时间测量，收益符号未知。

## 最强容量反证：少恢复页不等于更早准入

015315首条RESTORE_DEFERRED实际记录 `free_blocks=1044`、`request_tokens=16937`、`full_sequence_must_fit=True`。原R0=16928需1058页，故原capacity_lower_bound立即拒绝。

若改保存R=16384/1024页，1024≤1044仅使旧快速下界放行。actual KVManager2e91:372–387仍先做full-sequence gate：本事务没有owned或local computed hits，FullAttention完整已知16937 token需 `ceil(16937/16)=1059` 页；external R改变实际先分配的prefix量，**不把完整已知长度改小**。free1044仍不能通过原准入。随后原计算需要的suffix页也不会消失，总逻辑驻留仍约1059页，而非1024。

因此不能将缩R描述成“可提前34页恢复”或从页数断言降低这轮等待。它甚至可能让原先数百次cheap fast-reject进入原完整allocator/digest路径，增加CPU成本；不能把015315的fast454硬当未来相同次数或各步均匀耗时。若未来实现要保持快拒效率，必须单独证明适用FullAttention/无owned/hits的完整已知容量下界，不能伪造request.num_tokens、关闭reserve或换启动参数。本文不实现该附加策略。

## 明确需要的新接口与可原样复用的部分

| 挂点/契约 | 必须明确的变更或保持项 |
|---|---|
| plan_snapshot→Transaction之间 | 原plan_snapshot仍用真实issued/全部queued/known−1得到最大安全R0。当前没有缩R接口；须另建显式纯规划步骤，选完整k页≤R0/16后用**同Key、全部原pending_frames、真实known前R的digest、逻辑前k页**构造新Snapshot。不能伪造issued/queued使旧函数碰巧返回目标R。 |
| victim资格/日志/后验 | 72942当前selected_prefix_tokens表示最大安全R0且验收要求与SAVE完全相同。缩R后必须明示safe_R0与saved_R、选择依据/源段数/字节、未保存suffix长度，并相应审计R≤R0和真实命令；不能只放宽旧断言悄悄接受。若只测fragment，原victim规则/安全资格先保持，避免把短R让更多victim进cap的变化混入。 |
| Transaction/HostSlot | Snapshot本身允许更短完整页；nbytes由R派生，slot预算、命令页数、digest/epoch、源释放与pending-frame状态都必须以新Snapshot真实值一致。旧84be状态机可参数化复用，不需要伪ZERO或假FULL ACK；但“无R必须最大前提”不等于已有新selector。 |
| 原_preempt_request/free | SAVE真实settled后仍原样释放该请求**全部旧owned页**，不能只free保存的k页或保留未登记旧suffix映射。请求已知prompt/输出/token IDs/输出数/max/RNG/generator保留，原computed归0；未保存的旧KV不再可用。 |
| _try_restore/allocator | 真实分配外部前缀num_external_computed_tokens=R、delay-cache和原full_sequence_must_fit不变；只恢复本次新分配的完整私有prefix k页。当前FULL与page-order要求owned恰好k、num_cached0/ref1/unhashed/未bind未publish，这些不得放松。完整已知准入检查仍保留。 |
| worker SAVE/FULL/回读 | 5d9a的pages=R/16、bytes=R×43008、42层pinned整页、完整coverage/fence/event与可选回读已经参数化；它不会替planner选择R。只要命令/slot一致可原样复用，不能把少存544token声称恢复了R0，也不能让host旧大形状冒充新小R。 |
| 原后续schedule/表 | 恢复ACK后仅tentative computed=R。原schedule按真实known−R及原token budget计算已知suffix，正常追加后缀页，cache按新逻辑表绑定。原full-block replacement应含恢复prefix与后来追加suffix，不是仅k页表。原分配失败/预算退出须settled rollback，不发布后再fallback。 |
| cached-resume/consumer | 保全部原known IDs、confirmed输出数与cached-state/generator，computed只能R；不删544个已生成token、不减max或输出请求。先原runner检查，再由原消费者消费真正调度结果；consumer token数动态解析，不硬套9。 |

## 合法已知后缀计算与数值边界

015315原R0=16928，真实恢复输出consumer9；若同一恢复时刻保持原known16937且budget足够，截R=16384后逻辑上待算known suffix为553，而非9，恰好多544。这是**固定known/预算条件下的源码推导**，不是执行过的consumer553或未来实际长度；若更早/更晚恢复、预算不足或再次抢占，实际会变。

这些token已经存在于原all_token_ids：普通runner取它们作为输入重建KV，而不是请求模型再次生成它们。不得另调sampler补token，不删原输出或重置generator。多个chunk仍走原prefill/discard/async cadence，不能为证明“无额外采样”绕过现有逻辑；当前只读接口不足以证明全部跨chunk路径逐token RNG相同。

即使已恢复prefix的42层字节完全相同，suffix重算的M/Attention归约/批次、logits选择和全局采样行可能变化；保存generator对象身份也不证明全局随机行分配或最终输出等价。未来必须验证原known长度/输出数、实际输入与新增页、最终原consumer及必要准确率，不能继承103/105，也不能把只校验k页FULL回读扩大为未保存suffix数值正确证明。

## 交接与停止点

本轮只完成真实几何/容量反证和精确接口审阅，不制定固定调用阈值，不新增Snapshot构造器/runtime/计数器/测试或上卡。优先等当前共同观察器VERIFY0 A/B结果；若victim候选本身没有收益，也不能因此直接把fragment当下一已证方案。后继须root单独选择一个明确的短前缀规则及最短机制门，原始015315页数组与失败/DB变化继续保留。
