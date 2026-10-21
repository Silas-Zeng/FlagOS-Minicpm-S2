# systems_innovation 子智能体交接

更新时间：2026-10-22（Asia/Shanghai；详细实验时间以原始 UTC 为准）。

## 最新用户冻结范围：停止新增探索，完成已开始事项后交接

用户已明确停止新增探索。以下范围覆盖后文历史任务和探索建议：

- root持有的原版official `20261021T122607Z-original-baseline`现已完成，完整两档原四轮/原CSV、源码与bab2依赖、真实DB/KV和清理证据均已取回。本agent仅本地CPU终审，不SSH/GPU。
- 本agent已完成**已有任务必要的独立终审、现有e9dc只读比较入口验收、registry和owner报告真实结果更新**；分档描述比率已核，不合成官方总分，不称初始DB相同或稳定因果收益。
- 已开始的CPU草稿只收尾材料，不集成新优化、不改默认候选，不新增GPU验证/探索/扫描/accuracy轮次；不因小信号继续开启新方向。现有代码、negative与原型保留为历史证据。
- GitHub上传现已获用户授权，由root负责。三个协作仓库均为private：`Silas-Zeng/FlagOS-S2-vllm-plugin-FL`（新建，原公开fork保留）、`Silas-Zeng/FlagGems`、`Silas-Zeng/FlagOS-S2-Minicpm-throughput`。本agent只整理本地材料，不发外部消息；新上传授权不恢复性能探索，也不授权修改原参考仓库。
- 既定完整终审已完成，接下来待命；不重复验证、包装测试或pending smoke，不自行恢复探索。

历史冻结回报中的“未获推送授权”已被上述用户新授权覆盖。双平台范围同样以上级最新确认优先：仅实验分析库按天数BI-V150、沐曦－曦云C500归档，两个代码库共用；本agent现有实验/成绩全部BI-V150，C500由队友负责，不能汇作团队整体成绩。

## 2026-10-22 接续：文档中文化收尾

- 已完成八份负责文档的中文叙述：`docs/official-verification.md`、`docs/compliance-checklist.md`、`docs/environment-2026-10-21.md`、`docs/measurement-log.md`、`docs/report-outline.md`、`experiments/README.md`、`experiments/candidate-matrix.md`、`experiments/queue.md`。历史计划按时间和冻结范围解释，命令、哈希、数值及原证据/source保持。
- 明确当前候选准确率103/105（98.0952%）、95%门槛已验；官方计分区间未知，不生成总体计分公式。旧partial不作最终基线；候选绝对结果与原版最终比较分开。
- 本轮仅CPU文档操作，没有模型、GPU、SSH、源码导入、重跑smoke或新增测试。root继续持有原版official；最后收到的15:35Z回执为7raw/1summary、16K最后4/4在途、Attention bab2，尚未收到完整终审原件，故不提前填registry或最终gain。
- 轻量保真检查：八份文档旧长短哈希、数字与原始代码块全部保留；原有内联项仅将pending/verified/not applicable/device等状态词翻为中文。实验队列仍保留1至49行历史事项。原始source、CSV与证据目录未修改。
- 下一步仅等待root取回完整原件，再按既有最终证据清单和e9dc比较入口独立审计、更新registry/report；不恢复探索。

本轮最终回执：八份文档中文化完成；保留原命令、哈希、数值与49项历史队列。仅实验分析库按BI-V150/C500分平台归档，两个私有代码库共用，本轮成绩全部BI-V150。GitHub上传授权已更新为由root负责三个private协作库；性能探索继续冻结。保真报告：`analysis/2026-10-22-systems-docs-zh-preservation.json`。等待root完整原版证据，仅做既有独立终审/registry/比较，不上卡、不新增探索。

## 2026-10-22 原版结束封存脚本只读互审

root授权审新`seal_original_official.py`，本地读取eb0c2568版225项manifest映射、791/common及比较入口；AST/内存compile通过，只有stdlib，无模型/设备导入，不终止任何进程。原件保护、actual路径映射、bab2拷贝和新postflight字段无阻断。必要补强已发root：需对已保存ixsmi表断言无设备进程，而非只凭已知PID死与68MiB/0%。必须等runner确实退出后单次运行，避免先写新证据后遇活PID断言留下保护文件；monitor退出可引用原driver的wait与result.returncode。详细审阅和SHA见`analysis/2026-10-22-original-official-seal-review.md`。未运行main/SSH/GPU；不宣称封存成功，等待root最终实际版本和原件。

## 2026-10-22 原版完整证据终审及最终分档比较

root下载完成原版run/control后，本agent仅本地运行既有e9dc一次，exit0；原样JSON为`analysis/2026-10-21-official-final-comparison.json`，SHA52f8da4bea6ba7caf4f517edccb9c3c0ecbe85db89f79372b0e5c1c4fc74d832。补充独立审计落原版run的`independent-final-review.json`。原225archive字节/封存captured-live225、Attention三处bab2/worker446f及候230源54c/e155、原CLI/benchmark0813/driver791/包/单卡32768MiB、双方CPU6 before-after、DB快照实体三hash、finished时间和CSV原hash全部核对通过。

原2–4轮均值：4K1905.46→3683.65total tok/s，1.933207729367187倍（+93.3207729367187%），TTFT12310.5566667→4781.6433333ms（−61.15818753931246%）；16K861.9866667→2729.0733333total，3.166027316741171倍（+216.6027316741171%），TTFT636429.44→185063.6533333ms（−70.92157563714632%）。已同时发root和framework报告owner。

必要限制：原KV521840/候521936；原DB512/19130→516/19270，候489/18384→501/18789，初始不相同，不能称cache-matched、稳定因果或官方总分。全部仅BI-V150。原driver16:14:50.001906Z exit0cleanup_errors空，fullpost16:17:27.184712Z68MiB0%/9031IPv4IPv6闭/无GPU进程，server/benchmark/EngineCore退出；runner166637实际Z/PPid1，首次seal5292版末/proc不存在断言失败，源/idle字段已成功、原结果不改，过程说明和封存记录保留并核哈希。双方shutdown均有force-kill剩余1进程warning；原版无ERROR/Traceback，不误写没有任何警告。

更新了registry原122607与092944行（仍73行16列）、framework-experiments顶端/末节、queue31/48及页首（仍49项）。未改root README/CURRENT/技术报告，无远端命令、框架导入、新测试或新GPU任务；探索继续冻结。

