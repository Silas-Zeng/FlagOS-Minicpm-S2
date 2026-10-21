# 私有KV恢复页排序：只改分配后、发布前的真实映射

## 204159真实服务诊断完成

`experiments/framework/20261021T204159Z-kv-page-order-context16k-long{,-control}` 于20:47:11.313241Z exit0，包 **588886979857dc1eab16dcfa8ed8b8a76751741f3b21825cfa62fa8219872336**。独立416源SHA/0e2115及冻结worker31cc/事务616/c95f、原SERVER/bc51/seed、CPU6/物理32768MiB、原raw32-0同524288in32768out与后态通过。完整12事件见 `analysis/source/kv-transaction/204159-independent-review.json`，没有重新上卡或重复CPU门。

Engine/worker219639真实PRIVATE_PAGES_ORDERED：1044页、同页集合/Block对象/list、host逻辑序不变，run1044→66；完整ZERO/RESTORE命令页ID实际升序、唯一1044，独立相邻检查重算66run，ZERO/RESTORE/诊断回读均42×66=2772次，718405632B全42层byteequal。SAVE仍1008copy；saved/restored/published各1，restore_skips454、rollback0。原FIFO后恢复、publish/drop、runner六项状态及原output8token消费均通过。这里66run/2772现在是**本run实测**，不再仅旧集合推导。

DB前后518表19337行实体/schema/逻辑三SHA一致d9351095…/a5ca71a5…/a180ecc5…，KV521936/preempt0→1。20:47:45.919662Z source416无变化、68MiB0%、双栈9031闭/无GPU进程，controller Z和shutdown错误保留。227.54834548803046s/2448.0775670122475total/TTFT62799.9383899587ms只是VERIFY1原始绝对值；**不与202526的增长DB诊断计算收益**，没有不回读性能门或完整accuracy。future free/LRU变化、单victim覆盖边界仍在；容量必要下界早退只研究，未混入这份source。

2026-10-22，systems_innovation实现，framework/hardware独立只读审阅，root唯一GPU owner。本候选依据BI-V150真实normal42布局和202526已激活的单victim恢复，不覆盖稳定成绩、原a1b源码或证据。不改参数、模型、量化/推测、框架版本或worker传输实现。

## 实测依据与可减少的工作

`20261021T202526Z-kv-retain-context16k-long`已经完成一次R16704/1044页/718405632B的真实恢复，42层全byte回读及runner/原输出消费通过；此轮VERIFY1、DB增长518表19337行，仅为协议诊断。hardware对该原件目的页序列独立分析：1044页原序有1044个按`next==previous+1`定义的run，其中978个邻接是−1；对同一页集合升序可得66run。源页SAVE的1008copy不因此改变。

normal42传输器c95f只有物理页与逻辑host页都连续时合并copy。故对这份旧页集合推导，目的RESTORE/诊断回读调用可从1044×42=43848降到66×42=2772；这是对已存集合的CPU推导，**不是新服务实测或收益承诺**。actual worker31cc:240–247的ZERO同样先make_plan并按run执行narrow(...,count).zero_()，zero_calls=42×len(plan.runs)，因此对同一旧页集合ZERO也可从43848降到2772；这同样只是旧集合推导，非新实测。新run的实际页集合、run数和copy次数以新marker/完整RPC ACK为准，不能把旧集合66直接写成新测结果。

## 实际源码与别名边界

exact manager2e91:580→coordinator9dd0:346返回nonempty `single.req_to_blocks[rid]`的原list，`KVCacheBlocks`不复制它；`get_block_ids()`另建ID列表。外部R分配`delay_cache_blocks=True`后，真实目的页已全分配，`num_cached_block[rid]==0`，没有把host内容作为有效cache发布。返回的`allocate_slots`结果主要是本次`allocate_new_blocks`，外部前缀已分配时可能为空，**不使用这个返回值冒充完整目的页**，而是再次从manager.get_blocks取实际owned。

22e的后续`allocate_new_blocks`只extend后缀；`cache_blocks`把`req_to_blocks[rid]`逻辑位置与request的block hash同位置关联。因而必须先重排真实Block对象list，再按该新list把逻辑host页i恢复到新的物理页i；后续新SchedulerOutput的完整ID表及e155 cached-resume也从同一list生成。绝不能仅排序RPC IDs、修改Block.block_id、排序host内容、改变旧queued payload或旧runner表。

