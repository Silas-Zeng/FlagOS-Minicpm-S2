# 实验队列

本表全部实验/成绩均属天数BI-V150。队友负责沐曦－曦云C500；仅团队实验分析库按两平台归档，两个私有代码库共用，不要求平台拆分。不把本轮数据作C500或团队整体成绩，原始证据路径不移动。

**用户于2026-10-21 16:40Z授权继续自主探索，覆盖此前冻结。** 大收益优先，小收益也用最短上卡门验证并保留，噪声标待确认，不设最低百分比；正确性失败不启用，但代码和负结果保存。所有设备任务仍由root单卡串行拥有。新门50–63已封存；async/metadata各自同KV单次+0.703657%/+0.286723%保留，CTA第一服务pair描述+1.745903%但KV池差96、同物理32GiB，不称KV严格匹配或默认资格。181041 terminal0，不实现drain；后继单victim保存/恢复及私有页排序已诊断通过，0e不回读205219/205819配对KV+DB双失配，不报收益。归档写锁已解除，capacity212106真实462快拒及42层回读/原16token消费通过；FULL三独立副本及唯一CPU合同已双终审，新包装仅静态检查且hardware终审无阻断，FULL214400已由2071实际验收pass，真实FULL/0ZERO/42回读/原消费完成，仅VERIFY1诊断。213016基点KV521936、已完成213616候选KV521840容量失配；双方DB前后51919340同，FULL214400已真实验收通过；后继由root串行；不混VERIFY诊断收益。本agent不擅自设备。

本批215849/220122两次startup已独立验收，全部实际内存分项相同、KV均521936，未复现历史6块，不报gain/倒补原因。后继共同6a两组VERIFY0已完整结束（81/82），小TPS信号分别+0.1988%/+0.0603%分层保留，本项不再重复；230548真实snapshot已完成（83）。**root完成232735一致ZIP并解锁，当前唯一新候选为84进展victim/FULL一次VERIFY1机制门：015315机制已真实通过，DB增长不报gain；已授权首个同6a/VERIFY0性能A/B见85，A原FULL在途；不叠c6/新timer、不自动增加smoke或重复pair。设备仍root单卡串行。**

稳定原版官方`20261021T122607Z-original-baseline`已16:14:50.001906Z以exit0完成，8raw/2summary及225源SHA、最终bab2本地独立终审通过。原2–4轮分档totalTPS候选/原版4K1.933207729倍、16K3.166027317倍；初始DB不同、KV差96tokens，不合成总分或声称cache-matched因果稳定；新诊断不覆盖这两份正式原件。三个private协作仓库已由root完整上传核验：`Silas-Zeng/FlagOS-S2-vllm-plugin-FL`、`Silas-Zeng/FlagGems`、`Silas-Zeng/FlagOS-S2-Minicpm-throughput`。原公开fork保留，外部消息仍不由本agent发送。

**最新2026-10-22：85的A/B已完整收口，KV/启动项失配，收益null且不追加盲复跑。后继86的032653实际独立API门已完整验收：两case字节/流/guard/RNG通过，wall波动不能报稳定收益；原件与编译/DB/后态齐，不启动服务。**

下表按历史证据记录，不是待执行任务单。标为设备的任务必须单卡串行；旧阶段“待测”在后续行解决时，以后续证据及CURRENT为准。