最终回执原文：完整原版终审与既有e9dc比较完成，exit0。4K吞吐比1.933207729倍（+93.3208%）、TTFT−61.1582%；16K3.166027317倍（+216.6027%）、TTFT−70.9216%。原CSV/225源及候230源、DB/KV/CPU6、结束与退出警告均已核，初始DB不同/KV+96边界及runner僵尸解释保留，不合成官方总分。原registry行/owner报告/queue/交接已更新；无新设备任务。

## 2026-10-22 私有完整tree发布入口只读互审

root授权只读审`publish_private_tree.py`（SHA256 `3c6f2a11a2a7df056dc79b78f3930a8386bd98e19ea1919b7a50923067340ce0`）及`.gitattributes`（`a3c4f2f48b8e74f69f930ede8386ab1dd6d8d822f6575640966e0b834e550319`），没有执行发布、API或新测试，没有改其它文件。

当前普通Python运行下无阻断：仓库参数白名单仅三专用协作名，GET metadata实际校验private/full_name；只经已登录gh api，不读取token、不创建credential。按本地Git tree的blob原字节及mode构建远端完整tree；tree SHA必须等于本地、recursive返回不能截断且逐entry path/mode/type/SHA相等，核main仍为原parent后只以force:false更新。两个symlink的mode120000和链接target blob也在此验收内。空仓库首次README初始化是已授权的新私有库初始化步骤；最终源码发布仍需完整tree门。

`.gitattributes`先设普通文本LF，末尾对experiments、analysis/source、patches、tests/fixtures设-text，避免原始证据/源码字节被归一化。已读root实际4287文件的`tmp/git-evidence-byte-check.json`，mismatches=[]；两个symlink按target比较是正确口径。本agent没有重复该检查。

已向root说明唯一复用边界：关键private/tree/head条件使用assert，Python -O或PYTHONOPTIMIZE会移除。本次保持普通无优化Python即可按已审路径运行；未来通用化可改显式异常，不需要为本次重发两代码库或扩展验证。最终回执：只读审阅通过，无当前发布阻断；未执行网络或修改发布源码，性能探索仍冻结。

## 任务与边界

- root 分派：CPU-only 阅读现有源码、官方规则/benchmark、一手系统优化资料；最多提出两项有大收益可能且不重复既有负面方向的系统候选，保存到 `analysis/2026-10-21-innovation-systems.md`。
- 本轮记录 ownership：`analysis/2026-10-21-framework-experiments.md`、`experiments/registry.csv`、`experiments/queue.md`。仅按 root 提供的真实证据更新，不猜结果。
- 禁止 SSH、GPU、修改 benchmark/driver/候选、修改 CURRENT_WORK。root 是唯一 GPU owner。
- 已读根 AGENTS.md、CURRENT_WORK.md、现有 queue/registry、next-framework/large-gain/system-competition/mixed-token-bucket 研究；沿用既有成果，不从头重复。

## 当前实验证据与进度

- **最新root唯一GPU：official/20261021T122607Z-original-baseline runner166637**，source091033原13eb，原两档各4轮，正在运行，无完成吞吐结果。12:26:07Z root已实际用helper8b3337成功恢复installed Attention54c→bab2；完整restore record现已独立审通过3backupSHA+helper、双idle+post、逐byte反变换与manifest bab2。root12:29Z又核live installed+official manifest均bab2，benchmark167244/server166651/4K1of4/noBIVmarkers。
- 禁止SSH/GPU、任何retained/C3导入或再执行restore，以免污染原版正式baseline。启动后bab2指纹由root核验，源/原CSV/清理待真实证据。
- SQL+C3候选092944两档原4轮早已完成独立审计：4K3683.65/16K2729.07total；没有原13eb完整matched增益。115950 growth warm独立22源SHA/DB实体核完221.233836s，无正吞吐信号/TTFT约+7.51%，DB506→512限制保留，代码defaultoff，不集成/不大accuracy。121838省mask门已独立15源SHA/两cases核过，wall0.275858%/event0.453959%仅单层信号保留，不称服务/accuracy收益。
- 当前工作：owned记录同步实际restore已审+officialrunning，无新测试/设备/retainedimport。后文按时间保留历史探索与旧状态，以上为最新接续入口。

补充最新root回执：12:39Z startup-source-review.json本地记录225源SHA全通过、bab2保持；12:57Z实际4K原CSV已有2行、进入3/4，16K未开始，四进程存活。这些是阶段证据，无完整官方结果。已准备最终只读比较入口，见本文件末节与`docs/official-comparison.md`。

## 已改文件

- 新建本文件，保证子智能体的中间决策与最终回复可在切换 API 后恢复。

## 中间决策、结论与反证

- 不重新提已存在的共享 graph pool、裁图、量化、投机或改启动超参；既有文档证明共享 pool/大到小 capture 已存在，生命周期未证明 GiB 级可回收。
- mixed M 分桶已有专门设计，研究时不重复认领为新创新。新候选必须明确源码切口、机制、反证和最短验证。
- 16K warm pair 的约4.97%是已去除已知 DB/KV 初态混杂的单次短测信号；混合候选准确率103/105已独立通过，但不是官方性能稳定性结论。

## 未解问题与下一操作

1. 读取并复算 live4K 四轮/丢首均值与成功数，保留整体 running 状态。
2. 查询原比赛页与一手系统资料，结合本地 scheduler/KV 源码提出最多两项实际新方案。
3. root 提供完整官方结果后，按原8raw/2summary审计更新记录；在此之前不写完成/成绩。
4. 将研究最终答复复制到本文件，给 root 报告修改路径、关键结论和待验证项。

## 中间更新：live1004Z 独立审计已落盘

- 4K四轮均SUCCESS/256请求，1048576输入/262144输出；原第2–4轮各numeric均值复算全部匹配summary。Mean355.88秒、3683.65total tok/s、736.73output tok/s、MeanTTFT4781.64ms、MeanTPOT81.79ms。
- 新增 `experiments/official/20261021T092944Z-sql-mixed-official/live-20261021T1004Z/independent-partial-4k-review.json` 派生审计；未改原CSV。
- 已更新 owned report/registry/queue 为4K完成、16K待完成、整体running；没有matched baseline，不报整体加速。
- 官方比赛页本次web open不可达；采用项目已有2026-10-20原页面核实记录作为规则证据，并明确未重新核实live页，不编造新规则。

## 研究完成与下一 API 接续