## 精确实现与守卫

候选 `patches/framework/biv150_kv_protocol.py` SHA **0e2115d0fbdedea64d1b911c0d6ae3b359f178004d844a8dd8088dfa4388fb86**，历史a1b逐byte保 `analysis/source/kv-transaction/biv150_kv_protocol.a1b691.py`。去掉一个helper和bind前的一条调用后，完整字节精确逆回a1b；事务616、worker31cc、copyc95f、init footer、454次defer路径均未改。

仅在已有私有校验后、`tx.bind_private_allocation`/ZERO之前调用`_order_private_pages`，要求：

- 一个非空group，`type(pages) is list`且与`single.req_to_blocks[rid]`对象相同；`num_cached_block`实际整数0。
- tx仍HOST_RESIDENT、source已释放、无pending/inflight/cancel/closed、destination尚未绑定。
- 页数恰好R/16；每个Block ref_cnt1、非null、无hash，页ID与Block对象都唯一。

守卫外直接False，走a1b未排序路径；守卫内只`pages.sort(key=block_id)`，原地保持同list/同Block对象到原ID的对应与同页集合，随后重新导出destination，按原tail集合证明绑定。历史`new_block_ids`原字节/原顺序不改，也不把它当pending zero list。一次`PRIVATE_PAGES_ORDERED`记录前后run、同页/同对象/同list、host逻辑顺序不变和未来free次序可变。

本次allocator已经选择/evict的集合不变；**未来`free(reversed(req_blocks))`归还物理页次序会变**，包括失败回滚路径，不声称后继allocator/LRU轨迹完全一样。新服务必须独立验证，不能仅以“同set”免去准确率/复现门。

## 最短必要门

唯一新CPU合同 `tests/test_biv150_kv_private_order.py`（SHA **29deff8d51fcf6f7f7811aacc84a3ac6f9d431c3e08879a80b39206d178522b5**）1项/0.001s通过：真实CPU事务绑定异序fresh集合，构造host逻辑行在新表中读取仍顺序一致；同list/对象/ID/ref/hash/history/旧ID副本不变；错别名、cached/shared/hashed/pending/已bind或publish/重复页均不排序。没有框架/设备导入，没有重复旧copy/DTO/defer套件。`analysis/source/kv-transaction/private-order-cpu-check.json`保存命令/SHA及精确逆变换；首次逆校验因多一个空行断言失败，修检查脚本后精确，runtime未改。CPU四页映射不等真实1044页设备证明。

framework已核实际list/cache/runner别名并审冻结0e2115与CPU合同；hardware负责目的页几何和最终定向审阅。交付时定义的root唯一新隔离服务门保持原long参数与VERIFY1，至少必须得到实际PRIVATE_PAGES_ORDERED、同key正确的ZERO/RESTORE/42层回读、发布与runner六check及原output消费、32/0/tokens、源/DB/KV/清理齐全。没有marker或guard回退只算未激活，不能声称排序生效。该门现已完成，见顶部204159；仍不作性能归因，不混prefix截断或454次CPU下界早退。

最终更正：初稿及本agent消息误称ZERO固定逐页不减少，root按actual worker31cc反证后已逐源复读并纠正；ZERO也按make_plan.runs合并。仅改叙述，protocol0e2115/worker31cc/事务616/c95f及全部原证据未变。双职责最终终审均无阻断，root负责唯一新设备门。


## 不回读配对已完成，但不能归因收益

205219 stable 32-0/220.40704781701788s/KV521936/DB51819337不变，205819同0e源码32-0/220.92108358303085s/KV521840/DB51819337→51919340；参数/物理32GiB/CPU6与初始DB虽相同，KV+DB双失配，不能报gain。205819实际R16688/1043页/717717504B、SAVE966copy、排序1043→66、ZERO/RESTORE各2772、462skip、runner6check/原16token消费通过；VERIFY0没有回读，不套204159的1044页/8token/全byte诊断。独立原件审计205219-independent-review.json、205819-independent-review.json已保存，原始绝对值/失配与退出日志保留。容量67e4另是冻结CPU候选，未混入此轮，不能继承排序实测资格。
