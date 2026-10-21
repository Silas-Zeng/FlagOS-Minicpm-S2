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

## 最小只读观察器（首次CPU准备，后已181041上卡）

`patches/framework/biv150_kv_completion_probe.py`，SHA `a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6`。默认关闭，stdlib导入不载torch/vllm；enabled时只接受八个已审实际源SHA及单卡BF16/42层/FullAttention/builtin Scheduler或AsyncScheduler/V2/FCFS/defer-free关闭/无spec和connector的精确范围。它不实现策略，不能从INSTALLED声称命中。

独立init变换只接受e043，向general `register_model()`末尾append导入/显式enabled，得到`b3b7e2e8d9064c47ac09422741f18c9a3f7079946bc3306a9ccae393d554ca7c`；旧源码/runner和稳定候选不改。八源SHA、精确append/可逆前缀、扰动及重复变换拒绝、compile已核，记录于`analysis/source/kv-completion-probe/cpu-check.json`。

常态仅Core上下文/计数；原RUNNING allocation实际返回None后，才读实际predictor/free、有限在途frame IDs、原终止判定和唯一refcount1私有页。`reclaim_covers_deficit_events`只是容量假说：不读future就不知道输出是否ready，不能当作已可立即回收。preempt前从computed减去所有queued spans得到保守已处理下界，成功resume才读原payload前缀，差值标为**prefix gap exposure，非已执行GPU重算量/时间**。取消或request-ID复用按对象身份删除pending，不持久保存token/跨生命周期ledger。每64步及退出快照均`workload_complete=false`，observer读取错误计数并保持原方法调用/结果/异常。

唯一必要CPU合同`tests/test_biv150_kv_completion_probe.py`一次通过（1项，0.001s）：含失败/单ref与共享页/原terminal predicate、禁止任何future访问、preempt→成功resume、诊断读取失败仍原调用一次及原异常透传。它仅验证不干预合同，不代替真实EngineCore scope与失败触发；框架owner随后全文独立审阅无阻断，root安排181041真实计数门，结果见下节。

## 181041真实计数：当前负载不支持完成回收，不实现drain

完整原件`experiments/framework/20261021T181041Z-kv-completion-context16k-long{,-control}`，411源码SHA/a4de/initb3b7/e155/bc51及原SERVER/seed721201已本地核实。32成功0失败/524288in32768out，220.345997615717秒仅诊断，不作性能对比；实际KV521840。EngineCore199565的35份probe JSON与原log逐项匹配，eligible=true/batchqueue2，末周期2112 core calls/2109 schedule calls、1次实际RUNNING分配失败/抢占/成功resume，obs errors0。快照并非全程；原metrics preempt0→1与之对应。

失败时free0、原required1页、queue1，但terminal pending0/单ref private0/covers0。因此该次抢占不能通过所提“先消费终止输出”避免，**不继续实现drain**。不能因为core存在理论窗口就扩成策略。成功resume实际cache hit2944、保守processed-prefix floor16702，差13758为`prefix gap exposure`；它不是已执行GPU重算token或时间，不能直接拿13758×每token成本报收益。

前后SQLite实体physical1593/schemaa0a590/logical90e9完全相同、516表19270行，CPU6；18:17:30.243359Z完整post68MiB/0%、9031双栈关闭、无GPU进程、owned退出或Z。补充审计JSON位于run/`independent-diagnostic-review.json`。下一研究限CPU设计更短期准入预算及KV保留/host offload，先分析正确性和反证；不复用已否定full-output reserve、不改变现有默认或启动参数。

## 后继方向一：只在准入计算“直到首个可保证完成”的KV峰值

这是CPU设计，尚未实现策略/新计数器或安排设备。目标仍是避免RUNNING抢占，同时减少full-output reserve对并发及TTFT的代价；只可在原WAITING/PREEMPTED准入点、原allocate产生副作用之前拒绝本次准入，保留原FCFS break。不能停放已RUNNING请求，避免V2 all_token_ids/placeholder重加入协议风险。只读预算不改请求max_tokens、顺序、采样或服务参数。

最小候选边界是实际df780/2e91/9dd0/22e单FullAttention、block16、单卡/无spec/connector/多模态、每步一个sample、PP1、原token budget。用合法Request hard max与已分配页计算后续增长，考虑正在prefill的输入尾部债及ref0 prefix touch；不能用“现在prefill尚未分配”把它当作免费。原full_sequence_must_fit只是本次全输入能否放下，不持久替每个已准入prefill保留完整输入页。