- 新增 `analysis/2026-10-21-innovation-systems.md`，含规则来源、已有能力去重、两个新候选、反证、源码切口和最短上卡门槛。仅设计，没有候选代码、SSH或新GPU工作。
- 候选1：请求级未来输出增长 ledger，在容量边缘延缓首次准入以减少长prompt重算。v0.24已有默认完整ISL检查和watermark，不能改开关冒充创新；新方案与其差异是用实际API合法剩余max_tokens作未来预算。当前容量只能容纳29条17408tokens；保守预留可能把31活跃变29并伤TTFT/吞吐，须先看正式16K实际抢占/重算再决定。
- 候选2：仅少量preempted请求的精确KV host暂存，用payload往返替代长prefill；这是高风险后备，需要异步在途写/page重用的完整握手。不能把Ascend的现成P/D-only offload用于本mixed单卡，也不简单开connector。若实测拷贝+同步成本不划算，最小roundtrip gate即停止。
- 尚未取得安装版上游scheduler/KV manager的独立hash；本地plugin仅委托AsyncScheduler，公开v0.24只证明机制。实施前owner一次精确source核对即可，不建重型前置框架。
- 记录验证：registry现57数据行、每行16列；4K retained三轮sampleCV1.5067%，第4相对第2吞吐仍上升3.0531%，因此不把3轮均值称无漂移稳定值。
- 后续：等待root发完整官方16K/exit/result/DBafter/postflight本地证据，再更新本owner的report/registry/queue；不得拿live局部快照当整体完成。root可用followup_task重新唤醒此agent做记录审核。

## 本轮最终回报原文

已完成并落盘：`analysis/2026-10-21-innovation-systems.md` 和本交接文件。最多两项系统候选为输出增长预算准入、少量preempted KV精确host暂存；先等待正式16K证明重计算成本，避免重复已有完整ISL/watermark。4K局部独立审计通过，355.88s、3683.65total tok/s，各256success；owned report/registry/queue已更新，整个官方任务仍running。全程CPU/公开资料，无SSH/GPU、benchmark/driver/候选修改。


## 新授权：最小growth-admission实现（正式16K仍运行）

root最新显式授权仅本地CPU候选实现，取代先前“不得改候选”的本轮初始scope；仍禁止SSH/GPU/改冻结source/driver/benchmark/CURRENT。root10:17:06Z回执16K2/4，首轮128成功0失败/816.56s/2728.78total tok/s；累计metrics抢占6只是一次服务观测，不当分档最终值。

- 已读root新取回actual五源，hash全部写入runtime与implementation文档；coordinator与SingleType实际predictor证实可干净只读预算，无需持久ledger或自己重写物理page/refcount公式。
- 新增`patches/framework/biv150_growth_admission.py`（b27b3ac0855529f94c04fc55668fe4116ce15bb25b0a03e4c5779be3e9d9acdb）；显式enabled=True才安装，EngineCore进程创建scheduler前。仅waiting准入，ContextVar作用域保证不误拦running/capture/其他manager；actual allocated/preallocated、shared/free-prefix touch正确计入，apply_admission_cap=False，zero stale reservations。
- 新增`tests/test_biv150_growth_admission.py`（81e3106695f716d8b1fb3d4cc3b4e95b251f34a3f7e2f210208be8c89e5df920）；六必要CPU合同直接执行actual AST predictor，全过0.002s。未导torch/vLLM，无远端。
- 新增`analysis/2026-10-21-growth-admission-implementation.md`，含源码hash、实际切口、默认关/安装进程、风险、最短设备验证。已通知root交叉审查；不得将候选存在当已启用。
- owned report/registry/queue已记录10:17:06Z明确owner回执与候选CPU完成/GPU pending，整体官方仍running。
- 重大经验：物理free pool包含ref_cnt0的cache页，新prefix touch必须扣除；未来预算必须减已分配/预分配页；空running始终回原以免独自大请求被预算永拒；只在GPU-worker footer安装对EngineCore scheduler无效。保守future预算可能降低batch而适得其反，empty/超长回退仍可能重算。调度会影响无独立seed时随机数分配，不能继承C3 accuracy。
- 下一操作：root/另一owner交叉审runtime；当前official与baseline释放设备后，按root队列新source最短16K32req1024out，确认EngineCore marker/真实defer、完成tokens、TTFT、walltime、preemption。未值得继续不大accuracy/official。

本轮最终回报原文：最小独立growth runtime与六CPU合同已完成，原五源hash守卫、默认关闭、live预算无持久ledger；只waiting回None保持原FCFS。关键prefix/预分配/empty/超长/async回收合同通过，未碰冻结source/driver/设备。详细实现和风险已落盘，请root交叉审后决定最短串行上卡。


## 注册hook与最小证据补强（覆盖上文旧hash）

root指定general register_model接入，已准备纯bytes `patches/framework/biv150_growth_admission_source.py`，b0d5516684e4092dd643836c7bf43ffcd3681d855a32033d6745f13fda0cb709；exactinit SHAe043b789只在EOF的register_model尾append4空格import/install(enabled=True)，拒未知/二次transform，没有应用到冻结源码。实际pyproject确认general hook；register_quant_linear已先解析current_platform，避免platform register()期循环。公开v0.24 loader/core支持该时机，但仍须真实EngineCore marker验证。

runtime最新 **9245dd089a310620840a1c056544e66fb2dd0ea24f41ef8f0e4b22721bac7e49**，加first CHECKED pid/free/future一次日志，避免只有INSTALLED无法证明策略命中。tests最新 **da154cbf431257ab3350f4f935b11da5fb32f9965c332f37f986f6f8df0b9122**，7合同0.034s通过，新增purebyte hook编译/拒重复和actual AST方法install两次不嵌套。implementation文档和queue已更新。

framework_innovation独立初审实际预算路径无阻断：同轮新准入append/statusRUNNING在下次admit之前，会纳入未来预算；prefix ref0/预分配扣减/NoneFCFS/ContextVar finally正确。新hook已发其只读交叉审查，尚待最终回执。

## 跨owner最终审查与回报（覆盖上句待回执）

framework_innovation最终审9245/b0d5/da15通过，独立复跑7CPU合同0.030s；无阻断最短服务实验项。actual async_scheduler/core loader尚未独立本地审，故新source真启动必须用FIRST_CHECKED PID核EngineCore命中，不能只凭INSTALLED。其余作者文件未被reviewer修改。

pure transformer对冻结init只内存生成的输出SHA为d9e2caf40f8d126ec4344b6c98605847f9b4be438eb9961a2eb3bb0f40671ef9。所有候选默认关闭，实际冻结文件未变；root负责新隔离source及单卡队列。

本轮最终回报原文：growth-admission runtime9245、general-hook transformer b0d5、7CPU合同da15均完成并经framework owner独立审查复跑通过。原5源guard、actual prefix/allocated预算、empty/超长回退、无持久ledger；FIRST_CHECKED证明EngineCore真实策略命中。尚无GPU/accuracy/性能结果，下一步root在独立source最短串行16K32req长输出筛选。详细风险/命令/源码身份见implementation文档。


