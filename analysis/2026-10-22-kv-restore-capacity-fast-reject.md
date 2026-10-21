# KV恢复容量必要下界：只研究安全快速拒绝

2026-10-22。root要求CPU-only研究；**没有修改受测0e2115，没有实现新runtime/测试或启动设备**。204159页排序门独立完成，不能把本方案混入其结果。目标是保留原FCFS/allocator/恢复协议，只省去确定无法分配时的Python工作，不是准入放宽、整输出预留或新调度器。

## 精确热点和现有证据

当前 `patches/framework/biv150_kv_protocol.py` SHA `0e2115d0fbdedea64d1b911c0d6ae3b359f178004d844a8dd8088dfa4388fb86`，`_try_restore`159起：在身份/epoch/status/computed和pending/placeholder/budget检查后，每次先 `list(request.all_token_ids)`、`prefix_digest(tokens,R)`，再 `tuple(single.new_block_ids)`，最后调用 `allocate_slots(0new,externalR,delay_cache=True)`；容量不足才保HOST回原路径。FullAttention的new_block_ids为不drain历史，因此tuple可能长于本次R页数，不能把它当待zero列表或借此清空历史。

202526及204159各有restore_skips454，只有首条defer含free/reason：F1030、P1044、request_tokens16712、reserveTrue、pending/placeholder0。每个R16704 digest包含16704次整数检查、to_bytes和hash.update；454×R=7583616是“所有skip都走到digest”的可能上界，**不是已测执行计数/CPU时间**。没有各次free、digest/histcopy计数或host独占计时，不能说454次全可省、CPU节流已证或预报收益。最短后继验证应先证明早退实际命中，仍保留小信号，不设收益淘汰线。

## 必要条件证明，不代替准入

已审actual sources：manager2e91（184108）、single22e/coordinator9dd0（173831）、blockpool3fc5/request06b1（170854），以及df780 scheduler/Core27b。只在原协议eligible的单FullAttention/16token块、同一仍PREEMPTED且computed0的victim、无旧owned页、无local命中参数、完整R页、`0<R<=manager.max_model_len`时考虑。

记P=R/16、F=block_pool.get_num_free_blocks()。调用参数固定0new、0local、externalR、0lookahead、无connector；single predictor22e:130起在无owned/无local/无skip时第二次检查至少需P页。FullAttention继承`get_num_skipped_tokens=0`（22e:522），`remove_skipped_blocks`直接返回，不会先释放可帮助本次分配的页。2e91:162明确assert watermark非负；实际值不需要假定为0，水位/完整序列约束只会增加要求。故 **F<P必定返回None，既不会touch/evict/cache，也不会分配external页**。blockpool:692读free计数本身是O(1)只读。

因此最小切口是原暂态检查之后、复制tokens/digest/history之前：严格守卫成立且F<P时，仅 `_defer_restore(...reason=capacity_lower_bound)`并return，随后继续原waiting FCFS；原output真正普通准入仍按原wrapper释放host。F>=P只说明“不被必要下界否决”，必须走完整digest和actual allocate，保原full_sequence_must_fit值、水位和其它真实条件。不能用F>=P宣布有容量、跳过allocator、改waiting顺序或park请求。

## 必须先处理的边界和反例

- **已有owned页**：computed0不等于没有物理页。必须只读 `.req_to_blocks.get(rid)`核空，并对`num_cached_block`一致性核无或0；否则原分配可能只补缺口，F<P并不代表失败，走旧路。
- **window/recycling/hybrid/多个group/外部localhit**：skip/recycle/null页或共享命中会减少新页需求，不能使用总P下界；全部走旧路。原cachedprefix命中H页还需计ref0 touch的E，不能套“命中就免费”的公式，更不能据此改本次外部R路径。
- **F==P**：边界不拒绝。完整序列可能需P+1或水位，实际allocator仍可None；反过来不能把未知watermark加进快速阈值。R未整页、超maxlen、类型/源身份或状态不符均回旧路。
- **digest提前检查被延后**：数学容量证明不等于host生命周期完全等价。如果同对象token前缀在F<P时发生改变，直接早退会延迟DROP，暂占唯一host slot，可能阻止另一个victim保存。不能隐瞒这个区别。actual Request06b1普通`append_output_token_ids`只追加、ConstantList视图防直接修改，但df780:1179 streaming session明确`del _all_token_ids[...]`并追加新输入。首版快速路径应仅接受已审Request源/真实类、`resumable is False`且`streaming_queue is None`的封闭输入；其它情况保旧digest。追加旧FIFO输出不会修改稳定前缀；原pending/placeholder检查仍在早退之前。
- **长度失效和取消**：廉价`request.num_tokens<=R`应仍先DROP，不等容量；原request对象/attempt/status/finished检查和Core取消清理都保留。即便普通封闭输入，未来真实分配前仍完整digest，不将源身份/只读视图冒充字节校验。若不能证明某运行类型的前缀只追加，宁可不启用此快捷路径。
- **失败allocator副作用**：这里只证明FullAttention、no-owned、F<P这一分支的失败无touch/free/事件；不声称所有allocateNone都是只读，不把此结论推广到窗口/connector/正在拥有页的请求。没有新增future.wait/result、GPU同步、cache清理或历史list消费。

Request actual SHA为 `06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80`；当前协议未把Request列为专用guard，若未来实现不能默认为该源/类已验证。应仅禁用快捷路径而保留原恢复协议，避免新守卫使整轮协议静默no-op。该scope尚未在新服务打印`resumable/streaming_queue`实际值，不冒称已经命中。

## 若root选择实现，最短必要验证

一次定向CPU合同即可覆盖：F=P−1时不触tokens复制/hash/history/allocator但原FCFS照走；F=P走旧真实检查；有owned/local/window或streaming进入旧路；取消/epoch/长度不足即时失效；未触发快捷路径时输出/资源路径保持。计数可只加一个cheap累计fast_rejects，通过首次及原publish/drop日志带出，不逐步日志或引入profiling。此处仅列门，**没有新测试执行**。

后继一项root串行隔离VERIFY门须fast_rejects实际大于0，同时完整ZERO/RESTORE/42层回读/runner和原消费、源/DB/KV/idle通过；然后才讨论不回读的同参数性能对照。当前204159是0e原始页排序结果，不能声称验证本早退。不给设备owner增加重复COPY/DTO大门，不改官方命令或模型。
