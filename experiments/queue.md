# 实验队列

本表全部实验/成绩均属天数BI-V150。队友负责沐曦－曦云C500；仅团队实验分析库按两平台归档，两个私有代码库共用，不要求平台拆分。不把本轮数据作C500或团队整体成绩，原始证据路径不移动。

**按用户要求冻结所有新增性能探索。** 所有未开始项均冻结，旧“待开始”“CPU/设备”或历史partial不授权重启。原版官方`20261021T122607Z-original-baseline`已于2026-10-21 16:14:50.001906Z以exit0完成，8raw/2summary及225源SHA、最终bab2本地独立终审通过。原2–4轮分档totalTPS候选/原版为4K1.933207729倍、16K3.166027317倍；初始DB不同、KV差96tokens，不合成总分或声称cache-matched因果稳定。现无新增设备任务；此前14:47Z/15:35Z进度仅为历史。

只完成既有CPU材料、最终必要审计/比较及registry/report更新；不集成原型、不改默认、不加GPU/accuracy、不扫描或重跑准备smoke。GitHub上传现已获用户授权，由root负责；三个协作仓库均为private：`Silas-Zeng/FlagOS-S2-vllm-plugin-FL`、`Silas-Zeng/FlagGems`、`Silas-Zeng/FlagOS-S2-Minicpm-throughput`。原公开fork保留，不把新上传授权当作恢复性能探索；外部消息仍不由本agent发送。

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

## 执行边界

- 原13eb基线122607已完整结束，root12:26:07Z实际恢复54c41796B→bab241176B、启动及封存后bab2均核实。未清SQLite/Tritoncache；初始DB与候选不同必须保留。仅隔离091033插件不足以证明原版，live/source依赖身份不可省略。不得将本次冻结解除或因结果再启设备实验。
- 既有基线benchmark退出、CSV/日志封存后才由owner清理服务。历史`stop_managed_server.sh`是已有流程记录，不是在途停止指令。
- 历史流程在新GPU前调用`check_ready_for_experiment.sh`；当前所有未开始GPU项冻结，不据此启动。
- 含profiler的服务参数仅作诊断，不能混入正式计时。
- 单次或profiler结果不能写成稳定收益，不能捏造比赛总分。
