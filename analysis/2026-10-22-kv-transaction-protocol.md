# 有界单victim KV保存/恢复协议：实际接口与调用顺序

2026-10-22，systems_innovation负责Core/scheduler及CPU事务，framework_innovation负责独立worker，hardware_innovation互审；root唯一GPU owner。root已启动隔离 `20261021T200957Z-kv-protocol-context16k-long`（runner215427，实际目录以root CURRENT/原manifest为准），原long负载+VERIFY1，模型启动中；**尚无协议激活/完成/收益结果**。191545只证明构造normal/packed复制门，195012才观察真实normal42；不能把前者性能当后者收益。

## 实际证据与范围

195012 `kv-descriptors`：EngineCore、UniProcExecutor、WorkerWrapperBase、WorkerFL、ModelRunnerFL同PID213942；AsyncScheduler/queue2；42 unique storage，全部BF16 cuda0、shape `[32621,2,16,2,128]`、stride `[8192,4096,256,128,1]`、offset0、cross observed_none。current stream未观察，因此首版worker SAVE使用device-wide fence覆盖全部旧writer，不假当前流足够。20GiB cgroup的worker/core时点约4.37/4.64GB不是峰值/未来OOM保证。

固定源码：scheduler df780761…、Core27b23827…、KVmanager2e91e77…、coordinator9dd0a647…、single-manager22e3677…、e155 runner；184108原13源。194147补实际serial_utils d75c17a0…、worker_base7da44338…，完整包SHA d9124df09054f0f7cbebff0e15e5e560d83d075ed1c2160ad45e80f09ab4de48。UniProc4625:79/92调用run_method；actual serial486–510的callable收到wrapper，显式unwrap `wrapper.__dict__['worker']`，不是把Core tensor跨进程序列化。仅支持已观测UniProc同进程，mp/PP/多卡/其他布局回原路。

**重要纠正**：实际kvinterface7e3c:903 `needs_kv_cache_zeroing`返回has_mamba；MiniCPM FullAttention为False。22e:270/303仍把FullAttention新页append到new_block_ids，但df780:1046只True才take。因此该list是未drain历史，可含已经free/复用的ID，不是待zero集合。早期草稿错误硬要求True、禁止before与新页交叠，已按root/framework反证修正：scope明确False；仅验证after=原before+本次分配尾段，允许历史重复；另用实际req_to_blocks/ref_cnt1/unhashed/页数证明所有权。**全程不take/drain、不改历史list，worker只显式zero本事务目的页。** 不把原Mamba机制或可能noop的e155 `_zero_block_ids`冒充FullAttention安全保证。

## 代码与当前身份

- `patches/framework/biv150_kv_protocol.py`：**50375e899acbdcee15d3cdec2ecd77875fb355c56ccbfa663271509982ddc19a**。默认installFalse，exact e043 init末尾append general-hook；复用a4de completion-probe的pure `_scope`，不调用其install；a4de本身逐SHA锁定。installed scheduler/Core文件一字不写，只在内存从exact df780 schedule方法插入一条waiting调用，逐byte逆回和compile已核。
- `patches/framework/biv150_kv_transaction.py`：**616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13**，独立stdlib CPU接口，无框架/设备/allocator/RPC/采样。
- framework worker `patches/framework/biv150_kv_worker.py`：**31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf**；调用方才启用，复用c95f raw copy，实际normal42/source guards、device fence、显式zero/Event ACK及单slot。worker由作者与hardware终审；不在此重复其GPU门。
- 包装还须带a4de scope helper和c95f copy模块。root独占prepare/launcher，不重复写包装或改原driver/benchmark/serve参数。

hardware已全文审adapter592d与txn616无最短诊断阻断。当前5037仅把reserve_full_isl硬True改为接受实际bool，原值传回原allocator；协议不依赖True，且未发布前可回滚。hardware已将5037逆换该唯一行精确重建592d，最终定向终审无新增阻断；不能拿CPU审阅称服务安全已证。

## 最小事务与worker命令

