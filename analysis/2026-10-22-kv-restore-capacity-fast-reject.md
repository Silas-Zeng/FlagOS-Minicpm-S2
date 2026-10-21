# KV恢复容量必要下界：独立快拒候选

## 最新：仅独立候选已实现，canonical0e与在途pair未改

root读完下述研究后授权最小实现。新文件 `patches/framework/candidates/biv150_kv_capacity_protocol.py` SHA **67e4c07566ee3e52f84d6a96a494b8976d858420dadd5f833e66c3291e32fb73**，安装时必须映射到**新的隔离source**的`vllm_fl/patches/biv150_kv_protocol.py`；不能直接作为candidates子包启用，也不能覆盖当前canonical0e或在途配对source。历史0e全字节另存 `analysis/source/kv-transaction/biv150_kv_protocol.0e2115.py`。worker31cc、事务616、c95f、init footer、builder/launcher及官方命令均未改。

只新增stdlib sys、可选Request类缓存/两个helper、原try_restore hash前的一次if和fast_rejects累计；去掉这几项完整字节精确逆回canonical0e。Request守卫从**已加载**sys.modules读取实际Request类，核06b1整源SHA/模块类名/真实类identity、原init/append/num_tokens方法文件与无wrapper；不import框架。缺模块/源不符/异常仅禁快捷路径，旧协议正常继续，不把它加入全协议fatal scope。守卫结果只缓存一次，不重复读源/hash文件。

仅严格nonresumable、streaming_queueNone、同真实Request类型进入快路。长度O(1)不足先按原原因DROP；否则R整页且maxlen内、no-owned、cached无或整数0，F<P才defer并累计fast_rejects，保HOST/原FCFS；F>=P或任何其它guard回旧完整tokens/digest/history/actualallocator。原身份/终止/epoch/status/pending/placeholder/budget检查先行，没有新增future消费/GPU动作/准入放宽。计数沿已有稀疏FIRST/RPC/publish/drop事件带出，不逐步打印。

唯一新 `tests/test_biv150_kv_capacity_protocol.py` SHA **e9c57108e0e0c859ea512a6be8b851cfee78a3a8b48e0e0c5a6da43681379730**，实跑1项/0.021s通过：AST抽取已审Request/RequestStatus实际定义（不import其torch/框架依赖、未运行init），源/方法guard实际执行；F=P−1重复时tokens/hash/history/allocator计数全0，F=P及owned/cached/streaming/inputqueue/超max/缺源或源错走原完整链，取消/对象/epoch/长度即时释放，原output0保HOST/普通work时DROP。CPU证据 `analysis/source/kv-transaction/capacity-cpu-check.json`保存命令/SHA/精确逆变换；没有重跑旧COPY/DTO/defer合同或设备。hardware与framework均已实核冻结67e4/合同及JSON并终审无阻断，未重复执行合同。不把CPU AST合同称实际服务命中。

## 新隔离包装，尚未执行

按root授权新增 `scripts/remote/prepare_kv_capacity_source.py` SHA **a79b69d81115dd17ba77e09f5de690cda6a9cb5288f0c200f1868ee2f5d86eee** 和 `scripts/remote/launch_kv_capacity.sh` SHA **0ae8ced5c97f2460a97ac046eb808d47aa84915e80867e12c219d3dad457a32b**。复用旧4c8/8d7，只新文件最小差异，旧包装逐SHA未变。builder仍只接受冻结080656及ROOT/code新直系目录、普通素材文件/固定SHA；仅将ROOT/scripts下新input `biv150_kv_capacity_protocol.py` 67e4字节映到新source `vllm_fl/patches/biv150_kv_protocol.py`，manifest记录输入文件映射，init791c/worker31cc/事务616/c95f不变，runner e155不改。

launcher新标签`kv-capacity`、VERIFY1，原bc51 driver命令逐字不变，保68MiB0/无GPU进程/9031双栈闭前置、DB快照与run/control源码封存。purpose要求fast_rejects>0及capacity_lower_bound，再实际排序/保存/清零/恢复/全byte回读/runner/原消费；若快路未命中只能记未激活，旧协议仍可正常完成。`capacity-wrapper-check.json`保存Python及heredoc compile、固定pin与最小diff核验；没有执行shell/prepare整copy/新suite/GPU。hardware最终只读审阅和root全文diff审均已接受，无修改请求；三个新文件67e4/a79b/0ae保持冻结，不上传执行，设备先后由root解锁后决定。

当时唯一在途仍是0e的205819不回读性能配对，**不是67e4**；其root已观察KV521840与205219 stable521936失配，不能把未来原始差异作严格同容量收益，不改参数凑容量。容量候选不得改动该pair，也不得继承0e已测成功作为自身激活/性能证据。

2026-10-22。以下为实现前CPU-only研究与负例；**当前canonical0e2115和其已测204159/在途性能配对均未修改，新候选没有设备激活/收益或accuracy结果**。目标是保留原FCFS/allocator/恢复协议，只省去确定无法分配时的Python工作，不是准入放宽、整输出预留或新调度器。

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

Request actual SHA为 `06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80`；canonical0e未把Request列为专用guard，因此独立67e4已按顶部方案只为快捷路径增加验证。不能默认为该源/类已验证，应仅禁快捷而保旧恢复协议，避免新守卫使整轮协议静默no-op。该scope尚无新服务fast_rejects命中证据，不冒称已激活。

## 若root选择实现，最短必要验证

实现前定义的一次定向CPU合同：F=P−1时不触tokens复制/hash/history/allocator但原FCFS照走；F=P走旧真实检查；有owned/local/window或streaming进入旧路；取消/epoch/长度不足即时失效；未触发快捷路径时输出/资源路径保持。计数只加cheap累计fast_rejects，通过首次及原publish/drop日志带出，不逐步日志或引入profiling。当前67e4唯一合同已按顶部范围实跑，其它源码scope由旧guard保留，没有扩大到新模型/窗口或重复旧大门。

后继一项root串行隔离VERIFY门须fast_rejects实际大于0，同时完整ZERO/RESTORE/42层回读/runner和原消费、源/DB/KV/idle通过；然后才讨论不回读的同参数性能对照。当前204159是0e原始页排序结果，不能声称验证本早退。不给设备owner增加重复COPY/DTO大门，不改官方命令或模型。

阶段收尾：0e的205819已完成，不是67e4；与205219同时KV521840vs521936和DB51819337→51919340失配，不报收益。205819的462skip/R16688等不能当本快捷路径命中；没有fast_rejects设备证据。root要求本批完成后暂停文件写入供一致归档，goal持续，待解锁再接续。