## 正式两档完整归档与独立复算完成（最新状态）

root提供092944完整本地run/control后，本agent独立读取raw/source/DB实体/postflight，没有SSH/GPU。新增 `experiments/official/20261021T092944Z-sql-mixed-official/independent-official-review.json`。8raw/2summary准确case次序，各4轮全SUCCESS/成功数及input-output tokens、numeric finite和原第2–4轮全部summary均值均匹配。4K3683.65total/736.73output tok/s355.88s；16K2729.07total/160.53output tok/s816.48s；sampleCV1.506742%/0.023917%。四核心exact090505 accuracy，230sourceSHA全部逐项通过，官方argv/0813脚本/4轮丢首/no profile/no smoke不变。实际KV **521936**，勿抄旧短测521840。

DB实体只读重算schema/logical/physical与manifest均匹配，前后 **489表18384行→501表18789行，+12表405行**；不能宣称DB相同。benchmark UTC09:30:39.405817→10:53:36.070467，exit0/no cleanup errors；fullpostflight UTC10:55:26.276614为68MiB0%9031closed/无进程。是绝对候选官方结果，没有原13eb matched增益或分数。owned report顶端与末节、registry、queue31均已改completed，并保留此前running历史。

当前唯一GPU为root回执`framework/20261021T105526Z-mixed-bucket-row-kv-gate`、controller151230，root确认正式清理后才启；新gate尚无本地manifest/result供审，只登记running（queue33/registry新增行）。不得根据记录假定设备空闲。registry目前58数据行、16列均完整。

实际async_scheduler.py SHA da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884已作者与framework owner读：无schedule override；实际AsyncSchedulerFL亦无override，base wrapper继承风险解除，不加新测试/不改runtime。安装仍须真实EngineCore CHECKED。

本轮最终回报原文：完整官方两档独立复算通过，4K3683.65total tok/s355.88s、16K2729.07total tok/s816.48s；230源SHA/8raw2summary/4核心accuracy同源与真实清理通过。DB新增12表405行，KV521936如实留档；不算原13eb matched增益。owned记录更新completed，当前新gate151230只登记running无结果。


## 最新设备状态覆盖：105930重跑，无新增测试

root明确回执105526 gate exit1/cases[]：归档hash将__pycache__目录当文件，IsADirectoryError发生在候选case前，非候选功能负结果；remotecontrol/evidence.tgz已封存、root下载中，本agent检查本地尚无实体，不冒充独立审。root改regular-file过滤并实测68MiB0%closed后，当前唯一GPU改为`framework/20261021T105930Z-mixed-bucket-row-kv-gate` controller151669，仍无结果。owned queue33/registry旧行已记infra失败，queue34/新行running；registry现59数据行各16列完整。

源码隔离打包还曾因合法内部JSON symlink被预检拒；root仅解引用contained regular-file并留metadata，保留外部目标边界。code/{bucket,growth,hidden-gather}-20261021T105930Z已准备，growth仍无服务或准确率证据。重大经验已同步report，不补新测试；不修改driver/当前source，不SSH/GPU。下一API看本节和root CURRENT最新状态，不能把正式postflight68MiB当当前空闲。


## 最新重大验证：105930门独立通过，110149基点运行

已独立本地审105526与105930原始results/source：前者8源SHA/exit1/cases[]确认仅archive__pycache__错误；后者13源SHA全匹配，M259→384及952→1024有效Attention和整KV、下一32decode/KV皆bitwise/maxdiff0。真实Builder/Impl/writer+C2/C3，bucket._wrap_runner只装CUDA Harness；输入/position尾清零、毒值tail、padding-only RNG和下步unusedoutput均通过。两gate脚本只差两处if p.is_file过滤。independent-gate-review.json分别落各run目录。

重大边界：不是实际ModelRunner或整模型、GEMM/hidden/logits/LM-head/sampler等价；row指padding行，没有hidden-gather候选导入/测试。已纠正ownedqueue标题以免混淆。无accuracy/性能成绩。105930 exit0，fullpostflight11:01:49.406136Z为68MiB0%closed。

当前唯一GPU由root回执为`framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long` runner151990，原080656/16K1024/32req/c64seed721201，新driverbc51ac2d加测前后原metrics和scheduler源SHA，是growth匹配控制；无本地结果，queue35/registry新行running。ownedreport/registry/queue34已更新105930pass；registry现60数据行各16列。全程本地CPU、不SSH/GPU、不新增测试。

本轮最终回报原文：105930真实一层bucket行/KV隔离门独立审通过，13源SHA/两个shape及后继32decode全通过；明确非ModelRunner/整模型或hidden-gather证明。105526仅归档infra错误，raw保留。当前110149原C3匹配基点151990按owner回执登记running，等待raw，不预判收益。


## 最新重大结论与诊断交付（110149/110747/111804）

110149与110747已本地独立审各21/22声明源SHA、同bc51driver、32成功tokens正确；前者220.494323s、后者220.369000s。DB四份实体501表18789行三hash全部相同；KV却521840/521936差96。二者preemption均0→1；growth完整日志只有EngineCore INSTALLED无CHECKED/DEFERRED，判 **not activated/inconclusive**，不报0.057%或任何小收益。独立review JSON落各run；官方结果保持原样。

不能由源码默认值猜实际失败guard。root已读reserveFullISL默认True/watermark0/FullSpec默认字段；仍缺实际EngineCore对象。新增`patches/framework/biv150_growth_descriptor_once.py`最终 **4a6eaefa0b40358307f48c586b9be7dc4a801f4b8eeeda752ff2db5275619b99**，只新隔离诊断source启用，纯transform接growth init d9e2→输出5c11fd1f97057d9a820cb048690a8135bce41fea8d1160127c238653f181e163。守原9245+5源/原ctor；actualctor返回后一次29guard AST逐项值/异常JSON，真实pid/classes/fields。eval globals/locals同namespace防generator假NameError；constructorfalse不捕allocation符合root最短目标。全true时首waiting用weakref定位manager，不依赖growth授权ctx；payload/stats/log异常不阻原allocate，恰好一次原call/异常透传。

framework owner最终独立审4a6e通过；作者pycompile+一个针对性合同过。运行/包装方式与全证据要求写`analysis/2026-10-21-growth-admission-diagnostic.md`。未动在途/原runtime、未SSH/GPU、未新增suite。root负责新copy和--smoke-only诊断。

