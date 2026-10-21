# KV事务CPU独立审阅：V2恢复、FIFO与fresh zero边界

framework_innovation，2026-10-22。仅读systems的`patches/framework/biv150_kv_transaction.py`与实际df780/27b/e155/22e/2e91源码，不修改作者文件、不运行其测试或GPU。首读aeea9ff、后读新增rollback_unpublished的fae49192版本；作者仍在接入，以下是挂点约束，不将纯CPU事务称为完整服务协议。

事务本身只产生Operation与消费外部Receipt；pending-frame集合、slot单调serial/epoch、save完成前禁free、zero→restore→publish以及未发布私有页rollback的状态边界合理。Receipt.completed仍须worker真实事件/settle，不能由CPU阶段、future.done或placeholder伪造。当前无安装/框架导入，不能以它已通过合同推断真实resume已正确。

最关键的具体反例与建议已发systems/root：

1. **V2搬到cached列表还不够。** df780约1013把resumed移到NewRequestData并带_all_token_ids。e155已有req会进_update_streaming_request，清output_token_ids并将此前输出当prompt；其已有generator对象仍保留，不能误说必然重建generator，只有requests中无旧state的新分支才创建/seed generator。专用恢复应保留原CachedRequestState及原prompt/output边界；从new移除后成套补resumed_req_ids、完整替换block_ids、computed R、output数量及all_token_ids。**df780 _make_cached_request_data:1259仅在not use_v2时自动补all_token_ids，而e155:1451异步恢复num_output>0会直接索引它；只复用该builder会KeyError。** 必须为本次恢复显式补真实已确认token列表拷贝，不能引用后续会变的Request list。
2. **pending frame必须按实际原输出消费围栏。** Core27b:590 FIFO pop，595取future，603先处理abort，604–607原update_from_output返回之后，才可按snapshot epoch通知frame_processed；不能以device fence或future.ready代替CPU消费。不要修改仍在batch_queue中的SchedulerOutput/new/cached数据或提前消费其中一个请求；req ID复用、取消或原update失败都不能放行恢复。原payload及位置/RNG归属保持。
3. **不要drain其它RUNNING的zero。** 22e.new_block_ids是跨本schedule累计list，原df780在输出末尾整体take。split_fresh_zero_ids(before,after,private_pages)只移除此次独占追加尾段、保before原序是正确方向；同页回收再分配或别名不满足前提须原路。2e91明确num_external>0时num_new_tokens=0合法，可先只分R前缀页，避免原new suffix页混入restore集合。原后续allocation失败必须在publish前rollback私有页和tentative computed；一旦发出工作不可静默回退。
4. **原zero helper可能空操作。** e155 _zero_block_ids只有存在_kv_block_zeroer才调用；plugin WorkerFL未见stock worker的_init_kv_zero_meta流程，不能无检查调用后ACK成功。root已同意worker独立对实际normal42、本次private页的raw uint8 narrow(run).zero_，真实event完成后再restore，不改默认runner/不触其它页。
5. **RNG边界要诚实。** e155 bookkeeping:3703–3709对discard行的非None generator回退offset4；恢复必须保原generator对象/已消费状态，不多调用采样或改行。默认非seeded请求用全局随机流，减少recompute可能减少原丢弃采样，不能从bytewise KV一致推出逐token同基线。worker拷贝不调用RNG；端到端新路径仍需独立accuracy，不继承103/105。

实际195012已独立证实UniProc/WorkerFL/ModelRunnerFL同pid、normal42/42独立storage与queue2，解除“静态类不等实际对象”的缺口。剩余worker传输/真ACK/字节核验和scheduler专用payload仍由双方分工实现，交叉互审后才由root最短实际门验证；不扩大CPU模拟框架。

## 首次实际SAVE→DROP之后：暂态保留revision定向终审

200957实际只完成SAVE/free/DROP，restore_skips=1但无逐guard理由，不能断言是pending或容量；完整负例见 [`first-protocol-review.json`](source/kv-worker/first-protocol-review.json)。本owner提出暂态保留但不park/改变原准入的最小切口，systems实现新协议，root负责新隔离门；worker31cc继续冻结，旧50375完整副本保于`analysis/source/kv-transaction/biv150_kv_protocol.50375.py`，本owner实际核它仍50375e899acbdcee15d3cdec2ecd77875fb355c56ccbfa663271509982ddc19a。

新protocol冻结 **a1b691f52f3724b95bbcb11f5702611a17103161001bb929096c71ab4fa74751**，本owner逐diff只读审阅及最终SHA核对，无新隔离最短诊断阻断；没有执行测试/框架导入/GPU，没改作者文件。worker **31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf**、transaction **616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13**、init791c/footer保持原样。

定向检查结果：pending旧frame、output placeholder、token budget或external allocationNone只保留HOST_RESIDENT，让原waiting/FCFS路径继续，不返回伪调度结果、不提前消费future、不动已queued输出。仅首次defer记录CPU理由/free/prefixpages等描述，明确没有实际required-blocks观测；不把它当完成。原FIFO update成功后才按原围栏解除pending。

_wrap_schedule只在**本次新建**output.num_scheduled_tokens[rid]>0且tx仍HOST_RESIDENT时按`ordinary_recompute_admitted`丢host；status RUNNING本身不够，未发出work的allocNone/原break保留。这个output是dispatch前的准入计划，不能称已forward执行。RESTORE_DONE仍走原commit或未发布rollback，不越过原容量/FCFS来制造恢复事件；没有新增runner状态改动。