| 顺序 | 状态 | 类型 | 实验 | 结果/验收边界 |
|---:|---|---|---|---|
| 1 | 历史不完整 | 设备 | 未修改原版4K/16K官方基线，每档四轮 | 4K完成，16K只保留两条稳定记录 |
| 2 | 已完成 | 设备 | 采集prefill及稳态decode的torch trace | 精确形状与有效迭代已保存 |
| 3 | 已完成 | CPU | 按内核/算子/阶段聚合trace | 已定位主要内核 |
| 4 | 已否定 | 设备 | 扫描FlagGems FA2 tile及KV block-size | FlagGems端到端仍慢 |
| 5 | 已保留 | 设备 | 调优generic Triton Attention launch策略 | prefill内核7.1x，accuracy门通过 |
| 6 | 已完成 | 设备 | BF16 decode GEMM及带宽微基准 | 硬件下限已记录 |
| 7 | 已保留 | 设备 | 重写top-p-only采样器 | 内核13.9x，确定性门通过 |
| 8 | 历史不完整 | 设备 | 运行smoke、对齐及4K/16K诊断 | 准确率96.2%；长官方重复按当时用户要求停止 |
| 9 | 已否定 | 设备 | 非算子/编译器短筛 | block64、batch4096/8192、禁prefix、sampler compile均慢 |
| 10 | 既有材料收尾，未开始验证冻结 | CPU/设备 | 整理干净复现证据与报告材料 | 命令和证据可独立复建 |
| 11 | 已短筛，保留候选 | CPU/设备 | 跳过未变块表上传 | CPU10项+GPU32次状态迁移/3次replay通过；端到端增益未定 |
| 12 | 已完成 | 设备 | 基线greedy smoke重复，保留IDs/logprobs | 基线本身同greedy请求也不同，保留为验证边界 |
| 13 | 已短筛 | CPU/设备 | 直接3D decode映射与mixed Attention拆分 | 直接映射逐位通过，4K单层约1.3%；mixed大多较小，保留尾部条件 |
| 14 | 已完成，graph内部未展开 | 设备 | 原生五步decode graph trace 20261021T042609Z | 捕获五次graph replay（每次约80 ms）；ixsys未展开MM/Attention内部节点 |
| 15 | 能力门失败 | 设备 | 微型graph外部计时事件20261021T044007Z | replay elapsed_time报invalid resource handle，不扩成模型启动实验 |
| 16 | 单层机会信号 | CPU/设备 | 仅decode launch stages/warps 20261021T044807Z | w2s1单层延迟约降40%，五个输出门全逐位通过；当时未测端到端/accuracy |
| 17 | 完成，小幅未确认信号 | CPU/设备 | C2/B0匹配4K64请求/128输出decode短筛 | 119.224对120.671s（吞吐+1.21%）；无重复/accuracy，KV差96tokens，保留但不称官方成绩 |
| 18 | 单层机会信号 | CPU/设备 | mixed Attention拆分+w2s1 decode 20261021T051426Z | 完整chunk单层约降18%/10%；prefill精确/decode不同，未计metadata，accuracy未测 |
| 19 | 真实门通过20261021T054501Z | CPU/设备 | 天然prefix mixed拆分builder/forward接入 | 真实Builder/Impl、手工拆分精确、跨stream样本及纯graph通过；整2D decode不同，当时accuracy待测 |
| 20 | 完成，小幅未确认信号 | 设备 | C3同负载框架mixed服务短筛20261021T054922Z | 117.259s/2305.457 total tok/s，64/0；单轮相对B0约+2.91%，无accuracy/prefix覆盖证明 |
| 21 | 已完成，热点已定位 | CPU/设备 | 八步host profile 20261021T061506Z | _prepare_input_ids13.446/13.948s，重复SQL反射10.780s；不是性能成绩 |
| 22 | 门通过20261021T063353Z | CPU/设备 | 精确异步token gather/scatter融合门 | 十二个actual-method case精确，非法映射guard及动态62/61/60同cache entry；无服务/accuracy结论 |
| 23 | 重复强短信号 | CPU/设备 | SQL模型反射限于实际请求表 | SQL43.199/43.091s对匹配B0 120.471s，同KV521840，各64/0；非官方成绩 |
| 24 | 单次短信号20261021T073309Z | 设备 | SQL+decode launch组合 | 41.154s/64成功；相对SQL KV+96，增量未确认；DB479表/17982行不变 |
| 25 | 通过20261021T073644Z | 设备 | SQL+decode launch官方Level3准确率 | 101/105（96.19%），零错误、一个输出上限样本；清理完成，无官方吞吐成绩 |
| 26 | 单次正向短筛20261021T080656Z | 设备 | SQL+mixed Attention短筛 | 39.160s/64成功，同SQL+C2的KV521936；增量未确认，当时组合accuracy待测；设备已释放 |
| 27 | 完成，短信号有混杂 | 设备 | 16K128输出对照20261021T083031Z / 083455Z | SQL+C2 131.739s对mixed120.670s，各32/0；首轮DB479→481表、KV差96，+9.17%非可归因稳定收益 |
| 28 | 完成，长输出信号有混杂 | 设备 | 16K1024输出/32请求SQL+C2 084659 / mixed 085302 | 236.025s对220.368s，各32/0；首轮DB增2表67行、KV差96；+7.10%单次信号当时待warm控制，mixed accuracy未测 |
| 29 | 完成，暖库单次信号 | 设备 | SQL+C2已暖16K1024输出/32请求重复20261021T085855Z | 231.322s，32/0；DB483表18119行/三hash及KV521840与mixed相同；mixed+4.97%仍单次信号；抢占计数1只一次观测非最终值；清理完成 |
| 30 | 通过20261021T090505Z | 设备 | SQL+C3 mixed官方Level3准确率 | 独立原件核验103/105（98.0952%），105success0error/105stop0cap；228源hash、核心080656精确；清理68MiB0%端口关；SQL+C2此前101/105仍通过 |
| 31 | 完整完成并独立验收20261021T092944Z | 设备 | SQL+C3原两档四轮官方吞吐 | 8raw/2summary的SUCCESS/tokens/原丢首均值已核；4K3683.65 total tok/s/355.88s，16K2729.07/816.48s；230源SHA/080656核心精确；KV521936；DB489/18384→501/18789；exit0，10:55:26Z清理68MiB0%端口关；原122607完整对照分档1.933207729x/3.166027317x，非cache-matched，不算总分 |
| 32 | V1未激活，V2原因已定位 | CPU/设备 | 显式启用输出增长预算准入 | runtime9245/7项CPU合同互审；110747只有INSTALLED无CHECKED/DEFERRED；112603唯一false为实际V2=true；独立72d6支持已审builtin V2，无accuracy/收益声明 |
| 33 | 归档基础设施失败已独立确认20261021T105526Z | 设备 | token-bucket padding行/KV合成门 | exit1/cases[]；8源SHA已核；hash处理__pycache__触发IsADirectoryError，未跑候选case；重试只加is_file过滤，负面证据保留 |
| 34 | 合成隔离门通过20261021T105930Z | 设备 | token-bucket padding行/KV门重跑 | 13源SHA独立核；259→384/952→1024有效Attention+整KV精确/maxdiff0；后继32decode/整KV精确；毒值尾/RNG-padding门过；非完整ModelRunner/hidden-gather/GEMM/LM-head/sampler/accuracy；11:01:49Z清理68MiB0%端口关 |
| 35 | 完整独立控制审计20261021T110149Z | 设备 | SQL+C3 16K长输出创新匹配基点 | 220.494323s/2526.396110 total tok/s/32成功；21源SHA/同bc51 driver；KV521840/DB501表18789行不变/preempt0→1；11:07:46Z清理；非官方成绩 |
| 36 | 已完成但激活不明20261021T110747Z | 设备 | growth-admission同driver长筛 | 220.369s/32成功；22源SHA/DB不变，KV521936差96；EngineCore有INSTALLED无FIRST_CHECKED，preempt0→1；非激活/性能证明；11:18:03Z清理 |
| 37 | fixture门独立通过20261021T111804Z | 设备 | hidden-row BF16复制正确性门 | 8源SHA；259/952/2048/64（62真实行）四case bitwise/fresh/RNG；int32动态1entry、int64/8回退/跨stream通过；非fullrunner/accuracy/性能；11:20:21Z清理 |
| 38 | 完成，无可归因收益20261021T112021Z | 设备 | hidden-gather 16K长输出服务短筛 | 22源SHA/真实FIRST_SELECTED；220.357327s/2527.966764 total/32成功；KV521936对基点521840；DB501/18789不变/preempt0→1；约0.06%单差不证明收益；11:26:02Z清理，保留 |
| 39 | 诊断完成20261021T112603Z | 设备 | growth constructor描述符smoke | 23源SHA；EngineCore156959 builtinAsync的29guard仅notV2为false/28true/无异常；seed721001；DB501/18789不变；非性能；11:32:08Z清理 |
| 40 | 完成，冷库混杂20261021T113208Z | 设备 | token-bucket 16K长输出首次服务 | 22源SHA/真实FIRST_SELECTED1696→1792；231.619268s/2405.050339 total/32成功；KV521936/preempt0→1；DB501/18789→506/18926，增5表137行，不冷轮判回退；11:37:27Z清理 |
| 41 | 单层门过，计时未定20261021T113727Z | 设备 | mixed Attention双stream overlap | 14源SHA/输出KV/RNG/不同Q的join/回退全过；每窗4calls，wall中位12.883671→12.561840ms（省2.498%），但event12.421241→12.517388ms变慢；无并发/fullmodel/accuracy/E2E结论；pendingframes4→0；11:39:46Z清理 |
| 42 | 完整独立warm审计20261021T113946Z | 设备 | bucket同16K长输出必要warm重复 | 22源SHA/真实FIRST_SELECTED；220.390442s/2527.586930 total/32成功；KV521936/preempt0→1；DB506/18926三hash不变；旧C3基点DB501/KV521840不同，无可归因增益或冷轮回退声明；11:45:52Z清理 |
| 43 | 已筛，默认关闭不集成 | CPU/设备 | 已审builtin V2的独立growth revision2 | runtime72d6/transforme5ba/test2cee；真实CHECKED+DEFERRED、preempt0；必要warm221.233836s无吞吐信号/TTFT更高；DB506→512仍混杂；保留代码/证据，不大accuracy |
| 44 | 门通过，无E2E收益声明20261021T114553Z | 设备 | mixed overlap 64-loop必要摊销复核 | 14源SHA/同正确性全true/pending0峰9；methodv2把event构造放wall之外，64loops ABBA；wall12.460649→12.417108ms省0.349429%；event12.409186→12.414136ms持平略慢；保留原型不接服务；11:47:13Z清理 |
| 45 | 完整独立控制审计20261021T114713Z | 设备 | growthV2 DB506匹配原C3基点 | 21源SHA/原080656/bc51/同16Klong seed；220.249703s/2529.202049 total/32成功/meanTTFT62440.319729ms；KV521840/preempt0→1；DB506/18926三hash不变且同warm；11:52:46Z清理 |
| 46 | 完成且激活，冷DB混杂20261021T115247Z | 设备 | growthV2同driver DB506长筛 | 22源SHA/EngineCore162561 CHECKED31595free1151future及DEFERRED2702free2722future；238.113366s/2339.457082 total/32成功/meanTTFT68405.784913ms；KV521936/preempt0→0；DB506/18926→512/19130，增6表204行；当时仅需一次warm，不称最终性能/accuracy；11:59:21Z清理 |
| 47 | 完整独立warm审计，不集成20261021T115950Z | 设备 | growthV2同16K长输出必要warm重复 | 22源SHA/EngineCore164138 CHECKED+DEFERRED2696free2722future；221.233836s/2517.951184 total/32成功/TTFT67130.273776ms；KV521840/preempt0→0；DB512/19130三hash不变；对114713无吞吐信号/TTFT+7.51%，跨DB506→512边界保留；默认关/不大accuracy；12:18:37Z清理 |
| 48 | 完整独立终审通过，保留退出警告20261021T122607Z | 设备 | 原13eb两档各四轮官方基线 | 8raw/2summary原均值门过；4K1905.46total/687.94s、16K861.99/2584.99s；225archive/captured-liveSHA全同、原446f/Attentionbab2/无retained；CPU6/32768MiB；KV521840；DB512/19130→516/19270；16:14:50Z exit0cleanup空，16:17:27Z68/0/双栈端口闭无GPU进程；runner166637仅Z/PPid1导致首次seal末/proc断言失败，原记录与独立说明保留；原2-4轮比率见页首，不捏造总分 |
| 49 | 单层门独立通过20261021T121838Z | 设备 | actual2D full-visible prefix省mask | 15源SHA/两case bitsKVrng/随机页/3负slot+NaN padding/1prefill及C2回退全过；originalproxy恢复；仅P2019计时32calls ABBA：wall12.594359734→12.559617125ms省0.275858%，event12.491010189→12.434306145ms省0.453959%；保留小层信号，非graph/fullrunner/服务/accuracy；12:25:01Z清理 |
| 50 | 完成并独立验收20261021T173003Z | 设备 | SQL+C3实际自然前缀/plan覆盖计数诊断 | plugin411 SHA/e155→a39a/coverage29137/bc51核实；32/0、524288in4096out/120.483993s，KV521936，DB516/19270三hash不变/preempt0→0/CPU6；最后周期384calls/305metadata/250mixed/3000single-query decode请求步/2241prefix及plan/759outside，77unsupported单列、零计数错误；非全程非forward；17:38:31Z68/0/双栈闭无GPU进程，runner仅Z；不作性能结论 |
| 51 | guard拒绝，原因待诊断20261021T173921Z | 设备 | 固定MLP tile仅改CTA枚举 | 11源SHA/06c7policy/4b44gate/原4c2e核实；仅gate-up2048/12288/2048实际执行，bits/finite/inputs/RNG true但guard_rows false，exit1；无timing/down，保留负面，不启用，也不先判kernel越界或guard误报；17:39:31Z68/0/端口空闲无GPU进程 |
| 52 | 实际方法门独立通过20261021T174115Z | 设备 | 复用CPU positions/seq metadata | 10源SHA/b124/0e9615/0096/e155→50493核实；decode62/M259/M952/M2048/纯prefill2048五fixture各11checks全true，连续event+固定地址graph消费通过/selected75/RNG timing不变；32call方法wallABBA0.712748078→0.656465406ms省7.896573%约56.283us，只是方法门，非E2E/accuracy；17:41:34Z exit0/68/0/无GPU进程 |
| 53 | 完成独立审计20261021T174402Z | 设备 | A1 SQL+C3短基线 | 39.410040799s/6859.571686total；64/0、262144in8192out；KV521840/DB51619270三hash不变/preempt0→0/CPU6；410源SHA/原bc51/serve/seed；供async配对，不跨容量归因；完整idle |
| 54 | 单次小信号保留20261021T174741Z | 设备 | async token独立短服务 | 39.134667002s/6907.839537total，FIRST_SELECTED/411SHA；同A1 KV521840和DB；TPS+0.70365693%、TTFT−0.86563824%；64/0同tokens/idle，非稳定因果/未集成新accuracy |
| 55 | 单次小信号保留20261021T175049Z | 设备 | CPUmetadata独立短服务 | 39.073248478s/6918.697844total，FIRST_SELECTED/411SHA；同后继A2 KV521936和DB；TPS+0.28672344%、TTFT+0.23443063%；64/0同tokens/idle，不能对A1报0.86%严格收益；未默认 |
| 56 | 完成独立审计20261021T175441Z | 设备 | A2 SQL+C3容量匹配短基线 | 39.185280642s/6898.917031total；KV521936匹配metadata，410SHA/DB三hash不变/CPU6/64-0同tokens/preempt0→0/idle；A1/A2容量不同，时间变化不是matched漂移 |
| 57 | 仅诊断，非正确性pass20261021T180033Z | 设备 | CTA guard分阶段positive CPU原位bits | 11源SHA/7phase/28basic文件全−15992=BF16−17且hash不变；advanced初始化即错12288、读后storage没变，C identity/offset24576正确；无timing/down，保留原173921失败，18:00:42Z idle |
| 58 | 两shape门通过，正负信号均保留20261021T180646Z | 设备 | CTA正式positive basic guard门 | b216/06c7/11SHA/8phase每shape共64basic文件/输出输入RNG及post全过；gate-up32call wall省16.175816%/event16.332453%，down慢3.807269%/3.884804%；仅固定tile fixture，非E2E/accuracy，不同时默认；18:06:56Z idle |
| 59 | 完成无回收机会20261021T181041Z | 设备 | KV实际失败/抢占/resume只观察长门 | 411SHA/a4de/initb3b7/e155/bc51/32成功0失败/524288in32768out/220.345997616s仅诊断/KV521840；35快照，末2112core2109schedule、1fail/preempt/resume/obs0；free0需要1页queue1但terminal/private0，不实现drain；cache2944/floor16702/gap13758仅prefix exposure非GPUwork，非全程；DB51619270三hash不变/CPU6/preempt0→1；18:17:30Z68/0/双栈闭无设备进程 |
| 60 | 候选服务已实际命中20261021T182916Z | 设备 | 仅gate-up CTA group8服务 | 413源/5artifactSHA/7876/44fc/06c7；32成功0失败/524288in4096out/118.417526430s4462.042199total/KV521840/DB51619270不变；startup FIRST、首真实2048/1req step选42次，非全负载计数；与61描述TPS+1.745903%但KV差96，同物理32GiB；postidle，关停abort后EngineDeadError/forcekill保留，未默认/accuracy |
| 61 | 干净对照已验20261021T183543Z | 设备 | 无probe SQL+C3 context16K | 410SHA/e155/bc51/原SERVER/seed；32/0同tokens/120.484981576s/KV521936，DB3hash不变/CPU6/32768MiB/postidle；候选池521840不同，描述pair不称KV matched；不拿coverage诊断比 |
| 62 | 编译失败无case20261021T183421Z | 设备 | mapped非prefix decode首正确性门 | 17SHA/首derived skip2D JIT use_sme68954357763被add_accelerate_matmul binding拒绝；exit1/cases[]/无time，原wrappers恢复/18:34:44Z68/0/端口free；根因待actualcompiler审，未数学/性能通过，不启用 |
| 63 | 唯一必要基线重复20261021T184244Z | 设备 | 核同容量波动范围，不刷KV | 410SHA/32-0同tokens/120.763262668s4375.370360total/KV521936/DB51619270三hash不变/CPU6/postidle；与61同KV耗时跨度0.23096745%仅观察，不估计噪声分布；候选KV差保留，不改参数/假buffer/无限刷新 |