111804 hidden-copy fixture gate本地8源SHA与四shape fullbits/fresh/RNG、int32dynamic1entry、int64、8fallbacks/crossstream均过；无fullrunner/accuracy/perf，independent-gate-review已落盘。当前唯一GPU按root回执 **112021-hidden-gather-innovation-context16k-long runner155377**，未有本地完成结果。owned report/registry/queue已精炼合并更新；registry63数据行各16列完整。下一操作：root新诊断run JSON到达后只修证据确认的单一scope问题；先看hidden短测结果，不扩大CPU测试。


## 真实V2定位与独立revision2最终交付（最新接续点）

任务仍CPU-only，所有设备及CURRENT由root管理。112603实际JSON与23源SHA已独立核：EngineCore156959/exactbuiltinAsync/use_v2=True；原29guard仅 `not scheduler.use_v2_model_runner` false，28true，setup_errors=[]，DB501/18789三hash不变，exit0/清理11:32:08Z。该smoke实际seed721001，不拿作long性能。110747至此准确判未激活，不能报0.057%收益，也不应重复29条件诊断。

新建 `patches/framework/biv150_growth_admission_v2.py` SHA **72d6f3822c96be028f6ab3cd818de1da6bafdb38d52a50a12633851717332803**；新transformer `biv150_growth_admission_v2_source.py` SHA **e5bad3d863a36d0d24bc3650c513600e23909d2224fb315bb8eb99943f8b0d9a**；唯一必要合同 `tests/test_biv150_growth_admission_v2.py` SHA **2ceeb15965b43ccb60228b07882776b7c31405ef7e68fedc2711b5a70cf0d2a9**。旧9245/runtime、旧105930source、driver/args/env均不改。只接受exact已审builtin Scheduler/AsyncScheduler（不import/支持FL/MTP），新增actualasync整源SHA为第6源、继承/3原method身份、deferFalse guard；boolV2允许True/False。预算、futuretarget、allocate/FCFS/kwargs数学原样，默认off。

实际源码证明allocation与FCFS循环在V2 payload分支之前；Base更新computed，Async更新placeholder+PP1 nexteligible。future max(prompt+合法max_tokens,current+placeholders,computed)仍保守，不依赖V1payload。deferFalse和无connector避免延迟回free误算，原完成/取消/抢占继续live读，无ledger。新合同直接AST执行actualBase/Async两步，computed63→64→65、placeholder0→1→2、future96、PP1cadence及真实predictor页数正确；作者0.016s、framework owner独立0.017s通过，只此1合同/不重跑旧7。两个新模块pycompile和pureinit语法通过。

framework owner终审72d6/e5ba无阻断最短服务，已发root。transform只接受原e043080656init，输出 **830ff5805cb4d989cbc9225ef423720a6e261754ba180d2ca495e76434d7e421**，独立generalhook不叠旧v1/diag。完整审计见 `analysis/2026-10-21-growth-admission-v2.md`，旧diagnostic文档已补真实resolved结果。后继必须真实EngineCore FIRST_CHECKED+FIRST_DEFERRED，INSTALLED不能认定策略启用；marker在负载之后核。未有新accuracy/性能，不继承旧C3结果。

重大独立证据更新（每run均有independent JSON）：112021 hidden22源SHA、真实FIRST_SELECTED、220.357327429s/2527.966764total/32success、KV521936/DB501/18789不变/preempt0→1，约0.06%且KV差不归因；113208 bucket22源SHA、FIRST1696→1792、231.619268445s/32success、DB增加5表137行到506/18926，不冷判负；113946必要warm22源SHA、FIRST、220.390441753s/2527.586930total/32success、DB506/18926三hash不变/KV521936/preempt0→1，旧baselineDB501+KV差，不报增益，保留。上述fullpost分别11:26:02Z/11:37:27Z/11:45:52Z均68/0/closed。

113727/114553 overlap均14源SHA/实际单层backend two-Q立即mainstream消费join/输出/KV/RNG/fallback全过，pending清0。4calls wall省2.498%但event慢；必要64loop/methodv2摊销后wall仅省0.349429%(12.460649→12.417108ms)，event12.409186→12.414136ms基本持平略慢，峰pending9。无硬件并发/整模型/accuracy/E2E收益证明，不服务集成，保留小prototype。完整清理11:39:46Z/11:47:13Z均68/0/closed。

ownedreport/queue/registry已同步最新状态：registry69数据行各16列。**当前唯一GPU为root回执114713-growth-v2-matched-base-context16k-long runner161064**，原080656/bc51/同16Klongseed721201/DB506，完成结果尚未拿到；root准备了 `code/growth-v2-20261021T114249Z`，72d6/init830ff58，未执行。不要把此前postflight当当前空闲，不SSH/GPU。下一操作：root封存新DB506匹配基点，再串行最短growth-v2，核真实CHECKED+DEFERRED/32tokens/preempt/TTFT/wall/DB/KV，只有值得继续才大accuracy/official。我们只按原件更新，不抢设备、不重复tests。

本轮最终回报原文：growth V2已按actual allocation/placeholder/释放协议完成最小独立修订72d6，hook e5ba仅接原e043并输出830ff58；跨owner终审和唯一必要actual-placeholder合同通过。旧版及在途源不变，仍需真实EngineCore CHECKED+DEFERRED。hidden/bucket/overlap最新原件已独立复核并留JSON：hidden无可归因微收益，bucket warm恢复220.390s且新DB506，overlap64仅0.35%单层wall/event持平不集成。owned记录69行同步；当前root唯一GPU114713新DB506匹配基点161064，后继growth必须用新basis。

## 接续：114713基点独立完成，115247真实CHECKED（最新）

root派发CPU-only原件维护；没有SSH/GPU、没有新测试或候选/driver修改。114713已新增`independent-screen-review.json`，独立核21源SHA、同bc51/原SERVER/seed721201/16K1024/32c64、exit0；220.24970296164975s/2529.202048898997total、32/0、524288/32768tokens、meanTTFT62440.319728528266ms，KV521840，preempt0→1。前后SQLite实体506表18926行三hash完全相同且等于113946 after，fullpost11:52:46.493627Z68/0/closed。

**当前唯一GPU改为root115247-growth-v2-innovation-context16k-long runner162380**，sourcegrowth-v2-114249/newbc51/same16Klongseed721201。root原log回执：EngineCore162561已真实FIRST_CHECKED/free31595/future1151，KV521936；11:54:11Z2running30waiting。尚无FIRST_DEFERRED/结果/本地完整原件，不冒充独立激活/性能审计；新的scope确已执行，但是否实际延后准入与收益待真实证据。旧V1未激活问题已定位，不重复fake诊断。