request对象/epoch、终止、attempt、status/computed或prefix token失效仍明确discard；Core末原有取消/ID复用清理保留。极端same-id新对象在_try_restore早期直接return后可能被本次按rid的ordinary-work检查释放，安全上不恢复旧host，但日志理由不一定精确到新epoch；本owner已告作者，作为非阻断归因边界保留，不扩本次改动。

唯一新针对性合同 `tests/test_biv150_kv_protocol_defer.py` **b1d8cbb3aece15bbe4bfe395e0586f516be8a839db95199ddc99e95447600254** 已全文读：pending重复仅一次理由/不分配、原FIFO后placeholder仍保留、allocateNone保留、output0即便RUNNING也不drop、原output>0才DROP、identity/attempt/digest/terminal失效释放；无框架/设备。作者报告实际1test/0.002s通过，本owner未重复跑，也未重跑旧COPY/worker门。只能证明CPU分支合同，后继仍须实际ZERO/RESTORE、全字节回读和consumer证据，新门未返回前不报性能或accuracy通过。

## 202526真实验收与后继私有页排序边界

本owner已独立验收202526完整原件，详见 [`retained-protocol-review.json`](source/kv-worker/retained-protocol-review.json)：a1b/31cc/616源码身份、42层718405632B恢复回读、6项runner检查及原输出消费均通过，source/live416与正常退出后态通过；仅一次诊断，不继承整模型accuracy。DB实际516/19270→518/19337，240.93s不能作为性能对照。原200957 SAVE→DROP负例不覆盖或删除。

root授权systems仅实现**分配后、未绑定/未发布的私有目的页逻辑映射升序**。本owner实读2e91/9dd0/22e/3fc5/df780/e155，设计暂无阻断，但必须成套守住：

1. `KVCacheManager.get_blocks:580`→coordinator `get_blocks:346–353` 对非空请求直接返回 `single.req_to_blocks[rid]` 原list；`KVCacheBlocks`只是wrapper。应核 `type(list)`、对象身份和完整Block对象集合，以原地sort保所有合法alias的list身份，不能改 `block_id`、只改RPC页号或拿 `allocate_slots(...0...)` 的返回值当完整owned（该返回常为空new-suffix list）。
2. 原 `add_local_computed_blocks` 在没有local hits时先设置 `num_cached_block[rid]=0`，随后external分配extend真实list；`delay_cache_blocks=True`跳过hash发布。排序只适用于**确认仍HOST、pending0、未bind/ZERO/dispatch、exact整前缀页、唯一且ref1/unhashed/非null、numcached0**的集合。未知既有owned/hashed/shared/local-prefix不应排序。失败应在bind前按真实所有权处理，不能带着已错映射继续publish。
3. `allocate_new_blocks:278–310` 按已有list长度只extend后续suffix，保持新前缀序。`cache_blocks:318–361` 将真实list交 `BlockPool.cache_full_blocks`；3fc5按logical slice与 `request.block_hashes` 同位置绑定，因此必须先按新逻辑序恢复相应host页内容，再允许后续缓存。只有ID集合相同而逻辑内容错序仍是严重错误。
4. df780 V2输出在本次schedule末用 `get_block_ids()` **新建ID list**，原queued旧output并不alias Block list；e155 resumed路径整体替换真实runner表，原state/generator与all_token_ids/count保持。仍须原FIFO消费/pending0，不能据ID拷贝事实跳过旧frame；不改旧runner表或旧payload，不以重新绑定页面为理由改RNG。
5. **FullAttention `new_block_ids` 是历史列表，完全不改、不drain**；早期第3点仅按待清零列表设想的“移尾”已被actual needszero=False证据更正。此次fresh证明仅比较新增尾段/集合，own ZERO只触本次private页。
6. 初始分配/eviction选择集合与FCFS可保持；原 `free(reversed(req_blocks))` 将来会按新逻辑顺序归还物理页，可能改变后续reuse/eviction时序，不能声称未来allocator轨迹完全不变。真实缓存命中/后续append、字节回读和consumer仍需新隔离设备门验证，不以纯排序数学证明替代。

此节只有实际源码阅读/消息回执，没有修改systems协议或worker、没有新测试/GPU。硬件owner独立得出同alias/cache/free边界；等待systems实现最终SHA后定向互审。

### 最终排序实现定向终审

systems最终protocol **0e2115d0fbdedea64d1b911c0d6ae3b359f178004d844a8dd8088dfa4388fb86** 已实核，旧a1b副本SHA吻合。实际diff仅新增 `_order_private_pages` 与owned校验后/bind前一条调用；上述list身份/numcached0/生命周期/完整唯一对象集和ID/ref/hash守卫均实现，原地sort后重导destination，guard外False继续旧unsorted路径。history、454次暂态路径、worker31cc/transaction616/copyc95和init footer不变。未见进入新隔离最短恢复诊断的阻断，已回root/作者。

唯一CPU合同 `tests/test_biv150_kv_private_order.py` **29deff8d51fcf6f7f7811aacc84a3ac6f9d431c3e08879a80b39206d178522b5** 与 `analysis/source/kv-transaction/private-order-cpu-check.json` 已只读全文核对。作者实际1test/0.001s通过，本owner未重跑；真实CPU Transaction接受新映射、host逻辑行与新表对应、旧ID副本/history/对象ID对应不变，错alias/cached/shared/hash/pending/bound/published/duplicate均回旧序。去helper及单call精确逆回a1b的记录保留。这个4页构造不证明真实1044页合为66段，也不证明GPU完成。新run仍须实际marker、全42层回读、runner整表和原consumer，之后才讨论性能/accuracy。