| 64 | 四case单层门通过20261021T184809Z | 设备 | mapped修编译选项传播的正确性门 | 17源SHA/四case13checks/整KV及独立oracle bits/FP32三行/nextdecode与crossstream-capture回退通过；非模型accuracy；无time/exit0/18:48:35Z idle |
| 65 | 单层正信号保留20261021T185023Z | 设备 | mapped构造D29 timing | 同17SHA/四case；32callABBA wall14.344921375→12.435507453ms省13.310731%，event省12.762442%；D29/P2019是构造非服务实测几何，非模型/graph/accuracy；exit0/18:50:46Z idle |
| 66 | 服务无正信号20261021T185627Z | 设备 | mapped真实服务短筛 | 独立414SHA/32-0/524288in4096out/121.790163836s4338.478440total/KV521840/DB三SHA51619270不变；Engine207423真实FIRST_SELECTED D15非全程；对183543描述TPS−1.071665%且KV不同，不能将层13.31%外推；CPU6/32GiB/post19:00:37Z idle，shutdown ERROR保留，未默认 |

| 67 | 导入前失败20261021T191017Z | 设备 | 42层KV save/poison/restore首门 | 独立8SHA/d841/c95f/exit1/cases[]；source/copy.py遮蔽stdlib造成dataclasses循环，未初始化复制，无正确性/成本结论；19:11:31Z完整idle，原件不改；93eb仅改四档名引用，CPU真实source旧fail新pass+hardware审准，待重测 |

