# 请求调度与KV创新：先回收已确定完成的在途输出，再决定抢占

2026-10-22，systems_innovation。延续现有SQL+C3稳定候选；用户于2026-10-21 16:40Z解除探索冻结。本agent仅CPU读本地原件、准备默认关闭的观察器，没有SSH、设备任务或框架导入。稳定候选、103/105准确率及完整官方对照原件保持不变。本轮所有实测限天数BI-V150，不外推沐曦－曦云C500。

## 证据边界与纠正

BI-V150实际32GiB，候选server.log报告KV521936tokens；16K官方日志长区间running约30、KV约95–97%，4K区间约64请求但KV通常约一半。这支持“长输入下容量压力值得研究”，不直接证明每次抢占有大笔重算、每步mixed图未覆盖或某个精确batch几何。

**纠正前一轮回报：D29/P2019是054501及后继单层门显式构造的几何，不是实际服务测得的逐步形状。** 原a129只输出INSTALLED，没有自然前缀命中计数；持续prompt吞吐只能说明时间区间存在prefill活动，不能倒推出每步D/P、C3命中率或图覆盖。mixed子图方向先等实际父类/reorder/condense源码和最少计数证据，不直接扩成大改。

旧061506的13.95s/8步profile主要是SQL修复前调用链，不能作为SQL+C3仍可省的预算。已有full-output-growth准入策略确已CHECKED/DEFERRED，warm无正吞吐且TTFT更高；本策略不重新预留每请求所有未来输出，不固定降低并发、不改watermark。

## 已审实际源码

新原件目录：`experiments/source-audits/20261021T170854Z-scheduler-kv-c3/source`，其manifest的九文件长度与SHA已本地逐项核对；采集时17:08Z设备68MiB/0%，installed Attention仍bab2。与先前growth实际快照一致的关键文件为：

| 文件 | SHA256 | 机制 |
|---|---|---|
| scheduler.py | df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090 | 435–448跳过已确定到max_tokens且尚有placeholder的请求；522–572分配失败立即抢占；1107–1128释放及清computed；1130以后只推进已调度请求 |
| kv_cache_manager.py | 2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320 | 202–242找可复用前缀；389–420按实际slot需求检查free；435以后才分配/缓存 |
| block_pool.py | 3fc5dfe0ab7ccc6206f6eb7886b2aad15384f92708e6b9f7e5ec7838b7379abe | 542以后从free队列取块并逐出hash；614–635先使用无hash页，hashed页保留队列顺序 |
| gpu_input_batch.py | de1ea4fc9d43fc6079dd375e407c2b6d93f5e1a11f49732d13654c41eaf30a65 | 实际persistent batch，不能把暂停当作无成本标志变化 |

先前实际`single_type_kv_cache_manager.py` SHA22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914，401–409按尾块到前缀次序free；actual AsyncScheduler SHAda6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884，只对本轮scheduled请求增加placeholder，输出处理再扣除。

**重要反证：preempt计数不等于全prompt重算。** scheduler虽把computed置零，free并不自动删除所有KV hash；尾块先逐出，重新准入还会get_computed_blocks，可能复用同请求大量前缀。prefix统计也显式区分preempted。官方中途preemptions=6是服务累计快照，既非全档总数，也不能乘16K当损失token。它为growth消掉一次抢占却没wall收益提供机制上的可能解释，尚未测到真实重算量，不能说已经证实原因。

## 待否定策略（历史假设）：只针对已确定可回收的完成结果

目标是消除一个特定竞争窗口：异步调度已提交某请求的终止步，但完成输出尚未由EngineCore消费，KV仍记为占用；这时下一次schedule因为少数新页不够，可能先逐出另一个长请求。若先按既有FIFO处理这个已在途完成输出，原free路径即可释放其页，再原样调度。16K请求上下文大，完成一次可能释放约千个block；4K本来不紧张，策略应基本不触发。这里只是容量量级，不是当前触发次数。

精确首版逻辑：