若全部已RUNNING请求确为可连续推进的decode，且其FCFS位置/2048token budget保证每轮都推进，才可用有证明的剩余轮数H；每请求未来新增页为`max(ceil(min(prompt+max_tokens, computed+H)/16)-当前已分配页,0)`，候选还需其全输入及H内可到达的输出页、cached prefix touch。H必须包括batchqueue2的输出消费滞后，不能把placeholder当已确认输出。仅取所有请求`min(max_tokens-num_output_tokens)`通常不成立：较早长prefill可以耗尽预算，后面的所谓最早完成者未必每轮进展。

一个更保守、可证明进展的基准是FCFS running队首：无阻塞且原PP1/cadence成立时，队首prefill每轮先吃原token budget，之后每轮decode。因此可先用队首剩余prefill轮数+合法剩余输出+队列滞后的上界作为H。精确减少其余请求的prefill债，需要按当前原顺序重放小型**纯整数**预算/placeholder状态，获得H内峰值页，不能只把当前decode数乘H；这仍需对actual schedule/_update_after_schedule逐项建立合同，不能把估算直接当内存安全证明。

主要反证与停止条件：

- **all-running-decode才启用可能已经太迟。** 31个16K prefill可能此前已准入，输出增长债已存在，此后没有新准入点可拦；这种收窄策略可零命中。为规避风险直接跳过所有prefill又会牺牲并发，接近已否定的full reserve。
- 此负载16K输入/1K输出，队首在后续prefill期间只比末请求提前数百decode步；短H可能仍使31份上下文装不下，和full reserve做出同一决策。不能因为公式预留少一些就预报收益。
- “直到第一次完成”只保护有限窗口，不自动保证以后永不缺页。第一次释放后若仍有巨大剩余输入债，且没有新准入触发重算预算，仍可再次缺页；需要证明当前固定负载的后续峰值，或明确策略只降低风险而不宣称消除抢占。早EOS会改变后续预算释放/推进顺序，也不能未经证明就认为max-length整数重放是全路径上界。
- 空running必须原路准入可容纳的超长合法请求，避免饿死；新门只拒绝当前队头，不跳过它，取消/完成没有持久reservation要释放。原分配前只能读，原分配失败仍由原逻辑处理，不能中途撤销部分schedule。

最短下一切口应先是影子预算：仅在**原准入检查本来可以通过**的少量时刻采集CPU标量（FCFS index、computed、prompt/合法max、placeholder、next-eligible、实际页数、prefix ref0、新页需求、原budget和queue深度），不含token、不等待future。统计H来源是否有进展证明、预估峰值、是否与旧full reserve完全同决策；所有失败/无差异留存。一次已知16K/1024/32请求负载足够判是否值得实现，不先跑正式全量。当前35份probe不含这些准入描述，不能离线伪造它们或给出收益数字。若只有和旧growth相同的少并发行为，就保留反证并停止，不重复大accuracy。

## 后继方向二：抢占前保存KV，恢复时避免前缀缺口

数据量由已审模型结构算出，不依赖整板宣传值：`42层 × 2(K/V) × 2 KV heads × 128 × 2字节 = 43008字节/token`；16K上下文 **704643072字节=672MiB**，一个逻辑16-token全层block为672KiB。floor16702对应685.04296875MiB；13758 exposure对应564.29296875MiB。它们只是数据量，**后者既不是已测被逐出的物理字节，也不是必须保存的准确集合**。首次安全原型应保存确认有效、完整block对齐的前缀，不能复制尚未完成placeholder的尾部。

没有实测本实例PCIe协商宽度、D2H/H2D有效带宽或DMA并发，不能拿整板PCIe4x16或HBM数字代替。下表仅按单向有效GB/s假设给出672MiB完整前缀D2H+H2D的理想传输时间，未计散页/事件/host分配/CPU提交成本：

| 假设单向有效带宽 | 一次保存+恢复 |
|---:|---:|
| 4 GB/s | 352.321536 ms |
| 8 GB/s | 176.160768 ms |
| 16 GB/s | 88.080384 ms |
| 24 GB/s | 58.720256 ms |