| 68 | 重复正/首轮负均保留20261021T191131Z | 设备 | mapped同候选唯一重复 | 414SHA（413同首轮，仅包装时间/argv/output异）/32-0同tokens/117.028659571s4514.996599total/TTFT59836.117857ms/KV521840/DB3hash不变/CPU6/32GiB/idle；真实FIRST D15非全程；首轮121.790163836s并列不择优、不归cold或coverage；干净基线KV仍差96，未默认/accuracy |

| 69 | 字节与事件门通过20261021T191545Z | 设备 | 42层672MiB每向KV copy四几何 | 独立8SHA/93eb/c95f/四case八pass×五checks与RNG全true，actual42views/guard/未选poison；normal42/336、packed1/8copy；roundtrip wall222.053105/235.270289/119.956194/120.716930ms单warm样本，hostquota/提交混杂未知，不推稳定DMA或E2E；构造非observed布局/无模型恢复protocol；19:18:05Z idle，旧失败保留 |
| 70 | 已完成，仅SAVE/free | 设备协议诊断 | 200957单victim KV保存恢复v1 | 独立416源/DB三SHA/CPU6/32GiB/idle；32-0，SAVE R16704/718405632B完成后原free，再DROP；skip1但无ZERO/RESTORE/回读/消费，旧日志不区分原因，不报收益；旧50375原字节保留。 |
| 71 | 已完成，单victim协议诊断 | 设备 | 202526暂态保留a1b691 | 416源/32-0；SAVE/free→454skip保HOST→ZERO/RESTORE全42层byteequal→PUBLISH/DROP→runner六checks/原output8tokens；DB51619270→51819337、VERIFY1/240.929935s不报性能，非完整accuracy；后态idle通过，200957未知原因不回填。 |
| 72 | 已完成，单victim排序协议诊断 | 设备 | 204159私有目的Block排序0e2115 | 实际PRIVATE1044→66run；ZERO/RESTORE/42层回读各2772调用/718405632Bpass，publish/drop/runner六check/原8token消费；32-0、51819337三SHA不变、416源/idle过；227.548345s为VERIFY诊断，不与202526增长DB算收益，不混454早退/截断。 |
| 73 | 已完成，配对双失配 | 设备基点 | 205219不回读stable长负载基点 | 410源/32-0/220.407047817s/KV521936/DB51819337三SHA不变/idle；wrapper11917，205819候选已完成且KV521840/DB增长双失配，不报gain/严格容量matched。 |
| 74 | 已完成，容量快拒诊断 | 设备 | 212106容量必要下界67e4 | 实际fast462/首1039<P1043，R16688/717717504B/66run；ZERO/RESTORE/42层回读各2772，全byte/runner六checks/原16token消费通过；32-0、DB51919340三SHA同、416源/idle，无ERROR但forcekill WARN保留；227.191134s仅VERIFY1诊断，不是FULL证据或吞吐收益。 |
| 75 | 已完成，KV+DB双失配 | 设备 | 205819不回读0e页序候选 | 32-0/220.921083583s，R16688/1043页/PRIVATE66run/ZERO-RESTORE各2772/原16token消费，无回读；KV521840对基点521936、DB51819337→51919340，不报gain；416源/idle通过。 |

