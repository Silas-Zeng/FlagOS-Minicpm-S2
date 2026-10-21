# 首次失败快照的硬件与请求判读标准（230548原件已到）

仅天数 BI-V150 / MiniCPM5-2B；本实例16SM、32GiB、CPU配额6、主机20GiB。本文最初准备后验判读，不新增策略、运行时、测试或设备任务，不把A2/B2混入快照诊断。旧d38/429/78e包装因自然加载时序风险hold、未部署；后继c6b3/ce4e/6ec5已改为Core首次step延迟核验安装。现230548真实快照已经产生，独立硬件/请求专项见[实际解读](2026-10-22-preemption-snapshot-230548-hardware.md)。下文先验、条件算式仍保留原适用条件，不将其改写成实测。

## 先验单位与本实例约束

| 项目 | 可用的确切换算/事实 | 对选择的限制 |
|---|---|---|
| GQA/BF16 KV | 42层×K/V2×KV头2×head128×2B = 43008B/token；16token完整块688128B | 引用计数/allocator按全模型逻辑block计数，**不能再乘42算可释放页**；实际搬运则有42份独立storage |
| 长输入 | 精确16384token请求的KV为704643072B=672MiB | 少抢占一个长输入可能避免很大恢复/重算，但R并不是时间，尤其本地APC命中与物理碎片尚未观察 |
| 实际KV池 | 最近同观察器pair为521840token/32615池槽，actual BlockPool另将ID0取作null，非null可分上界32614 | 不能按32GiB除每请求字节得“应容纳请求数”，原权重、activation、nonTorch估计项及原预算已占空间；池槽数不是当前free |
| 32请求条件例 | 若32条恰16K、无共享且所有prompt同时驻留，则需32768非null块/21GiB；忽略null已超过总槽153块，计null则缺154块=105971712B | 这是条件算式，不证明真实首失败已同时驻留32条完整prompt；还要读实际running/长度/APC/shared与已分配状态 |
| Decode增长条件例 | 若32条同一步各新增1token，逻辑KV增加1376256B=1.3125MiB；真实新页只在16token边界跳增 | 一次缺1块不代表只需保留1token容量；释放整条约千页能跨过当前失败，却不保证此后无再抢占 |
| 静态host单slot | 1GiB最多容纳1560完整块=24960token，尚未计余量/校验buffer/实际cgroup current | `R×43008≤1GiB`只是payload上界，不能当可成功SAVE/实际pinned预算判断 |
| 20GiB主机限制 | 实际GPU KV池约20.9GiB，已经超过主机总限制 | 不能全池镜像，也不能为改变victim同时承诺多个约0.67GiB slot；本次没有改预算/协议 |
| 16SM、GQA2 | Cache只存2个KV头，query仍16头 | 不能将少一请求当吞吐线性少1/N，不能把小KV字节直接当Attention compute同比下降；没有本实例batch服务曲线 |
| CPU6/42storage | 当前恢复同一物理段每层一次提交，1个正向段对应42calls | 一次逐页遍历/大JSON有主机成本，诊断耗时不报性能；当前快照不记录page_ids/runs，不能按owned数量推复制调用数 |

上表字节换算是纯整数推导；设备/布局事实沿已封存184108/195012及222731/223613专项，见 [4MiB与首pair专项](2026-10-22-kv-memory-four-mib-observation.md)、[KV布局备忘](2026-10-22-kv-layout-transfer-research.md)。null槽依据actual `block_pool.py` 3fc5的188–192行，不另做设备采样。CPU6是配额，不等于6个完全空闲专用核；16SM是本slice，不套整板/A100参数。

## 拿到原件后的顺序