ownedreport/queue/registry现70数据行各16列同步：114713complete，115247running_checked_owner_receipt。下一操作只有等待root封存R2原件后审真实CHECKED+DEFERRED、32tokens/耗时TTFT/preempt/DB/KV/源/清理；基点KV521840与当前521936差96必须列出，不为微小差值归因。hardware+framework在CPU准备actual2D full-visible prefix省mask这个唯一新方向，固定原tile/math；本agent不复制其工作或扫描w16。

本轮最终回报原文：114713新基点独立复核通过：21源SHA、220.249703s/2529.202049total、32/0、DB506三hash不变、KV521840、preempt0→1，完整清理通过。ownedreport/queue/registry70行及handoff已同步；115247仅登记真实CHECKED owner回执，等待DEFERRED和完整R2原件，未报收益或accuracy。没有新测试、诊断或源码修改。

## 最新重大经验：原13eb插件隔离不等于installed依赖隔离

root派发CPU-only原baseline准备审计；未SSH/改远端/动设备。完整读actual retained `biv150_runtime.py` a0c，唯一显式sitepackages源写入为line120 `path.write_text`改Attention，另line123 `shutil.rmtree`删整个parent`__pycache__`；top-p只进程内函数替换，无第二个持久源码写入。actual `iluvatar.py` module-level line258即调用retainedruntime，不能假设仅GPU runner才触发。原baseline期间不可另进程导入retained平台模块。

独立纯AST提5literal（不执行/import runtime），两tunedblock+marker各唯一且marker exactEOF：current54c=41796bytes，反变换仅撤两block+末marker即得bab2，与a4先前独立`.orig`逐byte一致，**actual original41176bytes**（root41166是转录差，已通知），SHA bab2c0b9f9a7793ca411796b48ebb4734433160e7e99eabf46ddb7f1c30cb6e0。身份JSON `analysis/2026-10-21-original-baseline-dependency-review.json` 已落盘。d60/SQL/C2/C3既有pair共享retained54c，不因本发现另失效；原DB/KV caveat不变。候选092944两档绝对结果有效；尚未启动091033原13eb，提前纠正，不声称原baseline已完成。

新建 `scripts/remote/prepare_original_attention.py` SHA **8b3337e06e4dc083b5f99cafd785c6d5a49b64c86a10d721d47c76c304c8eda6**。默认inspect仅读字节/AST+stdout，本地archive inspect及pycompile过；framework owner独立全文终审无阻断，不新增suite，**apply未执行/未Linux设备试验**。显式apply只允许Linux exact regular installedpath，commonflock非阻塞+IPv4/6 9031+ixsmi单卡<=68MiB0%/NoProcesses，备份3源先fsync/readback，二次idle/hash，再同目录temp fsync保mode/uid/gid原子replace核bab2/postflight，manifest含全argv/源与脚本/元数据/原ixsmi/失败。无SQLite/Tritoncache/pycache删除，不自动rollback或删证据。没有改当前source或owned driver。

完整未来命令、reference staging路径、原13eb全树/无retained检查与锁交接写 `analysis/2026-10-21-original-baseline-dependency-plan.md`，report原baseline计划及queue guardrail已纠正：helper释放锁后officialdriver自己重拿，不能嵌套doubleflock；root须覆盖交接不启动其他candidate，验archive/启动后/CSV后bab2。base-revision.txt不代替全树身份，插件隔离不代替依赖恢复。未来candidate自己按a0c写回54c，baseline期间不提前还原候选，更不能当前在途时执行restore。

115247完整原件也已独立实体审22源SHA/bc51/同SERVER+shape+seed；真实EngineCore162561 CHECKED31595free1151future后DEFERRED2702free2722future，原238.11336583085358s/2339.4570819502455total/32-0/52428832768tokens/TTFT68405.78491348424ms，KV521936/preempt0→0。DB before匹配114713after506/18926，但after512/19130，+6表204行/三hash变，不能冷轮判最终回退；fullpost11:59:21.132870Z68/0closed。independent-screen-review已落run，V2审计文档补真实activated结果。

**最后明确owner回执唯一GPU115950-growth-v2-warm-repeat-context16k-long runner163945**，sameV2/bc51/longseed721201，只一次必要warm；暂无本地完成原件。ownedregistry71行各16列、queue47/report已同步。下一API先读root CURRENT最新设备状态；本agent下一操作等warm原件审性能，baseline恢复要等root整卡完全释放且排到原13eb时才执行。hardware+framework继续唯一mask方向CPU准备，本agent不重复造候选。

本轮最终回报原文：已独立确认54c→bab2与a4原件逐byte相同，原件实际41176B；retained还删parent pycache，top-p仅内存。未来restore helper8b3337/defaultinspect已跨owner终审，apply未执行，无SSH/当前mutation；完整命令、备份/idle/锁交接及原baseline验收已落plan和handoff。115247真实CHECKED+DEFERRED并0抢占，但238.113s首轮DB+6表204行，登记activated/coldconfounded；等待唯一115950warm。owned71行/queue47已同步。

## 最新实测终审：warm已完成、restore已实际成功、original官方运行

root明确最新owner消息后立即接续，不回退旧final状态。115950完整run/control独立审22源SHA、同bc51/原SERVER/shape/seed/32tokens；EngineCore164138 CHECKED31589free1151future和DEFERRED2696free2722future，221.23383624106646s/2517.95118443368total、32/0、meanTTFT67130.2737761871ms，KV521840/preempt0→0。DB512/19130三hash前后相同且等115247after，fullpost12:18:37.889080Z68/0closed。对114713同KV描述差throughput−0.4448385%/TTFT+7.5110987%，跨DB506→512仍非严格因果估计；无正吞吐信号，按root不集成/不大accuracy/不再补轮，源码defaultoff及negative留存。independent-screen-review落warmrun，v2文档已补终结判断。

root已把restore完整5原文件与prefix run/control取回。本agent独立审restore并新增 `experiments/dependency-restores/20261021T122607Z-original-baseline/independent-restore-review.json`：actual statusrestored/modeapply/argv，before54c41796B、independentrefbab241176B、retainedruntimea0c三备份SHA+helper8b33都准确；备份ref等a4早先原件，独立AST反变换逐byte同。双idle12:26:07.432605/.533529Z与post.632596Z都68/0/9031closed/NoProcesses，manifest installedreadbackbab2正确，原mode/root:root与所有命令已保留。root实际reference是scripts/triton_unified_attention.py.orig，和旧设计template不同，plan已补真实argv；不再写恢复未执行。