Key=(engine session, request ID, incarnation, preemption attempt)，持强引用校验同一个实际Request对象；slot操作serial在整个HostSlot生命周期单调，即使调用方误复用Key也拒旧ACK。新HostSlot必须新session或保留serial，不能复位后沿用旧key。只有一个victim，payload上限1GiB；R根据实际请求与页数决定，超cap就原抢占重算，不把16K构造写死。全层每token43008B，每16token页688128B；最大1560页/24960token，1GiB不是预填数据量。

`plan_snapshot`：R=floor16(min(issued_tokens−全部已排队frame的该req scheduled_tokens, len(已知all_token_ids)−1))。保留至少一个token重取logits；不用placeholder数量代替输入KV跨度，不保存未知/部分页。只复制前R/16个真实物理页及token前缀digest。worker在SAVE前后核actual cgroup可用量，另保1GiB headroom；lazy pinned单victim预算和诊断1layer缓冲明确计数，不为全GPU池做20GiB以上host镜像，显式配额也不是整个host峰值。

唯一RPC `worker.rpc(wrapper, command)`，经 `executor.collective_rpc(..., single_value=True)`同步直调。command是元数据，不含tensor：key、operation_serial、kind(SAVE/ZERO/RESTORE/DROP)、prefix_tokens、pages、nbytes。SAVE pages为源，ZERO/RESTORE为新目的完整页，nbytes=R×43008；DROP pages=[]/nbytes0。reply回显命令，包含真正completed/successful/processed bytes、worker_pid、host_held、error，以及验证/copy次数/内存字段。完整稀疏RPC_ACK JSON落服务日志，异常completion_unobserved后失败退出；不只丢成CPU Receipt。

CPU Transaction要求 SAVE_DONE后才source-free许可；原free实际返回才source_free_committed。旧frames原处理后逐一frame_processed。新私有页ALLOCATED→ZERO_DONE→RESTORE_DONE仍可rollback；publish才转原scheduler所有权，之后不能私有rollback或假回原重算。取消/失败未settle不能free/drop/reuse host；settled失败后先原/私有实际free成功再确认、最后DROP/close。CPU状态和worker返回布尔本身不证明设备完成，必须来自真实fence/Event。

## 精确实际调用顺序