1. 挂点在EngineCore调用原schedule之前，先做无副作用预测，且只在实际页余量不足以满足本轮RUNNING请求原slot需求时进入。沿原FCFS与token budget计算num_new_tokens；用实际coordinator predictor和已分配页计需求，不计未来max_tokens预留。范围先限已审单卡、FullAttention、无spec/PP/connector/多模态，其他回原。
2. 在running中只找**已经提交终止步**的请求：复用原scheduler435–448的同一保守判定（placeholder>0且原表达式确认前一步已达到该请求合法max_tokens），不预测未知EOS，不把“快完成”当已完成。按refcount及唯一物理页估计其真正可回收量，不把共享页重复计入。
3. 只有当前已有输出FIFO且这些输出可能解决页缺口时，先消费现有输出，沿原update_from_output/完成free路径处理，再重新检查并调用未改的原schedule。只排空触发时已在途的有限队列，不等待尚未提交的GPU任务；一次机会未解决就回原抢占，不循环等新请求完成。
4. 不提前free、不改页内容/精度/池大小，不改请求token、采样参数、benchmark或服务参数，不更换现成调度配置。区别于growth：正常运行/准入完全不变，只调整“已有输出完成处理”与“即将因缺页而抢占”两个操作的先后。

实际EngineCore现已归档于`experiments/source-audits/20261021T173831Z-engine-core/source/vllm/v1/engine/core.py`，94387字节、SHA `27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71`；同目录coordinator9dd0/single22e也逐项核对长度与SHA。原core539–581在FIFO尚有空间时优先schedule/提交，590才pop最老frame，595才原future.result，604先处理abort，605才update_from_output。因此所述竞争窗口在源码上可发生，**尚未证明当前负载命中**。constructor107–110加载general plugin，221缓存step_fn；独立观察器挂在general register_model末尾，早于绑定step_fn。计数阶段不调用future.done/result、不等待，不改变FIFO或原调度。

不能在原schedule中途raise退出后重来：前面请求可能已allocate/cache_blocks，而_update_after_schedule尚未执行，中止会留下错误的缓存可见性。也不采用“allocate None就continue并停放RUNNING请求”的简单改法：actual scheduler在V2下不为cached请求发送all_token_ids，而现e155 runner1443–1452在unscheduled请求重加入且有输出时会读取这个payload；placeholder未收敛还可能引入旧token。该方案有明确协议风险，不能作为快捷实现。

## 正确性不变量

- 先得到实际完成输出，再通过原生命周期释放页；任何在途GPU读写完成前不得回收。
- 原输出FIFO顺序、异常传播、cancel/finish处理不变；不重复消费future，不重复释放或复活请求。
- 预测器只读，不能触碰refcount/free队列、prefix hash、computed、placeholder或RNG；最终分配始终交给原manager。
- 未命中、无法证实终止、共享/异构/未知scope、无当前在途输出均立即走原逻辑；没有无限等待或长期降并发。
- 不继承C3准确率；调度时机若变化，新候选仍须独立accuracy才能进入默认。计数诊断则不更改语义。

## 最短必要计数与上卡门

先用只观察的独立模块，不变调度，记录少量聚合计数，不逐步打印/采profile：

- 实际RUNNING allocate失败次数及不同schedule次数；当时free、实际所需新页；
- 同一时点符合原终止判定的在途请求数、可回收唯一页、是否足以覆盖缺口；
- 真实preempt前已提交/已确认computed；同一请求**成功重新准入**时实际prefix hit和需要重算的已确认prefix差。不能在每次失败的prefix查询时当作resume计数，也不能把placeholder当已确认KV；
- 队列可取时再补当前在途深度、FIFO位置、实际完成释放页及是否避免原缺页，不记录token内容。

复用已知能暴露一次容量压力的同seed16K/1024/32请求、c64短负载及原服务参数，是已知约220s的最短实用服务门；没有必要先造完整调度模拟器或再跑原13eb。root单卡串行执行。若本轮同时有C3几何计数，可放同一只观察模块，独立区分目的。4K短诊断可证明普通范围回退，但不能用4K没触发否定16K容量机会。

有真实完成回收机会后才做最小策略revision：记录FIRST_CHECKED和FIRST_DRAINED/RETRY，完成数/失败/tokens、原KV与DB状态、CPU配额、终止/取消及所有回退。先用相同SQL+C3基点做一个必要短对照；有变化再按实际需要warm复核。**不设最低收益百分比：小正差也上卡保留，噪声记录待确认，负结果和代码均保留；正确性失败不启用。** 正式两档和accuracy只在准备纳入默认时扩大。

