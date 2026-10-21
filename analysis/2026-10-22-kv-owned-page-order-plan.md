# 私有恢复页映射升序化：真实页图与唯一后继候选

范围仅为天数 BI-V150 16SM/32GiB 本实例、MiniCPM5-2B BF16、单组 normal42。本文是 CPU 原件分析与设计，未改 runtime、未执行新设备工作；不能外推 C500。root 已选择唯一候选：**allocator 原样选完页后，只在尚未绑定/发布的私有页列表上改变逻辑到物理映射次序**。不混前缀截断、暂态早退、请求排序、块大小或其它策略。

## 202526真实恢复已经发生

原件 `experiments/framework/20261021T202526Z-kv-retain-context16k-long{,-control}`；root归档包 SHA `430d2f7c211d2f52211e05cc29dca8505e840a3f6b1ec930c6410dca3a5f6c73`。本 owner 专项只读 control 的 worker31cc/protocola1b691/transaction616/copyc95f，实际SHA全符；不代重复完整 official/DB/source验收。

独立计算 [JSON](source/kv-transaction/202526-restore-page-order-review.json) SHA `ce5328d89cb161bcc70f2a769e73dbcb7a97e7486bced22d57254058bc3eb0d0` 保存原日志 SHA `7ace8be07da9ade2eba898507c345c2161173fd711b975c9ead4943f1103dd55`、页序hash、步差直方图及两种66段列表。原SAVE16704token/1044页/718405632B、1008calls；首次 RESTORE_DEFERRED 明确 allocation_none/free1030/placeholder0/pending0、full_sequence_must_fit=True，最后restore_skips454。只首个暂态有reason，不能把454次全断言为同一分支或用free单值重建全部allocator条件。

ZERO、RESTORE 的1044目的页逐项相同且正数/唯一。ZERO43848次、RESTORE43848次；全42层回读718405632B、43848次，verification_performed/passed=True，completed/successful=True。随后6个 runner状态检查均True，原输出消费8个scheduled token。它证明本次真实保存/恢复/回读/消费链路成立，不是准确率门。服务32/0、240.929935357秒仅诊断；root回执DB由516/19270变为518/19337，不能与旧DB运行作性能比较，也不能把总耗时分解成43k调用的成本。

## 真正的页序：大量连续区间被反向枚举

| 对同一1044页集合的CPU计算 | 正向相邻差+1的段数 | 42层可合段调用数 |
|---|---:|---:|
| 实际原逻辑序 | 1044 | 43848（与实际ACK一致） |
| 原序整体反转 | 66 | 2772（仅几何假设） |
| 按物理页号升序 | 66 | 2772（唯一候选映射） |

原序中978个相邻步差为−1，故其反向连续段为66；当前 c95f 只合并源/目的同时正向连续的 `.narrow.copy_`，host行又按逻辑次序正向，所以这些−1不能直接合并。不是“物理页全不连续”，更不能从43848这个调用数单独猜布局。

同一集合排序后的三大区间是237..1027（791页）、30959..30995（37页）、31000..31152（153页），其余63个独立页；总66个物理连通段。这也是在不换选中集合、只重新排列其映射时正向连续段数的下界；升序达到该下界。不能宣称可以变成一个连续段。整体反转也达到66，仅作证据，不另加第二变体。

调用数的几何上限是每阶段43848→2772，少41076次、93.67816%。字节仍为685.125MiB，SAVE原映射/1008calls不动；ZERO写量、H2D量、诊断D2H量不减少。这里是 Python 记录的操作提交计数，不冒称已采GPU实际launch/DMA引擎轨迹，亦不换算成毫秒或吞吐收益。

## actual源码允许的最小切口

以下代码均为取回 actual 源，不是公网最新版假设：

| 源/切口 | 事实与限制 |
|---|---|
| single manager22e，205–234、265–276 | 空local hits先把num_cached_block置0；external页由原block_pool选定后extend进真实req_to_blocks |
| pool3fc5，542–571 | get_new_blocks原样popleft_n并处理这批既有cache eviction、refcount；候选不能修改这一步或另挑页 |
| manager2e91，580–586 | get_blocks通过coordinator取得block对象，get_block_ids另建Python ID列表 |
| coordinator9dd0，346–353 | 返回single.req_to_blocks[rid]的实际list引用，不是block对象拷贝 |
| single manager22e，353、397–410 | cache_blocks以后按该逻辑list给pool赋逻辑hash；free按其reverse归还，未来顺序会受映射变化影响 |
| 当前a1b protocol _try_restore | external R/delay_cache_blocks分配后，先审private ownership，再导destination、tailproof、bind、ZERO/RESTORE；这是唯一可插入位置 |