prefix `framework/20261021T121838Z-prefill-visible-prefix-gate/independent-gate-review.json` 已核15源SHA（policy87c6/gated3db/candidatea6d3），两实际backend/builder/writer syntheticcase bits/finite/fullKV/RNG/padding/随机物理页/3负slot+NaN/oneprefill/C2decodefallback全过，Pcase旧prefix复用16blocks，原proxy最终恢复。只P2019/KV16K计时，Q2048仅correctness。32callsABBA复算wall12.594359734375→12.559617125ms省0.27585848%，event12.491010189056396→12.434306144714355ms省0.45395884%；保留小单层信号，无fullrunner/graph/service/accuracy/E2E结论。内部12:19:02Z exit0，完整post12:25:01.258460Z68/0closed。

**当前唯一GPU是root official/20261021T122607Z-original-baseline runner166637**，source091033原13eb、791officialdriver/a4falauncher/原两case4轮/第三marker显式空。root12:29Z启动后只读actual installed及manifest都bab2，benchmark167244/server166651，4K1/4，无BIVmarkers。完整源数量与逐项SHA尚待root最终核，不猜exactcount；没有完整baseline结果或整体增益。严禁本agentSSH/GPU/retained或C3import/reapply，以免污染。本文所有审计只stdlib文件/hash/JSON/只读SQLite，无新tests/设备。

ownedreport顶端、queue49/registry73行×16、baselineplan和CPUidentityJSON、V2终审文档、handoff顶端都已同步。旧“未执行/等待warm”只留历史段，最新以本节及顶端为准。下一操作：root封存original官方阶段证据/完成原CSV后CPU审，最终必须核installedbab2/DB变化/原四轮均值/清理；不混入候选092944绝对结果，更不补无必要的大accuracy。

本轮最终回报原文：115950 warm独立22源SHA/DB实体审完221.233836s，无正吞吐信号、TTFT描述约+7.51%且跨DB限制保留，不集成/不大accuracy。restore现已实际成功并独立审三备份+helper/双idle+post/54c→bab2；prefix15源SHA/两case及0.276%wall/0.454%event小层信号已核并保留。当前root唯一GPUoriginal官方122607 runner166637，启动后live+manifestbab2/4K1of4已确认，无完成成绩。owned73行/queue49及handoff全部同步，不再沿用旧未执行状态。

## 最终对比CPU入口已交付：只在两份完整官方证据齐后计算

root新任务要求精简复用，未动791driver、官方benchmark、任何候选源或设备，也未改report-outline。新增 `scripts/compare_official_runs.py` 最终SHA **e9dc056cee3b0db0f42c153d5321f4eb0d136396187c90acd70087cd4108481a**，217行；一页用法 `docs/official-comparison.md`。

全文读并pin79119f run_official_gate、35d30d run_accuracy_gate、0f2a57 snapshot_tuning_db。三模块导入均stdlib（official仅额外import已pin common），顶层无设备/retained/网络调用；脚本加载main guard不执行、禁pyc写，仅复用validate_outputs原raw8/summary2 gate与readonly/query_only DB指纹，没有复制大validator。stdout JSON，code2pending/1invalid/0compared，不改原CSV/任何源，不加GPU工作。

两run结束exit0/result benchmark_completed+completedstatus/benchmarkexit0/cleanup空后才审原CLI/模型0813benchmark+791driver+helpers/package/Python/Triton/FlagGems/原4轮丢首；全部归档source SHA、固定32GiB单BI-V150每条gpu.csv总量（不把free当total）、原postflight、真实KV与SQLite三hash/表行数。非Attention installed源须相同。baseline必须13eb、bab2、无retainedmodule/hook/marker；root终审要求仅补worker446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64，已读当前manifest确认并加pin。candidate为d60/54c/e155+原init/SQL/C2/C3/top-p/retained core exact。实际DB/KV都输出并保留归因边界。

只给各case原2–4轮Total tok/s均值比/百分比与Mean TTFT均值百分比；TTFT正值代表延迟增加，不发明总体官方公式、不宣称稳定因果/accuracy通过。原base不完整时只报pending缺项且gain_computed=false，没有cases或ratio。

已且仅已跑一次真实完整092944candidate+真实122607不完整base的CPU smoke，code2/pending，列base result.json与exit-code缺失，gain_computed=false/no cases，`analysis/2026-10-21-official-comparison-smoke.json`已保存。未伪造result/CSV、未把candidate当baseline。root随后已读实现并确认安全，只要求加baseline workerpin；按要求没有重跑pending或扩大验证，最终SHA更新如上。完整成功分支还未有真实两份齐的验收，等root本轮正式baseline完成并取回后执行。

当前root最后明确进度12:57Z4K已有2raw/3of4、16K未开始，bab2保持；startup12:39Z225源SHA全pass JSON已本地。原版official122607仍唯一GPU，root拥有四进程；不SSH/GPU/retainedimport。本轮只交付script/用法/smoke记录/handoff，不增加实验登记或改report-outline。GitHub团队交接按root的`docs/team-github-handoff.md`，不等穷尽探索，不擅自发布。

本轮最终回报原文：最终只读比较入口compare_official_runs.py已完成，最终SHAe9dc056c…，复用原791CSV gate和只读DB helper，补baseline真实446fworker pin。唯一真实incomplete-base smoke返回pending/缺result+exit/gainfalse，无伪造或新设备/测试。用法和handoff已保存；等原版完整证据齐后root运行真实分档对比，不算总体官方公式。

## 团队复现说明的一次必要审阅（最新）

root派发CPU-only文档review，原版仍唯一GPU；13:16Z实际4K三条raw/进入4of4、16K未开始、bab2保持。只读candidate-usage/full-package/team-github-handoff及链接official-verification，后读root新technical-report。没有重跑4aba包装/安装/模型/比较，没有修改root README/CURRENT/默认、上述文档或registry/report。仅新增 `analysis/2026-10-21-team-reproduction-review.md` 并更新本handoff。

主要实际缺口：usage顶端仍git am retained/default，而full-package应用完整4aba后又回链usage安装，容易重复patch或复现成旧默认；full4aba是git apply普通diff。建议canonical唯一原13eb新checkout→full4aba一次apply→同一checkout pip install→原命令与真实源/marker验收，历史delta标签清楚不叠加。污染警告目前full-package/team有但usage主入口靠后/缺少，对两个delta“本身不写installed”的说法不能掩盖完整候选包含retained持久写。完整已测环境/Corex/Torch/Triton/FlagGems/SQLAlchemy与源SHA也应统一放入口，旧CPU2.0.43只是历史，不能升级实际服务2.0.48。runtime幂等与Git patch一次应用需分开措辞。