当前容器限制20GiB，不是宿主可见503GiB都能用。至少需记录当前memory.current、pinned分配是否成功和限额；一份672MiB host条目有机会容纳，但没有实际余量证据前不作保证。GPU若先额外分配672MiB packing buffer，会改变startup KV容量，不是免费操作。应优先按实际物理页连续run合并直接D2H/H2D，或用有界小staging；每层每block约16KiB，若逐页逐K/V提交可产生数万次小copy，CPU6核开销可完全吃掉理论带宽优势。actual e155的KV创建/reshape在7110–7238，支持packed backing和stride-order，必须读真实shape/stride与alias后选实现，不能假设42个标准连续tensor。

只保HBM页不offload也有明显反证：缺页时free0，没有其它空闲容量；原free已按尾到前缀释放并保留hash，prefix自然缓存已存在。仅给被抢占前缀调Lru优先级可能把其它必需页挤掉，不能凭“保留KV”四个字制造容量。新实现必须减少实际重算/搬运成本，不能只开一个现有offload配置或切现成connector冒充改造。

### 安全切口与当前缺的实际源码

EngineCore管理CPU页元数据，实际KV tensor在模型worker；日志同有EngineCore前缀不足以证明executor/worker同一线程或同一进程。需要实际executor类别及安装字节后才决定调用路径。已有core27b、scheduler df780、output f281、request06b1和e155 runner可定位生命周期，但尚缺：`vllm/v1/executor/abstract.py`、实际executor实现、`vllm/v1/worker/kv_connector_model_runner_mixin.py`、`vllm/distributed/kv_transfer/kv_connector/utils.py`、`vllm/v1/outputs.py`及实际KV reshape helper/backend。只读取源即可，不能用新版本分支代替。

候选必须有以下状态机，尚未实现：

1. **保存后才free。** `_preempt_request`释放前记录request epoch/原block IDs/已确认有效长度；worker在所有先前KV写入的真实compute-stream事件之后保存到pinned host，保存完成ack之前原GPU页不能复用。scheduler不能把“copy已提交”当完成；必要的首版可同步等待一次真实事件，以正确性为先，再判断能否重叠。observer仍不做任何等待。
2. **恢复后才发布可用前缀。** 重新准入须先通过原容量检查并实际分配目标页，携带明确restore命令/epoch；worker在新页zero之后、Attention读之前完成H2D依赖。不能仅把Request.num_computed_tokens改成16702或塞假prefix-hit，然后让原runner读未恢复的页。原`_update_states`1213–1216会zero新页，恢复顺序放错会把刚恢复数据清掉。V2新请求数据/后续batch及cache hash发布需要真实ack/原输出协议保证。
3. **取消/异常/复用隔离。** request ID复用用epoch区分；D2H/H2D事件完成前host buffer不复用，cancel不能提前free异步copy仍会读的页。失败只可在尚未发布computed/cache前回原recompute；部分恢复已经对后续batch可见时不能静默回退。prefix共享/packed alias必须按实际物理页/refcount处理，不能覆盖其它请求仍使用的缓存。

这不是十行CPU包装可安全完成的事情。最短可测试切口先是独立“实际layout的42层、16K、散页与连续run保存→原页毒化/复用→恢复”的GPU门，检查全KV bitwise、未触guard/共享页、事件前后可见性、固定地址消费者、取消/epoch及RNG，记录CPU wall和必要事件、实际copy字节/提交数/host峰值。使用positive basic原字节检查，避免本轮negative高级索引guard误报。只有往返成本和正确性有信号，才接新的真实restore命令；随后一次同参数16K长输出服务门查看实际恢复前缀、避免的exposure与吞吐/TTFT。不能把672MiB带宽微测等同于全服务收益。