1. 先确认新隔离源/最终pin，`CORE_HOOKED`只作安装预检；按实际Engine PID核唯一的 `CORE_HOOKED→SCHEDULE_ARMED→FIRST_CHECKED eligible→FIRST_RUNNING_FAILURE complete=True` 次序，真正失败快照恰一份。前端其它PID的装载/拒绝事件另列，不能当第二份快照。只有入口已包裹、实际Engine拒绝/INCOMPLETE或没有失败，都不足以解读victim机会。该事件必须在原RUNNING allocator实际None之后、原tail pop之前。
2. 校验running对象/ID唯一、failed_request_id对应failed_running_index、原tail ID等于running最后一项。running_count取实际值，不强迫等于负载总32；queued中出现不在当前running的ID也不能擅自删除或视为错误。
3. 按真实queued SchedulerOutput的scheduled token数逐rid求和；不读future，不以placeholder或当前schedule新登记项代替已排队span。复算每行 `stable=max(0,min(issued−queued_span,known−1))`，`R=16×floor(stable/16)`。本schedule未issued项只单列，不重复扣。
4. 只有R≥16、对应完整非null/唯一逻辑页覆盖、nonstreaming及静态cap等描述均成立，才标为“值得审后续SAVE资格”；不称copy已安全或可成功。缺页、R0、超cap各自保留，不修数字使其通过。
5. 需求只用已标derived的exact FullAttention RUNNING快径值N；和原free F核对是否N>F。若不一致，先列未观测/守卫问题，不为使快照“合理”而额外调用allocator或cache predictor。
6. 然后才比较原tail与其它请求的现有进展和容量，不选择策略、不把条件模型当预测时间。

## 关键字段的有效含义与禁区

| 字段 | 能回答 | 不能回答 |
|---|---|---|
| `confirmed_output_tokens`、`legal_max_output_tokens` | 已确认进展、合法剩余输出上界 | 真实剩余EOS长度、未来最终完成时刻；不能按ID/benchmark行号猜 |
| `issued_computed_tokens`、`queued_scheduled_span`、placeholders | 乐观提交与未消费输出窗口的区别 | GPU已完成多少；即使Future实际完成也不读取它 |
| `snapshot_prefix_tokens`、逻辑coverage | 不超过issued−queued/known−1的完整页候选前缀 | 所有页值/布局/哈希都已验证、原source后续不会写、当前SAVE成功 |
| `private_single_ref_unique_pages` | 该请求单独free时可能令ref变0的非null唯一物理页数 | protocol新分配的“私有unhashed”页资格；这里可包括hashed页，二者含义不同 |
| `shared_unique_pages` | ref>1，单独抢占此请求不会释放这些页 | 多victim联合free的真实收益；本次没有联合选择/全局物理并集 |
| `owned_nonnull_unique_pages` | 每请求自有映射去重数量 | 全running物理页并集；跨请求shared会重复，不能简单相加当占池量 |
| `hashed_unique_pages` | 有hash的owned页数量 | APC实际命中长度、hash来源/数值相等、将来是否仍驻留 |
| remaining上界、`is_prefill_chunk`、next eligible | 当前阶段/调度资格的CPU描述 | 真实服务速度、最早释放者、是否是最终makespan长尾 |
| free、derived required | 当前这一个失败请求的容量缺口 | 所有后续decode的保留预算、整个队列稳定性或OOM概率 |

“可释放”字段只解释当前ref计数：hashed的ref1块free后仍可作为APC缓存留在free queue，free容量会增加；不能因有hash就从可释放量扣掉，也不能因此认定其恢复免费。ref0 APC hit被touch时会消耗free，已有 `P−H+E` 下界仍成立，见 [原物理APC前缀研究](2026-10-22-kv-surviving-prefix-reuse-plan.md)。

## 一次快照最多给出的可证伪判断

先列原tail行与所有其它行的实际prompt/output上界、确认进展、R与单引用页量，保原顺序。只计算必要条件：若失败请求继续保留、预算与其它条件不变，候选v单独free需要 `F + U(v) ≥ N`，U为唯一ref1非null页数。v就是failed_request时，该请求原本会退出本轮，不能套“让它继续成功”的相同局部条件。