已给root摘要；root明确接手直接修usage canonical入口、旧路径历史标签与污染前置，本agent未动其文件。实际full4aba SHA只读吻合，既有hardware包装独立验证不重复。官方serve/throughput命令齐全且与常量一致；accuracy通过official-verification链接也有完整Level3/API/sampling原CLI，不是缺命令。103/105和3683.65/2729.07均准确标候选绝对/自身accuracy，原baseline pending与无总体分数正确。

technical-report未发现否定绝对成绩/accuracy/包装的实质错误：亲读两official manifest CPU quota600000/period100000均6核；SQL13.405与其中10.780为inclusive嵌套，没有相加；4.97%仍标单次暖控制信号，官方baseline表未填。两项小措辞建议仅落review：SQL反射逻辑不主动改DB，不代表正常调优run不新增表；growth“减少抢占”用控制0→1/候选0→0实际观测表述并留跨DB边界。

新review最后准备baseline完成字段清单：保持registry16列/更新现122607行；完整exit/result/cleanup再改complete；原8raw2summary/请求tokens/原2–4均值、最终源数量+225startup不能代终审、bab2/worker446f/原scriptdriver、真实KV+DB实体3hash/表行数、时间/PID/argv/fullpost、e9dc真实两份比较与percaseTPSratio/TTFT。**没有提前填任何结果、没有创建假result或占位CSV**；如未齐仍pending，旧partial不充baseline。report后继两行绝对+两case对比，DB/KV差异保留，不合总体分数。

本轮最终回报原文：团队复现必要review已保存analysis/2026-10-21-team-reproduction-review.md；主要缺口是usage旧retained入口与full-package回链导致重复安装，root已接手canonical一次4aba路径及污染前置。原官方命令齐全，成绩绝对/基线未完成表述正确；technical-report无实质数据错误，6核quota已核。只备好结束后registry/report字段清单，未填任何baseline结果、未改root文件或新增验证。

## root修订后的入口复读及最新官方阶段

按root要求只读再读candidate-usage新入口：已唯一指定完整4aba/原13eb新checkout、git apply一次、同checkout `--no-deps --no-build-isolation`安装，参考repo只读/new destination明确；历史deltas是alternative不叠加，原命令/环境report/源hash记录相连。主要安装P1已解决。污染约束内容已齐；仅提小排序建议，idle/禁止导入段当前位于安装代码之后，移至首段代码前可避免先复制后读。SQL安装、decode FIRST_SELECTED、mixed仅INSTALLED且不证明everybatch的标记语义准确。未改root文件，不再重复验证。

新analysis review顶端已标“主路径已修”，旧行号/缺口表明确初次快照，不制造未解决阻断。technical-report仍无实质数据/accuracy/绝对成绩错误；只留SQL不主动改DB不等于run不增表、growth计数观测/跨DB不直接归因两个文字建议。

最新root13:24Z实查及本地progress-latest.json：原4K四轮全部SUCCESS、单case summary1905.46total tok/s/meanTTFT12310.56ms，16K1of4进行中，bab2正确。它是阶段证据，不是完整8raw/2summary/exit/清理，不能算最终ratio或套装gain。本轮未更新registry/report成绩，完成字段清单仍仅在review待真实完整原件。原版official122607保持root唯一GPU；无SSH/GPU/候选import。

本轮最终补充回报原文：已复读root新版canonical入口，主要重复安装路径问题已解决，历史路径/三marker语义/原命令及污染内容均正确；仅剩污染约束放到安装代码前的小排序建议。review已标已修/剩余事项，technical-report没有实质数据错误。原4K已完整但16K仍1/4，只记录绝对阶段进度，没有提前填baseline结果或计算gain。

## 冻结后的既有收尾：最终取证文件/字段已准备

按用户停止新增探索的范围，只修改owned queue顶端，明确覆盖所有未开始pending/CPU-device建议与历史partial重启；只有root已经在途original122607可继续，已有CPU材料及最终必要audit/registry/report可收尾，不新集成/新GPU/新accuracy/新scan/重复smoke，GitHub只准备材料无推送/对外消息授权。root14:45Z最新回执16K2/4、5raw/1summary、bab2正确，尚无完整baseline。

仅本地读e9dc比较入口与原791/35d3/0f2a，新增 `analysis/2026-10-21-original-baseline-final-evidence.md`，逐文件列result/exit/finished、原8raw2summary、final manifest/原command/source、DB双快照实体/命令、GPU全采样/日志、PIDs/model与正确字段。不改任何脚本/官方源/结果，不运行远端或GPU，不重复现有review/测试。

已向root提示两个关键证据缺口：原791只自动写result.postflight(端口/free>=30000)及benchmark_source_after(RUNS/SKIP/benchmark字节)，**不写完整GPU利用率/空进程表，也不核结束时live Attention**。e9dc明确需要run/postflight-full.json，port_9031_closed/memory_used_mib<=68/利用率0（gpu_utilization_percent或utilization_gpu_percent）；总量从gpu.csv32768MiB核。建议root另保存control/final-source-review.json及run/postflight-sources/最后实际Attention字节：archive/live失败清单、actualsource_count、live/archive/copy三bab2、实际source_dir worker446f、benchmark0813/driver791、无retainedhook/module/marker与UTC。只用固定路径读字节，不能import/find_spec父包触平台。225startup不替终审；现有比较器只查archive，不替远端after身份。

清单规定等driver自己的finally停四进程/DB-after/写exit完成，再补fullpostflight与live source证据、封存整run/control/source/DB原件/恢复备份，归档SHA+成员清单与下载本地核同；不把monitor正常−15当失败、不强制不同utc调用的start微秒相等、不在候选写回54c后才采baseline after。完整取回后root再派既有终审/e9dc真实两份比较；目前不运行该比较、不填最终registry/report值、不合计分公式。

本轮回报原文：queue顶端已明确冻结所有未开始项。最终取证清单已保存，特别标明791不自动提供完整postflight或live Attention after证据，root需补run/postflight-full.json和最终source-review/原字节；准确字段与取回顺序齐全。原版仍16K2/4，仅等待既有任务结束，无新探索/测试/远端/GPU操作。

root随后14:47Z更新为6raw/1summary：16K第二轮128请求全成功、2585.11s，已进入3/4、bab2正确；queue冻结顶端与final-evidence介绍已同步阶段状态，仍无完整结果。按root要求清单明确两manifest CPU quota600000/period100000=6核；两run初始DB不同不能称cache-matched或清库对齐；实际KV分别读两份完整server.log，不抄相邻短测/默认值；最终两case原2–4描述比率不合比赛总分。只改这三份本地文档，没有运行任何远端/模型/测试。