| 76 | 已完成，真实FULL诊断通过 | 设备 | 214400显式RESTORE_FULL事务 | 2071实际exit0/pass；416源/固定1aff84be5d9a与b4e63947/原bc51-SERVER-seed，32-0；SAVE→FULL→DROP serial123、0ZERO，R16704/P1044/718405632B、SAVE1008/FULL与42回读各2772全bytespass；zero_calls0/fast454/host释放/runner六checks/原consumer8，DB51919340三SHA同/KV521936/idle；226.794828s仅VERIFY1诊断，不报性能/完整accuracy。 |

| 77 | 配对完成，DB同/KV失配 | 设备基点 | 213016容量性能stable VERIFY0 | 独立410源/原SERVER-bc51/32-0/220.505020230s/KV521936/DB51919340三SHA前后同/CPU6/32GiB/idle；raw完成后shutdown ERROR/WARN分类保留；213616候选完整验收，KV521840对base521936差96失配、双方DB前后51919340同，不补stable凑容量/不归因gain。 |

| 78 | 已完成，DB同但KV失配 | 设备 | 213616容量VERIFY0候选 | 独立416源/32-0/218.917006328s/KV521840 vs base521936；双方DB51919340三SHA前后同；实际fast462/R16688/717717504B/66run/旧ZERO-RESTORE各2772/host释放/runner六checks/原16token消费，无回读；source/idle过，raw后shutdown错误分类保留，不归因性能/不套FULL证据。 |