该条件满足仍不等于优选。候选若已经被本schedule登记，真正换victim需要原PRIORITY已有撤销token/budget/block/spec/encoder语义；当前只观察，不能简单remove任意对象。即使U更大，较早完成者被暂停也可能推迟第一次大批页释放；反过来原tail若进展少，也不证明它最后最慢。一次快照没有W(v)等待时间、实际L(v)剩余服务或恢复C(v)阶段时间。

当前快照还没有WAITING/已完成全列表。实际running少于32时，不能猜其它请求已经完成还是尚未准入；最后makespan长尾也可能来自尚未准入请求，而非此次tail victim。即使某候选可降低victim合法剩余上界，也不能由此断言总耗时会变短。

若所有候选进展/合法上界/R/页量近似相同，或唯一其它容量可行者恰可能最早释放容量，记录“不支持改victim”。没有校准的重算/传输成本时，不按R、token差或SM数直接换毫秒打分。当前快照不采物理段数，不能选择所谓“复制最连续”的victim；不为此追加本轮模块字段/套件。

后续如确有明显不同的候选，也只得到值得root另行评估的单项机制，不是策略收益。真正改变抢占会改变batch/request采样行与全局随机数分配，必须有新的精度和复现门；不能继承已有accuracy。旧growth/full-output reserve负结果、terminal无机会与当前两个KV协议的正确性边界继续保留。

## 一手资料的用途

[PagedAttention原论文§4.5、§7.3](https://arxiv.org/html/2309.06180v1)说明原FCFS/最新先抢占的公平目标，以及小块传输提交与重算的权衡。它提供判断维度，不提供本实例victim评分；论文上的块大小和吞吐结论不移植到16SM/GQA2、42独立storage/6CPU。当前block size16及原参数不改。

本标准不重复已有TRAIL/CacheOPT/固定budget节奏研究，不训练预测器，也不要求新的硬件扫描。先等一次实际CPU快照，对上述问题给有证据或明确未观测的回答即可。

## 当前产物状态

元数据说明 `source/preemption-snapshot/interpretation-schema.json` 最初只有单位、条件算式与判读字段；不是新测试或模拟器。230548原件到齐后已经追加实际专项记录引用和观测状态，原条件算式不冒称本轮实测。runtime `c6b3baa96db494e7c22d8c7a3f02980d06d3469c491bf850e9ebac77675204f6`、builder `ce4e9773900316c1c19c70acc2dfba5822da08bbdc9e32fa5945b76ab3a666ac`、launcher `6ec5d60bf606b8f6c9cee19a1dbce52517b086c65a4d89ad58bf55b37da10812` 在230548实际部署；原d38等及旧合同保留为未部署历史。

`late-arm-check.json`（c6aedb167f70860e89776ab8c0ac56cbf88fe798adb98bc8c3a11bd51810cf1c）保留Core110 general早于137 scheduler类选择的源码依据、唯一合同014a的1test/0.058s及中途fixture self阴影失败。没有重跑旧suite；这些CPU回执不证明actual snapshot/整copy/launcher通过。

作者后验入口 `scripts/review_preemption_snapshot_run.py` 最终 `6eb45eceb46405e448e1388940c238e6f1c008123e5566b158910ed4e05bdcf0` 已由本owner只读终审，不执行其完整门。它复用2071通用long原件函数只将source数改413、不调用KV门；逐row复算queued/R/cap/单引用页/derived需求，保policy_selected=None。首稿e0ea的替代列表可含failed自身，已最小排除并注明保留failed继续的容量前提；同Engine四事件次序亦收紧，旧稿保留。真实原件到齐后由framework运行唯一全门，本owner只做硬件/请求专项解读。

230548实际为31条running，KV521936token/32621池槽，不是上表较早pair的32615槽。此次ref1非null唯一页计数合计32620，加null槽1恰等32621且free0；输出327..569，不能把32条条件例的154块缺口套到本轮。详见[独立JSON](source/preemption-snapshot/230548-hardware-request-review.json)。
