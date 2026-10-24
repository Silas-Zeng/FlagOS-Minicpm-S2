# 当前6f组合的GPU热点：框架侧下一步

2026-10-22，framework owner，仅本地原件／源码阅读。当前基点是runner **6f918ae6** 与metadata **0e961524**、async **1bb85e31**，保留SQL、确定性top-p、prefill54c、C2、C3；不把尚在对照的C3views／pure-gather或其它KV候选算入基点。本文没有新GPU、SSH、模型导入或主代码改动。仅适用BI-V150。

**先补当前自然mixed的短native时间线，再选GPU实现。现有证据不能支持“当前仍有92.96%在Attention”或“大量时间花在输入等待”。** 最多保留下述两个减少真实GPU工作的切口，不再扩CPU对象／key／Event微优化。

## 可继承与不能继承的证据

| 原件 | 实际可用结论 | 对当前版本的限制 |
|---|---|---|
| `experiments/profiles/b0-triton-16k-prefill/prefill/results/` | 旧5步948kernel、3720.346ms；Attention3458.5ms、MM224.64ms；旧窗口GPU间隙约0.99% | 此时Attention启发式尚未换54c，92.96%不是当前比例。不能拿旧算子百分比决定新调度。 |
| `experiments/profiles/20261021T042609Z-native-decode/{manifest,summary}.json` | 原生5步真实B62/62/61/61/60，当前同字节top-p da77／runtimea0c／Attention54c／MM4c2e。可见LM-head合5.598190ms、rank2温度除法1.678733ms、hist1.568927ms、rank1随机分数除法0.916709ms、softmax0.879402ms | runner尚无SQL／C2／C3／两CPU方法。5个graph壳合401.683256ms，内部kernel不透明；不能将可见kernel排名当全GPU排名，graph与kernel也没有可相加的覆盖关系。 |
| `experiments/profiles/a3-hist-top-p-profile/` | 已经证明旧top-p大头能被真实实现消除 | 当时hist还是早期4split，与当前确定性1split不同，不继续使用其hist比例。 |
| 当前组合104544／104920 `-control/input-prep-timing-*.json` | 部分快照256／2048步；入口等待1.858095ms／14.059984ms，整个preprocess4.553461s／14.488007s；占0.0408%／0.0970% | 不是全程覆盖，preprocess包含CPU工作及已有提交，不等于GPU空洞。没有证据优先拆入口同步。 |
| `analysis/source/preemption-snapshot/progress-pair-resource-samples.json` | 旧两长服务约5秒采样GPU util中位96／95、SM时钟1500；CPU限流周期仅约0.165% | 不是当前6f，离散利用率不等于occupancy或HBM带宽；不能由6CPU规格宣称host critical。 |

042609 manifest SHA **a896c3ae**，summary **bb0a7a6e**。本轮只用stdlib重聚合既有summary／gzip，不重跑原validator或设备。旧061506的SQL反射13.4s已由SQL补丁消除，不计入新预算。MM CTA grouping、mapped decode、visible-prefix、overlap、growth／KV事务均有既有正负或失配记录，不换名字重新列作新方向。

## 候选一：单位温度时跳过整词表GPU除法

这是当前证据最直接、改动较小的一项，优先级高于重做sampler编译。实际sampler源码：

- `experiments/source-audits/20261021T174453Z-benchmark-sampling/source/vllm/v1/sample/sampler.py`，**1a2f18dd**，`apply_temperature()`无条件 `logits.div_(temp.unsqueeze(1))`；非all_random还先处理greedy温度。
- `experiments/source-audits/20261021T170854Z-scheduler-kv-c3/source/vllm/v1/worker/gpu_input_batch.py`，**de1ea4fc**：185–191为CPU温度镜像，383–387按真实请求赋值，644／775随swap／condense移动，832起由同镜像构造GPU温度及SamplingMetadata。