| 79 | 已完成，启动标量诊断 | 设备 | 215849同6a stable smoke | 412全源/原bc51 smoke-only-VERIFY0/8in32out完整；PID231345实际profile1/原int→PARENT真list/三hook恢复，全部内存标量完整，KV521936；DB51919340三SHA同/post22:01:02.902726Z68/0/闭/source过，ERROR空但forcekill WARN保留；不报性能/不回填6块原因。 |

| 80 | 已完成，两启动分项相同 | 设备 | 220122同6a capacity smoke | 418全源/原innovation5bef字节保持/原bc51 smoke-only-VERIFY0/8in32out完整；PID231998实际profile1/PARENT真list/三hook恢复；内存分项与215849同、KV均521936，未复现旧6块；DB51919340三SHA同/post22:03:14.114658Z68/0/闭/源过，ERROR空/WARN保留，无gain或历史因果。 |

| 81 | 首pair完成，小信号及唯一复核均保留 | 设备 | 222731capacity→223613FULL，共同6a VERIFY0 | 两侧418/KV521840/内存非时间项/CPU6/32GiB/DB51919340三hash/实际pageIDs和R16688几何/fast462/consumer16均同；218.818909→218.384834s，FULL TPS+0.198765756%、耗时-0.198371462%、TTFT-0.215245394%；0ZERO，VERIFY0无回读；唯一c0全审+独立原字段+hardware页专项，保留单次小信号非稳定收益/纯ZERO时间/accuracy；唯一复核见82，两组分层，本项不再重复。 |