1. general-plugin安装于Core构造前；Core.step_with_batch_queue wrapper只设置ContextVar，首step验证真实类型、原source与scope并记录FIRST_CHECKED。普通无抢占步不运行任何copy/fence。实际runner存在后才包e155 `_update_states`，不在general import阶段提前导入runner造成环。
2. df780 schedule523运行请求分配失败后仍由原FCFS选择victim并pop running；包 `_preempt_request`1116 **原free前**读取group0真实页、queued `(future, SchedulerOutput, exec_future)`中该req的scheduled token跨度，创建单victim计划与预算。scope/长度/预算不适用则原preempt恰好一次，无GPU副作用。
3. SAVE RPC先覆盖所有旧GPU writer的device fence，再按实际normal42页run D2H，Event完成后ACK。只有这一步真实settle后才执行原 `_preempt_request`：原free、statusPREEMPTED、computed0、waiting.prepend都保持。save失败且已settle可原重算；无法settle则fail closed，不把已pop的request继续执行成半状态。
4. **不在schedule内重入future.result/update_from_output**。原Core590–607按FIFO消费，原scheduler.update_from_output成功后才标相关旧frame processed；原AsyncScheduler会对PREEMPTED返回输出正常更新placeholder、跳cache。EOS/取消/同ID新Request导致旧victim不再live时，settle后DROP；不写async_tokens_to_discard，不重复/伪造采样。
5. 恢复只在df780 waiting672、RUNNING分配已完成、原computed==0分支之前处理同一victim对象。旧frames/placeholder未清、非PREEMPTED/epoch变、预算0或prefix digest变则DROP副本并继续原重算，**不park、不跳过队头、不改FCFS顺序**。
6. 在原等待准入约束下 `allocate_slots(request,0,num_external_computed_tokens=R,delay_cache_blocks=True,num_lookahead_tokens=0,full_sequence_must_fit=原bool,has_scheduled_reqs=原runningbool)`，仅分配R私有prefix页，不混入suffix。actual manager340允许0new+正external，这是内部记账复用；实际新复制实现是本补丁，不开启现成connector/serve选项。失败直接原重算；成功核单group、每页ref1/非null/unhashed、实际页数与本次append尾段。历史list完全不变，不误清其他请求或历史页。
7. worker显式normal42目的页zero_→真ACK，然后host H2D restore→真ACK。此时只把request.computed临时置R，Transaction仍RESTORE_DONE；原waiting计算后续num_new并走原allocate。若allocation失败、未形成work或schedule异常，未publish的私有页实际free后确认rollback，computed回原0，host DROP；不让已恢复R成为无工作时永久占池。无法判断的原异常保留失败，不吞成性能成功。
8. 原schedule返回有效新output后，确认target RUNNING、原NewRequestData.computed=R、完整block前缀仍为所恢复页、至少一个scheduled token。**只改这个新建output**：target从scheduled_new_reqs移除；加入cached.req_ids/resumed_req_ids、完整替换block_ids、num_computed_tokens=R、原FIFO已确认output_count、复制all_token_ids，清cached output-count映射cache。普通V2 payload及任何旧queued SchedulerOutput不改。
9. 这一步必要：df780:1013 V2把resumed当New；e155:1615已有CachedState的streaming分支会清output_token_ids（但其generator对象本身仍保留，不能误称必然重建）。专用cached-resume让e155:1437替换fullblocks，1448按all_token_ids恢复输出；df780:1259在V2原本不填该dict，**必须由本适配器补齐**，否则KeyError。只有全部新payload合法才不可逆publish，再DROP/close释放host预算。发布后任何异常失败退出，不伪装fallback。
10. e155原 `_update_states`返回后稀疏核同CachedState/同generator对象、输出tokens、computedR、完整block替换与CPUcomputedR，记录RUNNER_RESUME_STATE_CHECKED(beforeAttention)。原future真实返回并原update成功后记录RESUME_OUTPUT_PROCESSED。前者是状态证据非GPU完成；后者沿原D2H ready事件消费，不新增采样/同步，不声称完整模型accuracy。

## 最短门与禁止外推

root准备隔离新source+原bc51 long16K/1024/32req/c64/seed721201。首门开 `BIV150_KV_VERIFY_RESTORE=1` 仅作协议诊断：首个成功restore额外逐层D2H复用一层pinned缓冲，与SAVE host全byte相等；验证回读字节/事件/内存通过完整RPC_ACK保留。这一轮含验证开销，不计性能收益。至少需真实SAVE_ACK_FREE→旧frame处理→ZERO/RESTORE complete并verification_passed→RESUME_PUBLISHED→RUNNER_RESUME_STATE_CHECKED→RESUME_OUTPUT_PROCESSED，32/0/tokens、源/DB/KV/清理齐全；只有INSTALLED/FIRST_CHECKED不算激活。

实际库容量/物理32GiB/CPU配额/DB/并行host条件照原要求明示；verified诊断后才考虑不回读的同参数性能短对照，无最低收益淘汰线。token RNG不新增调用/不重置generator，但少做prefill会改变全局采样批次时序和数值路径，**不能承诺与旧随机输出逐token相同**，后继仍须独立准确率和复现门。

现有CPU证据 `analysis/source/kv-transaction/cpu-check.json`、`adapter-cpu-check.json`：一项事务合同覆盖ack/epoch/旧frame/zero/取消/回滚、按真实反例补守卫后必要复跑；一项adapter合同使用actual f281输出DTO验证V2完整字段/all_token_ids/cache-property/publish-close、exact waiting插入逐byte逆回+compile、e043 exactappend、defaultFalse，无torch/numpy/vllm导入。**不是GPU协议证明**。registry不新增伪设备结果，现93行/queue69仍是此前已完成证据。

当前官网 [offload worker接口](https://docs.vllm.ai/en/stable/api/vllm/v1/kv_offload/base/)也区分提交、完成查询与等待，这仅支持接口边界的设计参考；它是较新文档，不能代替本机0.24源码，不引入现成connector/新框架分支。191545约120–235ms构造copywall与181041的13758token exposure均不能直接换算服务净收益。