可迁移实现是**从本步真实CPU元数据证明全部有效随机行温度恰为FP32的1，才省掉一次全词表读写**；未知metadata、混greedy、非1、spec／额外采样行等仍原路。不能只根据模型generation_config或比赛默认猜恒1，也不能 `.item()`／D2H验证后反而增加同步。须把证明绑定到最终行顺序／同SamplingMetadata，本步重新验证或依原更新版本失效，不能缓存一次all1永久使用。保原logits对象、处理顺序、top-p／softmax／指数噪声／全局和请求generator调用，不改采样参数、不裁词表。

旧已同字节GPU路径约**0.336ms／采样步**的温度除法是预算线索；graph壳约80ms／步说明即使全省也不能据此承诺大收益。该路径的实际当前shape／时长及是否处于暴露critical path仍待新trace。它减少GPU矩阵遍历而非只少一次Python调用，但很可能只是小收益。

最短确认：先从新native时间线将rank2 div关联到真实temperature调用及形状；仍有可见成本才写独立guard候选。真实sampler短门对同logits／同RNG状态比较输出logits、样本ID和调用后RNG，包含1／非1／混greedy、行变更、掩码-inf、正负零／非有限边界和fallback；不把NaN数学等价当bitwise证明。正确后复用当前4K64req128out最短服务对照；不先跑大官方或扫描温度。若当前已融合／成本不可见／guard抵消，停。**未实现、未测。**

## 候选二：把末层死输出行的gather前移，减少末层GPU计算

这是较重的框架图裁剪，列作条件性第二项，不能直接开服务。旧真实FX `tmp/remote-source/computation_graph.py`（**ab75722c**）7670起：`submod_83`为第41层全M KV写入＋Attention；7679起`submod_84`对全M执行O projection、残差norm、gate-up／SiLU／down及final norm。当前6f runner约4447行才 `sample_hidden_states=hidden_states[logits_indices]` 后做LM-head；非spec时2241行的indices为每请求query末行。两CPU方法没有移动这个边界。

第一最小版本仅把**末层Attention之后／O projection之前**的选行前移到`submod_84`入口：同一indices选Attention output和对应residual，再运行原尾段，后续LM-head仍N行。第0–40层以及第41层全M QKV／RoPE／KV写入／Attention都不动，不能跳prompt中间层或漏最后层KV。更早只算末层必要query虽还能少Attention，但需新的query metadata／kernel地址协议，当前不一起实施。

它与旧hidden-row gather候选不同：旧候选只替换已经全部计算完的最后gather；这里删除末层O／MLP的无消费者行计算。但只覆盖42层中的部分末层，**不能宣传几十个百分点**，decode M=N时也没有死行可省。GEMM的M改变会改变tile／归约实现，不能继承103/105或当前6f准确率；动态compile／AOT／capture、完整输出hidden API／aux／spec／pooling／TP-PP等须严格回退。需要先读当前installed Llama/compile尾段身份，旧FX不是已验证的新hook。

最短确认：新自然mixed trace先确认末层尾段耗时及真实M/N；只在其预算明显大于gather/新小M GEMM成本时继续。第一门取实际末层输入及权重，比较原全M尾段后选行与前移选行后尾段，换值／新指针、residual alias、选中hidden／logits误差、完整KV不变和后继decode；未验证其它完整hidden消费者时只限定原text非spec路径。没有正预算则停，不铺43段graph缓存。**未实现、未测，优先级低于低风险identity删工作及新GPU排名。**

## 当前最短native确认接线

root已要求、hardware独占准备`tmp/current-mixed-native/`；本owner只审新增差分，不竞争写代码。复用原bc51的ixsys启动／`--profile-from-start off`／cleanup与原SERVER，不加torch profiler选项、不改生成参数。最小driver fork仅允许原`--context-screen`与native并用，仍16K输入／32请求／128输出／c64／seed721201；新的独立诊断目录及source保全部SHA，不进入官方baseline。