| 82 | A2/B2已完整验收，本项重复结束 | 设备 | 唯一必要A2/B2复核，同冻结源码和参数 | 224411 capacity e52a→225501 FULL 62b0，本agent各唯一c0 pass；两侧418/KV521936/启动分项/DB四端51919340三hash/原args与环境/R16704-P1044-718405632B-SAVE1008-目的66-fast454-consumer8同，218.847904625→218.716006502s，TPS+0.060305656%/耗时省0.060269311%（0.131898123s）/TTFT+0.207191537%。FULL2772/0ZERO/真ACK/runner6/host释放，VERIFY0无回读，post23:01:06Z源与idle过/ERROR空/WARN留。首组521840分开不混均值；小正TPS与TTFT负向均保留，按预定结束重复，不追容量不择最好，非稳定因果/accuracy。 |

| 83 | 首次真实snapshot已完整验收，无新策略 | 设备 | 230548抢占瞬间CPU只观察 | framework唯一6eb45/06c16d26全审，本agent只读登记；413/32-0/220.418993s仅诊断/KV521936/DB51919340三SHA同/后态23:11:57Z68-0双栈闭。Engine240315真实completeTrue：31running prompt16384/output327..569/free0派生需1/queued1，最小remaining455为已scheduled index0，原tail327/rem697/1045私有页中1044hashed。结构候选含原tail，不选评分/不改victim，不把free等同全前缀重算，不承诺FCFS公平或收益；shutdown ERROR/WARN保留。后继只留中文最小路线，root决定controller/设备。 |

| 84 | 机制真实通过，DB增长不报gain | 设备 | 015315唯一进展victim/FULL VERIFY1门 | 唯一b7ff全审f776f89b；真实28候选选原index2/output552不同于tail30/output327，单次主动替换/原preempt0→1；SAVE-FULL-DROP同rid，R16928/P1058/728039424B/SAVE37run1554/目的65/FULL与42回读2730/0ZERO/fast454/runner6/consumer9/host释放。417/live/32-0/238.576937023s仅诊断/KV521936/CPU6/32GiB；DB51919340→52319474(+4表134行)，三SHA全变不报性能，01:59:22Z68-0双栈闭/ERROR空/WARN留。下一性能包装等root正式指令，不自动重复；最新用户暂不发布/PR，不为发布停写。 |

| 85 | A/B完整完成，KV与启动项失配，收益null | 设备 | 首个FULL1aff/进展72942共同6a VERIFY0性能A/B | A020721 218.399598237s/KV521936；B021658唯一3f1/90f3c896 pass，218.513384285s/KV521840，nonTorch+4MiB但不归因。两侧418/32-0/原args环境/DB四端52319474三SHAdc2c-0dc7-c05d同，environment_matchfalse，TPS/duration/TTFT收益均null。B实际9候选选index21/output392不同tail30/output319、failed20；R16768-P1048/SAVE26段1092/目的66-FULL2772/0ZERO/fast462/consumer9/host释放，无回读，原preempt0→1，02:22:42Z源live/idle过/ERROR空/WARN留。动态策略行为允许不同，本首对结束不追加盲复跑/第三run，不追容量、不算raw时差gain，后续等root决定。 |

