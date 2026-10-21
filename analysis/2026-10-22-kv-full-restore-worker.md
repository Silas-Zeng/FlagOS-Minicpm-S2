# RESTORE_FULL独立worker候选：完整覆盖、真ACK与失败生命周期

范围仅天数BI-V150/本项目MiniCPM5-2B BF16 normal42，CPU本地实现准备；不改服务参数、模型或当前受测文件，不外推C500。root当前唯一GPU为capacity `20261021T212106Z-kv-capacity-context16k-long` / runner224783。本文候选尚无设备结果、不继承accuracy或性能。

root授权从冻结31cc复制到 [`patches/framework/candidates/biv150_kv_full_restore_worker.py`](../patches/framework/candidates/biv150_kv_full_restore_worker.py)，首稿SHA **5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477**。原 `biv150_kv_worker.py` 仍 **31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf**；canonical0e、capacity67e4、616事务、c95f copy和当前包装不变。最终安装需由新source builder把副本映射到新隔离的canonical worker模块名；没有默认install或框架top import。

## 协议接口与严格选择

与systems约定原command dict字段不变：key/operation_serial/prefix_tokens/pages/nbytes，新增真 `kind="RESTORE_FULL"`。systems拥有独立事务/protocol；worker只执行设备操作和host资源，不修改Request、调度、computed或RNG。

SAVE自己的D2H/event完成后，候选ACK才新增描述符 `full_restore_supported=True`、`saved_layers=42`、`saved_page_bytes=16384`、`saved_prefix_pages=R//16`、`saved_bytes=nbytes`。它描述保存端能力，**不宣称目的覆盖已经完成**。Core在原private完整分配/bind后核这些字段，再选择FULL；没有descriptor或提交前资格不足仍走原ZERO/RESTORE。FULL一旦提交，失败不能回旧路重试半写页。

新事务只能从ALLOCATED提交真实RESTORE_FULL；真实成功Receipt后才能RESTORE_DONE。禁止构造不存在的ZERO_ACK或直接改ZERO_DONE。目的物理页仍由Core证明ref1/unhashed/私有且未发布，worker再独立证明写入范围/布局，不把客户端bool当完整覆盖证明。

## SAVED入口完整覆盖与绑定

原ZERO曾负责绑定destination；新入口显式迁移该职责。slot必须同key/owner/nbytes/storage签名、SAVED/settled、此前无destination。`_full_restore_plan(torch,policy,slot,raw,pool,packet)`在接受新操作/任何copy前只读元数据：

- command保持完整16token页/非null唯一目的页/pool边界/1GiB上限。
- host恰42个普通Tensor，各为pinned CPU uint8、shape `(R//16,16384)`、连续/offset0，storage恰完整范围，层间storage唯一。
- `_context`继续核normal42 BF16池的实际形状、stride、storage大小/独立性及模型/worker源身份；raw view恰42个cuda:0 uint8完整页Tensor，offset0、连续。
- 冻结c95f `make_plan(range(R//16),pages,...)`逐页一一对应，plan逻辑页数和run总页数恰R//16。因此成功写入为全42层、每目的整页有且仅有一次对应host内容，不靠“旧页本来为零”或后继writer补写。

验证通过后，slot强持有目的tuple和plan，phase为RESTORE_FULL_BOUND；原raw/host引用仍保留。**然后保留RESTORE自己的 `torch.cuda.synchronize()`**，覆盖目的页旧writer，再原c95f H2D、真实Event record/synchronize；VERIFY1仍按原单layer pinned buffer逐层回读/CPU byteequal，全部通过才成功ACK。旧ZERO/RESTORE分支仍原状态机，没有删其数学或调用。

成功FULL ACK明确 `zero_stage_executed=False`、`zero_calls=0`、`destination_bound=True`、`full_coverage=True`、`full_coverage_bytes=nbytes`；copy/event/可选回读计数沿原值。没有发ZERO操作，不把零工作记成已传输。

## 失败、取消和资源

预校验拒绝不改变已有正常slot；接受绑定之后任何错误仍按原逻辑FAILED，尝试真实device settle。不能settle时保持raw/host/event/map强引用、completedFalse，Core不能free/DROP/publish。已settle的失败也不能publish，交原未发布private回滚/释放；已发布后不能用私有回滚接口。

异key/epoch/owner/storage/serial、部分层/partial-byte/未知layout/alias、R外tail均不属于FULL覆盖资格。新的操作不会清零整个pool、改变历史new_block_ids或其它请求页。host预算/1GiB额外guard/诊断buf预算、源snapshot不变及原FIFO/RNG边界保留。只有最终accuracy能检验端到端输出分布，字节相同不足以自动继承103/105。

## 当前验证与下一条操作

首稿仅compile语法通过；hardware全文只读初审未见完整覆盖/同步阻断，确认绑定发生在真实SAVED入口、原fence仍在、失败不降级，未跑suite/GPU。systems将准备**双方合并的一项CPU合同**，本owner不再另铺worker模拟suite。合同只证command/状态/描述符/完整性元数据、真Receipt和失败引用逻辑，不能声称模拟的event验证CoreX。