沿原native footer，在真实execute观察到自然mixed（至少一个1-token及一个>1-token请求）后，第三个合格步开始，只采**3个连续实际execute**；开始／停止边界保原native诊断同步，不每层同步。逐步记录真实shape／single-query数，若中间夹puredecode须明确列出，不能造出全mixed样本；没有自然mixed或trace无有效kernel则诊断不成立，不改调度硬凑。计划取真实2D／3D/reducer、四MM投影、sampler／memcpy与GPU空洞；实际graph仍不透明时保未知，不为此开启eager或改变graph服务参数。

这轮只回答**当前昂贵GPU路径和可消除工作**，不从带profiler耗时报告吞吐收益。完成现有C3views／gather对照后由root串行执行，本owner不启动设备；尚无这轮trace结果。

接线定向终审已通过：`tmp/current-mixed-native/mixed_native_footer.py` **f0f41e30**、`prepare_mixed_native.py` **60b6b691**、`run_mixed_native_screen.py` **2214bbed**，生成runner **29d98aee**。初稿在第三execute返回后立即stop会漏第三次独立`sample_tokens`；按6f4477／4496／4514及actual Core27b549／565修为**第四execute入口先同步／stop／restore，再原第四call一次**，窗口只记录前3个成功execute。作者仅更新同一CPU计数合同，本owner未重跑。driver只改context＋native联合与3步mixed验收，原SERVER／负载／seed／ixsys／清理不变；夹puredecode时严格拒绝完整mixed结论。root负责新launcher和完整412基点map、原单卡锁／DB／后态；只读审阅不等于实际trace成立。

单位温度补审：actual InputBatch 的`all_random`只表示`greedy_reqs`为空、`all_greedy`只表示`random_reqs`为空（1091–1096），**没有现成O(1)的all-temperature-one字段**，二者都不能代替全1证明。最小可行边界是在原`_make_sampling_metadata`（832起，batch成员／行序变化时由812–830刷新）对已上传源`temperature_cpu[:num_reqs]`做一次O(N)精确FP32全1判定，将证明绑定到新SamplingMetadata对象及其温度tensor／N；常态复用该对象的采样步仅O(1)核身份／资格即可，不必每步扫描或维护新请求集合。add／remove／swap／condense必须使证明随原metadata更新失效；dummy、spec额外行、替换metadata、任何未知外部温度写入均原路，不凭旧id或模型默认猜值。仅限定all_random且有效行数对应时，省原`logits.div_(1)`不改用户温度／处理顺序／随机数消耗／logits对象；仍须短门验证实际浮点边界、原alias及后续sampler，不先承诺NaN payload或in-place版本计数无影响。证明创建、严格guard和wrapper自身都要计入成本；旧0.336ms/步仅局部预算，11:44:35Z新诊断尚在途，若当前trace无明显rank2除法预算或落在未暴露区间，直接停止本方向，不为它另跑长服务／社区搜索／新实现。

114435诊断后续root回执：三个真实步骤均N2／M2048／P2047，可见2D Attention126次640.380ms／60.2339%、GEMM504次337.1918ms／31.7161%、3D约2.689%，sampler＋vocab仅0.0426%（名称归类下界，不冒称完全覆盖）。**因此单位温度identity停止实现，本文此前两个切口不是当前实施队列。** 本owner反查a4四CSV及`analysis/2026-10-21-prefill-unmeasured-candidates.md`：42行17配置没有w16；w4、T128、BM256及s2／s3已有负结果，不重扫；visible-prefix／mapped／overlap已有原件不重复。当前N2中C3已实际分出1decode＋2047prefill，框架重排没有遗漏decode可删，BQ16对齐只移动不足16token尾部且不删除累计工作，不支持新FCFS／chunk改法。root现唯一选择**2D固定BM128/T64/s1的8→16 warps**，hardware独占`tmp/next-prefill-w16/`；D1/P2047/KV16K仅上界fixture，trace未记录实际seq_len。framework仅互审新增launch／数值边界和原门小差分：3D原C2w2不变、未知guard回原、同KV／scale／stream／RNG、编译资源与误差失败保留、一次32ABBA；warp布局变不继承bitwise或准确率。尚无该点设备结果。
