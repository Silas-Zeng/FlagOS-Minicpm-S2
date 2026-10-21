# 天数BI-V150下一框架优先项：先证实真实KV布局，再准备抢占保存/恢复协议

2026-10-22，framework_innovation，仅本地CPU审阅。本批不新增优化代码、不SSH、不导入模型或GPU框架，不修改SQL+C3稳定源/default。共享代码库仍为团队共用，本文数据仅属天数BI-V150，不能外推沐曦－曦云C500。root要求本批复核和研究落盘后暂停文件写入，供checkpoint与离线包。

## 选择及证据强度

目前最值得继续验证的是**被抢占请求KV保存后释放、恢复完成后重新发布有效前缀**。这是systems已有KV研究的后继协议准备，并非本owner新发明或已经可用的服务优化。它具有比再清理少量Python view更大的可避免工作基数，但**尚无E2E收益证明，也没有已实现的恢复协议**。下一步首先补一次真实运行时布局与executor证据；不能把normal/packed构造门当成生产布局。

已读依据：[`scheduler-kv-innovation`](2026-10-22-scheduler-kv-innovation.md)、[`framework-research-closeout`](2026-10-21-framework-research-closeout.md)、[`memory-lifecycle-feasibility`](2026-10-21-memory-lifecycle-feasibility.md)、[`prefill-graph-feasibility`](2026-10-21-prefill-graph-feasibility.md)、actual184108的executor/core/scheduler/KV管理与worker源码、spec JIT66a168。旧SQL前host profile不能作SQL后预算；现有42层Attention/MLP构造几何也不能代替真实服务关键路径。

真实长输出观察181041出现一次allocation失败：free0、需要1页、queue1，但terminal/private可回收页均0，已经否定当前负载下terminal-drain机会。之后resume的cached前缀2944，相对保守processed floor16702得到13758 **prefix gap exposure**；它不是实际GPU重算token、耗时或准确被逐出物理字节。full-outputreserve115950真实CHECKED/DEFERRED但无吞吐正结果；不重做此策略或已暂停的复杂短期准入影子。

本实例16SM/32GiB，CPU配额6；16K长负载有容量压力，但这些规格和running数量不能证明CPU或HBM已是瓶颈。4K短服务无抢占，不能用它否定或验证抢占恢复；16K128out的两baseline和两mapped轮preempt也均0。mapped单层D29收益约13%最终只得到服务首轮负/复核正，进一步说明层内收益不能直接外推。

## 当前成本门能说明什么

systems/root已完成191545 raw页成本门：42层、每方向672MiB、normal42/packed42各连续与8run，四case的字节/guard/RNG通过。单次roundtrip wall约normal222/235ms、packed120/121ms；event与wall差异较大，且没有CPU quota/并发host记录，不能叫纯DMA带宽、稳定成本或packed布局因果收益。本owner本批读取其已落盘独立结论，**未重复上卡或重做该门审计**。原包装名`copy.py`遮蔽stdlib的失败和修复run都保留。

成本门没有模型、生产页分配/共享/取消、实际runner tensor descriptor或恢复ack。不能拿13758 exposure乘某token速度后直接减掉0.12秒，声称可获大收益。较合理的继续条件是：真实可保存前缀和重放成本明显存在，且最保守的save/restore事务能安全接入；其中任一不成立即降级。

## 精确切口与缺口

| 实际归档源 | 已读切口 | 接入时必须保留的边界 |
|---|---|---|
| `experiments/source-audits/20261021T184108Z-kv-copy/source/vllm/v1/core/sched/scheduler.py`，df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090 | `_preempt_request`1107–1128，1116先free、1120 computed归零；waiting新准入cached-prefix与allocate分支约689–947 | original FCFS/token budget；save ack之前不可把旧页交还重用；不能简单跳过free以制造容量 |
| 同归档`vllm/v1/engine/core.py`，27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71 | `step_with_batch_queue`519–635，547调度、549执行、575入队、590–595 FIFO取结果 | queue/placeholder是提交，不是完成；不提前消费、丢弃或重排输出 |
| 同归档`vllm/v1/executor/uniproc_executor.py`，4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe | `collective_rpc`79–106即使non_block也在调用线程先run_method，后包装Future | 静态类语义不能证明运行时实际executor；不要直接从scheduler访问假定同进程的KV tensor |
| exact e155 runner `vllm_fl/worker/model_runner.py` | KV构建/reshape约7110–7238；`_update_states`1213–1216对新页zero | actual tensor shape/stride/storage_offset/alias先实证；restore须在zero之后、Attention消费之前 |
| actual KVmanager2e91/coordinator9dd0/single22e及backend1219/helper a351 | prefix touch/物理页引用计数/释放、NHD factory和normal/packed reshape | 共享页不重复计量、不覆写其他请求；不能只调num_computed或伪造prefix hit来跳过计算 |