公开一手资料只作机制边界，不替代本实例实测：[PagedAttention论文](https://arxiv.org/abs/2309.06180)解释分页与共享；[PyTorch官方异步/pinned传输教程](https://docs.pytorch.org/tutorials/intermediate/pinmem_nonblock.html)明确pinned源生命周期、D2H读前同步及重叠的条件。该文档运行时比本机Torch2.10/Corex新，不能据此假定BI-V150的实际DMA/事件实现。当前两条方向都只有设计和反证，没有新策略代码、设备成绩或accuracy。


## 184108实际依赖齐备与KV复制门定稿（最新）

此前缺executor/worker/KV-mixin/outputs/reshape源码的段落仅采集前历史；actual13份现已取回并核对complete/missing0/mismatch0。重要布局纠正：actual Triton1219 NHD是 `(blocks,2,block_size,kv_heads,head_size)`，不是KV-first。a351 helper支持normal或packed offset/stride；目前没有服务tensor运行时descriptor，不能宣称服务已测某种布局。静态uni分支也不能直接当runtime executor证据。

root已选择先测抢占KV保存/恢复成本，暂停复杂准入影子，不实现terminal drain。独立raw页复制模块c95f与最短门最终d841冻结，normal42/packed42×1run/8run，16K每方向672MiB；producer→save completion→poison→restore completion→consumer的严格生命周期、全byte/guard/RNG检查已跨硬件owner独立审阅。只做一项必要CPU合同1pass/0.002s，无设备结果。完整scope/精确SHA/命令和最后guard delta见 `analysis/2026-10-22-kv-page-copy-gate.md`，不把构造geometry/一次传输成本当服务协议、accuracy或E2E收益。


## 191545修正版KV门完成：四case正确，成本仅单样本

`experiments/framework/20261021T191545Z-kv-page-copy-gate{,-control}` 已完整本地，包SHA **7b491c525759e3320ecac8cd385d31fd1f434784ade63eef16bb2ab02a554316**。独立仅读8源SHA与93eb/c95f/1219/a351固定身份一致，19:16:59.928412Z exit0；normal42/packed42各contiguous与fragmented8四case，各untimed/timed两pass，40项checks与4项RNG均true。保存/恢复全byte、两guard不重写、未选页poison、42 actual-factory view消费者全部通过；shape(1058,2,16,2,128)、normal stride0=8192/offset41=0、packed stride0=344064/offset41=335872符合源码，每方向704643072B，copy调用分别42/336/1/8。原191017导入失败及修复加载证据保留；不是隐藏失败后只挑通过。

| 构造布局/页映射 | save wall ms | restore wall ms | roundtrip wall ms | save event ms | restore event ms |
|---|---:|---:|---:|---:|---:|
| normal42/contiguous | 25.946121 | 196.106984 | 222.053105 | 24.756731 | 26.488735 |
| normal42/fragmented8 | 27.699296 | 207.570993 | 235.270289 | 25.073376 | 194.106018 |
| packed42/contiguous | 24.943508 | 95.012686 | 119.956194 | 24.734741 | 26.496109 |
| packed42/fragmented8 | 25.027936 | 95.688994 | 120.716930 | 24.747791 | 26.758972 |

方向wall是host提交至事件同步返回，timing Event已预初始化，producer设置/poison/consumerclone/分配与CPUoracle窗外；保存事件完成后才读pinned/毒化，恢复事件后consumer才读取。每geometry仅一组warm成本，normal连续restore wall196ms/event26ms，而normal8run event194ms，host提交/调度混杂尚未分离，copy gate没有CPU quota或并行host工作负载记录。**不称稳定DMA带宽、packed因果加速或服务收益，不将event直接作纯硬件传输时间。** 各case显式host1432682496B、raw GPU728039424B；GPUallocated peak1456078848B含测试consumerclone，cgroup仅时点/20GiB限额非host峰值。

owner19:18:05.738516Z后态单卡68MiB/0%、9031双栈闭/无GPU进程，owned退出或Z、8源无failures核实。全量tensor没有另存binary；本地独立检查冻结代码的完整oracle和原结果，不重新运行GPU。结果保存 `run/independent-gate-review.json` 和 `analysis/2026-10-22-kv-page-copy-result.json`；registry93数据行×16列/queue69均LF。

这一门仍没有权重/真实runner tensor布局/Attention数学/请求allocator/跨进程恢复protocol/模型accuracy。后继服务入口若继续，须先证明actual executor与持有KV view的worker生命周期、save完成前不free、zero后restore且Attention前ack、host pinned强引用/epoch/cancel及失败回退；这些只是后继约束，**本批没有实现或运行**。181041 gap13758依旧只是exposure，不能把约0.12–0.24秒copywall替换成假定GPU重算节省；不能开启现成connector模式冒充实现。