## 可能零收益或变慢的反证

内存失败可能发生在所有请求离终止还远时，根本没有待处理的完成输出；原EngineCore也可能已经主动消费该类输出，则触发次数为零。原抢占的KV大多仍能命中prefix，实际重算本就很少；多一次FIFO等待反而损失CPU/GPU重叠，或者共享页释放不足。上述任何情况都不能强称大收益，也不继续堆复杂ledger。先保留真实计数与零结果，再决定是否实现，避免重复growth的假设。

## 已准备的最小只读观察器（尚未上卡）

`patches/framework/biv150_kv_completion_probe.py`，SHA `a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6`。默认关闭，stdlib导入不载torch/vllm；enabled时只接受八个已审实际源SHA及单卡BF16/42层/FullAttention/builtin Scheduler或AsyncScheduler/V2/FCFS/defer-free关闭/无spec和connector的精确范围。它不实现策略，不能从INSTALLED声称命中。

独立init变换只接受e043，向general `register_model()`末尾append导入/显式enabled，得到`b3b7e2e8d9064c47ac09422741f18c9a3f7079946bc3306a9ccae393d554ca7c`；旧源码/runner和稳定候选不改。八源SHA、精确append/可逆前缀、扰动及重复变换拒绝、compile已核，记录于`analysis/source/kv-completion-probe/cpu-check.json`。

常态仅Core上下文/计数；原RUNNING allocation实际返回None后，才读实际predictor/free、有限在途frame IDs、原终止判定和唯一refcount1私有页。`reclaim_covers_deficit_events`只是容量假说：不读future就不知道输出是否ready，不能当作已可立即回收。preempt前从computed减去所有queued spans得到保守已处理下界，成功resume才读原payload前缀，差值标为**prefix gap exposure，非已执行GPU重算量/时间**。取消或request-ID复用按对象身份删除pending，不持久保存token/跨生命周期ledger。每64步及退出快照均`workload_complete=false`，observer读取错误计数并保持原方法调用/结果/异常。

唯一必要CPU合同`tests/test_biv150_kv_completion_probe.py`一次通过（1项，0.001s）：含失败/单ref与共享页/原terminal predicate、禁止任何future访问、preempt→成功resume、诊断读取失败仍原调用一次及原异常透传。它仅验证不干预合同，不代替真实EngineCore scope与失败触发；框架owner正在独立审阅。下一设备门由root串行安排，必须看到真实EngineCore first_checked eligible及真实失败/抢占计数，零触发也保留。

## 181041真实计数：当前负载不支持完成回收，不实现drain

完整原件`experiments/framework/20261021T181041Z-kv-completion-context16k-long{,-control}`，411源码SHA/a4de/initb3b7/e155/bc51及原SERVER/seed721201已本地核实。32成功0失败/524288in32768out，220.345997615717秒仅诊断，不作性能对比；实际KV521840。EngineCore199565的35份probe JSON与原log逐项匹配，eligible=true/batchqueue2，末周期2112 core calls/2109 schedule calls、1次实际RUNNING分配失败/抢占/成功resume，obs errors0。快照并非全程；原metrics preempt0→1与之对应。

失败时free0、原required1页、queue1，但terminal pending0/单ref private0/covers0。因此该次抢占不能通过所提“先消费终止输出”避免，**不继续实现drain**。不能因为core存在理论窗口就扩成策略。成功resume实际cache hit2944、保守processed-prefix floor16702，差13758为`prefix gap exposure`；它不是已执行GPU重算token或时间，不能直接拿13758×每token成本报收益。

前后SQLite实体physical1593/schemaa0a590/logical90e9完全相同、516表19270行，CPU6；18:17:30.243359Z完整post68MiB/0%、9031双栈关闭、无GPU进程、owned退出或Z。补充审计JSON位于run/`independent-diagnostic-review.json`。下一研究限CPU设计更短期准入预算及KV保留/host offload，先分析正确性和反证；不复用已否定full-output reserve、不改变现有默认或启动参数。