下一次最小只观察记录应在实际worker已初始化KV之后，输出一次executor/worker/runner的类module+qualname，以及42层KV的shape、stride、dtype、device、storage offset、storage别名分组和block_size；只读CPU descriptor，不读tensor值、不GPU同步、不额外分配大buffer。另记录cgroup实际余量，20GiB限额不能拿宿主503GiB代替。该collector/挂点**本批尚未编码或运行**，由root后续授权；stdlib源码采集本身不能得到这些运行时对象。

## 先设计可否定的最小事务，再决定是否实现

只支持exact单卡、无spec/connector/多模态、已证明布局、明确request对象epoch、已确认有效且完整block对齐的前缀。首次协议宁可串行等待真正的copy完成，不先做复杂重叠。必须同时满足：

1. 保存：捕获原物理页及安全有效长度，真实producer依赖后D2H；ack前旧页和host staging保持强引用、不被free/复用。`num_computed_tokens`含optimistic提交，不能直接当已完成长度。
2. 恢复：原容量检查实际分配新页，runner原zero之后H2D，消费者等待完成后才发布有效前缀；不通过假cached token绕过allocator/worker数据协议。
3. 生命周期：request ID复用用epoch隔离，取消/异常不会让仍在copy的页提前复用；共享页、目标alias、host预算均严格约束。只有尚未对后继公布computed/cache时可回原recompute，部分发布后不能静默fallback。
4. 随机与输出：不改temperature/top_p、采样行或request输出归属。减少recompute可能改变原丢弃采样所消耗的全局RNG及batch轨迹，bytewise KV门不能保证端到端逐token相同；必须审原per-request generator/async placeholder及discard路径，并独立accuracy。不得沿用SQL+C3的103/105。

最短反证顺序：先一次真实descriptor（无额外GPU计算）；若executor传输不可接、有效前缀不可证明或host余量不足，停止服务实现。随后仅针对明确事务做CPU状态合同（save失败、取消、ID复用、restore-before-publish），而不是铺泛化测试框架。生产协议准备好才在新隔离源复用**已发生抢占**的181041负载：context-long-screen，输入16384、输出1024、并发64、32请求、seed721201，原SERVER不变；128out无抢占负载不足以验证该事务。首次仅核至少一个真实save/restore/epoch与后继消费、请求完成与清理、实际KV/DB/CPU/host峰值/拷贝字节，失败原样保留；无真实恢复就不报吞吐结论。短门正/小正差均保留，准备默认前再独立accuracy/必要官方验证。本批没有发起这些步骤。

## 与另一个较低风险执行候选的比较

可保留但不升为“大收益主线”的具体点是**Attention每步launch recipe与已编译handle复用**：actual spec JIT66a168的`run`737–790热路径仍经过binder/cache-key、used globals校验和launch metadata；C3每层public unified会重复解释相同step descriptor。已有MM的`FixedTilePair.prepare`使用`compiled[grid](*args)`证明本安装有该接口，但不证明Attention适用或存在明显host预算。首个可能挂点为C3/实际backend1219构造step descriptor后，复用同源码、同配置、同shape/stride/option/SME/global身份的原compiled handle，仅换真实指针/标量，capture或未知hook回原路；不能跨不同layer绑定错误地址或绕过有意义的JIT/global guard。

这条线尚无profile证明剩余CPU关键路径，可能只有小收益；需要先用原kernel热cache、真实3D+2D组合做包含完整argument pack与生命周期的一次短ABBA，bits/stream/capture核对，再服务。**本批不写候选或门，不排设备**。旧SQL前13秒profile、85段现成编译图、C3重复views源码次数都不能证明它有大收益。相比之下，KV恢复有一次真实prefix-gap观察与已测搬运上界线索，因此下一队列优先“实际layout/executor证据+安全事务”；若无法建立可避免重算预算，就如实降级，不把研究潜力当成绩。

当前async/CPUmetadata单次约+0.70%/+0.29%的小信号继续保留；mapped首负/复核正并列，prefix服务负结果也保留。没有任何新候选合入stable/default。本批文档完成后暂停写入，等待root checkpoint及后续具体授权。