| 86 | 已完成，真实API字节通过，wall不稳定 | 独立API设备门 | 032653单层两真实SAVE页序，C batch与正pitch | 唯一原件审计eff32911：86seal/7源/实际SDK编译so9e33及mappedlibd39d；两map18checks+计后5+RNG/独立CPU payloadSHA全过，37→11和26→6calls（全部原KV字节保留）。首case8call ABBA wall基线7.4153/1.4542 vs候选0.6723/0.6819ms，event基线约0.6525 vs候选约0.6282ms，仅组合单层信号；不报稳定wall收益/独立2D贡献/42层服务/E2E。DB52319474三SHA同，CPU6/56Torch线程/host20GiB观察非峰值；03:27:06Z68-0双栈闭/source不变。registry113，首本地Path URI修正留痕非设备失败，不重跑。 |

| 87 | 已完成，三路真实字节通过且六窗无节流增长 | 独立API设备门 | 035754唯一64call c95f/C-linear/C2D镜像门 | 实际系统审计9d0bcd7b：86seal/7源/编译so9e33/ABI及maps/同非0流/DB和后态全过，两map30checks+计后7+RNG/CPU payloadSHA同。A37/26、B37/26linear（受控fallback9/4）、C11/6调用；首case64call A/B/C/C/B/A wall0.682748/0.655124/0.631449/0.631231/0.654983/0.689953ms，event及逐窗v1原值另存，六窗nr_throttled/throttled_time增量0；不追溯032653原因、不报稳定服务/E2E。CPU6/56线程不改、DB52319474三SHA同、03:58:09Z68-0双栈闭/源不变。registry114，本门不自动重复。 |

| 88 | 已完成，真实SAVE与FULL两组42层字节通过 | 真实服务机制门 | 042225新SAVE a662接入原FULL420树 | 唯一后验d7213a76：420/cd3d-df6a/a662-818e-0a4d-SO9e33/原1aff84be791ce155与原bc51long VERIFY1均核。实际R16688-P1043-717717504B/23run→5segments每层，SAVE210=168linear+42pitched（旧966），源free前42c95f966calls全bytespass；原FULL66run2772及独立42回读2772pass，0ZERO/serial123/DROP/runner6/原consumer16/fast462/host释放。32-0/230.825783s仅诊断/KV521840/CPU6/32GiB/DB52319474三SHA同，04:29:03Z68-0双栈闭/源live过，ERROR空/WARN留；registry115，不报收益/accuracy，不自动大官方或重复长pair。 |

| 89 | 已完成，Event完成性通过，typedblocking无CPU下降信号 | 独立API门 | 045818 generic/typed/typedblocking ABCCBA | 唯一系统审计b21fb342：61seal/source2/实际源pin/DB及post过；24trial×6=144checks/RNGtrue、early0。每trial8次32MiB，wait-threadCPU三路均约9.44ms，typedblocking未见下降；首C wall较低伴threadCPU/wall异常原样留，不报gain。六窗节流增量0，DB52319474三SHA同/04:58:26Z68-0双栈闭/源码不变。registry116，下一仅已授权nativeSDK差异门，完成手头即转GitHub维护，不新服务/大测试。 |

| 90 | 最后手头门已完成，native无CPU下降，不接服务 | 独立API门 | 051336 generic/typedblocking/directCorexblocking | 唯一系统审计365e6760：85seal/source5/actualSDK编译so1376/flags3/mapsd39、24trial144checks/RNG/settled-close全部过；native threadCPU两窗9.4344/9.4364ms≈wall9.4194/9.4210ms，无低CPU证据。early0、六窗节流增量0，DB52319474三SHA同/05:13:44Z68-0双栈闭/源码不变。首次SCP未退出时文件锁仅收集时序，完整exit0解包后全核，非设备失败。registry117，按用户完成手头后只维护GitHub/方法PR，不新实验/服务/大测试。 |

## 执行边界

- 原13eb基线122607已完整结束，root12:26:07Z实际恢复54c41796B→bab241176B、启动及封存后bab2均核实。未清SQLite/Tritoncache；初始DB与候选不同必须保留。仅隔离091033插件不足以证明原版，live/source依赖身份不可省略。16:40Z继续探索授权覆盖旧冻结；新增设备实验由root另行排程，不改既有正式原件。
- 既有基线benchmark退出、CSV/日志封存后才由owner清理服务。历史`stop_managed_server.sh`是已有流程记录，不是在途停止指令。
- 新GPU前保留空闲/同锁/源码身份检查，仅root按最新授权串行启动；本agent只CPU，不因研究或旧待测行自行上卡。
- 含profiler的服务参数仅作诊断，不能混入正式计时。
- 单次或profiler结果不能写成稳定收益，不能捏造比赛总分。