[PagedAttention原论文第4.2–4.3节](https://arxiv.org/html/2309.06180v1#S4.SS2)解释逻辑页与物理页通过block table分离，逻辑相邻不要求物理相邻。这里只用其映射原理；具体可修改边界仍由上表actual实现和本项目事务约束决定，不照搬早期scheduler。

## 交给systems的实现/审查约束

1. 只在原allocator成功以后、`tx.bind_private_allocation`/ZERO之前执行一次；tx仍HOST_RESIDENT、未绑定目的页、无pending frame，未把新映射放进任何旧/新已dispatch输出。不能对后继普通append、已经有KV值或已发布的表反复sort。
2. 实际 `owned[0]` 必须是 `single.req_to_blocks[rid]` 同一个普通list，长度恰R/16；num_cached_block[rid]为0，所有对象非null、ref1、unhashed，block ID唯一且是同一实际分配集合。排序前后block对象身份集合和ID集合都守恒，不只比数值长度。未知alias/共享/已hash/不完整所有权就保原映射。
3. 对这份真实list原地升序（不能只改临时ID tuple，或换list对象让旧引用看不到变化）。allocator已选页、当前evict集合、refcount、hash/池freequeue不动。历史 `new_block_ids` 完全不改，其本次尾段证明只比较相同集合仍有效。
4. 排序后才重新导出destination，供同一tx、ZERO、H2D、诊断D2H、原get_blocks与后继cached-resume payload全部使用。host行i仍是逻辑第i页的原KV，不排序token或host内容；把它写到新destination[i]，并让block table第i项也是该页，才保持逻辑语义。
5. 原ZERO/RESTORE/回读worker31cc与copyc95f不用改。因为物理destination现在正向连续，同一既有make_plan自然对66段提交；仅把copy调用“按页号排序执行”而不改逻辑映射并不能让原host正向行可合并，不能冒充等价实现。
6. 所有当前完成ACK、1GiB payload/guard、epoch/取消/未settle强引用、原后继分配、发布前回滚、cached-state/generator保留约束不放宽。没有新增GPU staging/packing或采样调用，也不更改R或请求FCFS。

ZERO只写集合，本身可单独排序物理清零区间且不改逻辑映射，风险更低；但会留下RESTORE/回读43848次。root本轮选择的是上述**唯一protocol映射改动**，不另加ZERO变体或worker分叉。

## 必须显式承认的未来free影响

本次popleft_n和evict已在排序前完成，选中对象集合/本次eviction集合保持原封不动。但single manager原free调用 `reversed(req_to_blocks)`，pool3fc5的free_blocks614+按传入优先序把unhashed页prepend、hashed页append；映射改变会改变以后归还物理页的次序。因此不能同时承诺未来freequeue、物理allocator轨迹或将来的eviction集合逐步完全一致。逻辑token顺序仍不变，当前实现不会新增请求重排或挑选策略；这些未来影响必须在新真实门和最终准确率中接受验证，不通过额外free hook偷偷修回另一行为。

若未来要求连物理freequeue顺序都逐步不变，则这个重映射方案不满足该更强约束；不能在报告里隐去。当前只保证同次选中集合/本次evict集合，以及每逻辑页内容与其新表项对应。

## 最短验证与收益反证

systems按root要求保留a1b受测字节，做一项必要CPU合同：真实list别名/对象集/IDs/num_cached0/guard回退、原hist未变、destination与后继表一致，单改源码身份可审。不能用fake event证明GPU正确。

root随后只排隔离新源、同真实长输出恢复门+VERIFY1：真正看到本次分配页集合守恒、新映射实际进入命令与runner表、ZERO/RESTORE/全字节回读、6个runner检查和后继原输出消费。新run页图可能不同，应记录它自己的原序/新序runs/calls，不能硬断言仍是66段。CPU/shape开销与DB新行要各自保存，诊断elapsed不冒称匹配性能。

减少提交可能受producer同步、固定pin/验证、CPU节流及真实DMA成本掩盖；保持bytes不变也不保证延迟下降。只有正确链路通过且两端DB/容量/参数/并发条件匹配，才另作必要性能比较；之后独立accuracy。当前仅设计及原件统计，无运行代码改动、无新GPU/SSH操作。

## 后续owner实现与0e2115独立终审（覆盖上文实现状态）

systems已按root授权单独实现此候选；本 owner 没有编辑运行代码。最终 `patches/framework/biv150_kv_protocol.py` SHA `0e2115d0fbdedea64d1b911c0d6ae3b359f178004d844a8dd8088dfa4388fb86`。受测a1b原字节在 `analysis/source/kv-transaction/biv150_kv_protocol.a1b691.py`，SHA精确 `a1b691f52f3724b95bbcb11f5702611a17103161001bb929096c71ab4fa74751`；本人内存删除唯一 `_order_private_pages` helper及唯一bind前call后，SHA逐字节精确回该a1b，没有其它算法增量。实际worker31cc、transaction616、copyc95f与footer均未变。

helper检查owned一组、真实普通list与req_to_blocks同对象、num_cached0、HOST_RESIDENT、无pending/目的绑定/inflight/cancel/closed、source已实际释放、长度与R/16相同、非null/ref1/unhashed/正整数唯一页号和唯一block对象。任何新guard不匹配返回False、保持原映射。通过才原地sort；随后断言list身份、block对象集、精确升序页号，才返回原控制流导出destination。历史list不修改，fresh helper容许同集合异序，ZERO/RESTORE/readback/cached-resume均接同一新目的序。

PRIVATE_PAGES_ORDERED只记录CPU前后段数/身份守恒，明确host逻辑内容未变与未来free次序可能改变，不冒充GPU传输或因果性能。已有其它私有所有权原guard不放宽，原defer454相关路径未改，也未混前缀截断设计。

已只读 `tests/test_biv150_kv_private_order.py` SHA `29deff8d51fcf6f7f7811aacc84a3ac6f9d431c3e08879a80b39206d178522b5` 及owner `private-order-cpu-check.json`：唯一一项CPU合同1test/0.001s，通过真实事务命令构造、host逻辑行/新表一致、guard拒绝保序等；本 owner 未重跑。owner首次逆向校验的LF计数错误保留说明，修检查脚本后确认精确，runtime无额外delta。独立定向终审未见阻断同真实VERIFY门的问题，回执已给root/systems；截至此回执尚无该排序版设备结果，不能把CPU4页合同或旧run66段当新设备证据。

## 204159真实页序门专项验收：调用减少成立，吞吐未判

完整 `20261021T204159Z-kv-page-order-context16k-long{,-control}` 已到本地，root归档包 SHA `588886979857dc1eab16dcfa8ed8b8a76751741f3b21825cfa62fa8219872336`。本人独立读实际control四件，确为0e2115/31cc/616/c95f；新专项 [JSON](source/kv-transaction/204159-private-order-hardware-review.json) SHA `0cafbe28c8200dae37ee5bd5edff66e3f7e2391837b5bb2b83f884e98a34020f` 保server.log SHA `5c3932d221738ab1466cc7a1de6b3ab112e6138e4a64b532ea23c8e896054eeb`、实际全66段和ACK/consumer原行号。framework负责完整source/DB/postflight验收，本节不重复该工作。

实际 PRIVATE_PAGES_ORDERED：1044页、R16704、before1044/after66、同list/同block对象/同ID、host逻辑未变；真实 ZERO 与 RESTORE 命令的1044页逐项相同、正数唯一且升序，独立重算恰66段，仍是791/37/153三大段加63单页。同次完整排序前页数组没有单独输出；守恒依据是已核0e源码postassert与真实marker，不能说从同次两份完整数组独立比对得出。

SAVE仍1008calls；ZERO2772、RESTORE2772、42层诊断回读2772，均与42×66相等。实际submitted/transferred/readback718405632B，verify_performed/passed=True，真实done ACK成功；后继6个runner检查全True，原8个scheduled token输出消费，DROP成功且hostheld=False。故“通过私有页映射消除反向枚举造成的提交碎片”已获真实命中/全字节/消费证据；无额外GPU staging或新算子。

服务32/0、227.54834548803046秒、2448.0775670122475TPS只是VERIFY1诊断。root回执本轮DB518/19337三SHA不变；旧202526从516/19270扩展后才到该DB，且两轮都含首次诊断/回读，不能将两个elapsed相减报收益。本轮没有独立阶段wall/event；93.67816%是提交次数减少，绝不是TPS提升或DMA时间比例。全模型accuracy仍未测，不继承稳定SQL+C3成绩。root后继匹配wrapper另审，当前冻结四件不改。