等联合合同/最终pins后双方定向终审，由root准备独立source；最短真实门需见SAVE descriptor、RESTORE_FULL真实命中、没有ZERO、42层整byte回读/runner六检查/原consumer和退出后态。当前capacity门优先、设备owner不变，不插入第二任务。只有通过新门后再考虑VERIFY0必要比较，不借理论字节量承诺收益。

## 三件最终定向审阅与唯一联合合同

本owner已实际逐SHA核对最终三个独立文件，worker首稿后无字节变化：

| 候选副本 | SHA256 |
|---|---|
| biv150_kv_full_restore_worker.py | 5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477 |
| biv150_kv_full_restore_transaction.py | 84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883 |
| biv150_kv_full_restore_protocol.py | 1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8 |

systems事务只加 `submit_restore_full()` 从ALLOCATED提交真实操作，成功ACK将该kind正规转换为RESTORE_DONE；旧ZERO路径和取消/回滚/publish保持。协议只在SAVE echo/完成/workerPID验证后保存五caps，原private bind之后再核同R/bytes/42/16384、真实owned list/numcached0/ref1/unhashed、ALLOCATED无pending/未取消等，才选FULL；缺caps在提交前回旧ZERO/RESTORE。FULL成功ACK额外强核未执行ZERO、目的绑定和完整字节覆盖字段，缺证据则保inflight失败关闭，不free/publish，不伪构造Receipt；实际失败且已settled才原回滚，没有FULL提交后降级。

唯一双方联合合同 [`tests/test_biv150_kv_full_restore.py`](../tests/test_biv150_kv_full_restore.py) **0035b97f5331083001409871165a66e364c3c1a8f956182e2080d53520e65a54**，作者实跑1test/0.002s通过，记录 [`full-restore-cpu-check.json`](source/kv-transaction/full-restore-cpu-check.json)。本owner完整只读代码/结果/三件diff，未重复运行：真实 `_command`/`_full_restore_plan`/c95f plan验证42层描述符与重复/少层/alias/预绑定拒绝；真实adapter/事务经CPU RPC ACK stub验证FULL、缺caps旧ZERO、缺proof/未settle保inflight、settled失败原free/DROP、cancel等ACK后回滚。**它没有执行worker.rpc设备分支、copy或Event，不证明CoreX完成/字节正确。** 这些依赖源码互审和下一root真实门，不能从stub推出。

framework侧终审未见进入最短独立VERIFY1门的阻断，已回root/systems/hardware；候选三件冻结等待hardware最终回执/独立builder，不能直接从candidates子包安装。canonical0e/67e4/31cc/616/c95与当前受测包装原样。capacity212106在另外的67e4/31cc链上已真实通过fast462/字节/consumer，仅作该前置证据，不替新FULL设备门。

## FULL214400真实设备门与worker核心独立核对

root封存 `20261021T214400Z-kv-full-restore-context16k-long{,-control}` 后，systems实际运行已审2071全体验收，结果 `analysis/source/kv-transaction/214400-independent-review.json` SHA **aa16dc31f430230db6c1c0ed69f55b88b3d036b3822bf59e2b9a8ddd9d97ea45**。完整416源/系统/DB/原负载/退出由其与root验，不由本owner重复整套审计。

本owner另外只运行 [`review_full_restore_worker_ack.py`](source/kv-worker/review_full_restore_worker_ack.py) 核四个核心源文件/真实worker ACK/字节/consumer，结果 [`full-restore-214400-worker-core-review.json`](source/kv-worker/full-restore-214400-worker-core-review.json)；没有重跑COPY、CPU合同或设备。该小审从实际command计算R/页数/run，确认真 **SAVE→RESTORE_FULL→DROP serial1/2/3**，没有ZERO/旧RESTORE。实际R16704/1044页/718405632B，SAVE24段1008calls；FULL66段2772calls，zero_stage_executed=False/zero_calls0、destination_bound/full_coverage True且全nbytes。SAVE五caps实际齐备，H2D与42层718405632B整字节回读通过、回读2772calls；host在copy中持有、DROP后释放，runner六项全真、原consumer8tokens、fast454。

无ZERO由真实命令/ACK与固定5d9a分支对应，不冒称额外profiling测得零内核。六检查仍在Attention前，原consumer另证；单次FULL成功不覆盖所有取消、多victim或完整accuracy。32/0；本run **226.79482778999954s仍是VERIFY1诊断，不算收益**。系统全审实际KV521936、DB519/19340三SHA前后同897/29d/71ac、21:49:38.171431Z68/0/双栈闭/无GPU；shutdown ERROR/WARN原样保留，测前ERROR空。本owner没有把它与不同KV/回读的旧pair作性能对照，也未更改运行资产。
