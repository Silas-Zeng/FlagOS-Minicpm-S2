# 框架预算筛选与新增互审交接

2026-10-23。此前完整工作保留在 [systems_innovation.md](systems_innovation.md)；本文件仅接续当前 CPU 预算筛选，不复制旧报告。root 独占设备；不修改 registry/CURRENT、原件或 GitHub。

## 本轮现成证据与决策

| 证据 | 实际预算 | 可支持与不可支持的结论 |
|---|---|---|
| 104544 / 104920 输入准备诊断（6f 组合） | 4K 部分快照256步：等待1.858095ms/预处理4.553461s；16K部分快照2048步：等待14.059984ms/预处理14.488007s，分别0.0408%/0.0970%。 | 原prepare event等待约7us/步，暂不支持移动同步。整个prepare含其他准备，部分窗口混有不同阶段，不能把平均17.79/7.07ms称当前纯decode关键路径或可删时间。原件索引见registry及team/methods/input-prep.md。 |
| [单 computed H2D 服务pair](../../analysis/skip-computed-h2d-service-pair.json) | 215040→215331，同KV521840/DB540，30项比较通过；36.683611→36.457831s，总吞吐单pair+0.619291%，TTFT−1.026463%，TPOT−0.053834%。 | 证明源级消除无消费提交值得保留，但只是单pair，差主要对应TTFT；不把0.619%当稳定每步CPU比例，更不与其他候选相加。 |
| 192308当前Q/GQA恢复窗口（tmp/q-gqa-resume-native/192308-analysis-endpoints.json） | 可见kernel跨度2855.519772ms、区间并集2807.461640ms，未覆盖48.058132ms。 | 图节点完整性未建立；48ms不是已确认CPU空泡，也不能全归victim。425恢复已另测，不能拿原重算预算重复报收益。 |
| 旧061506 allocator cProfile（framework既有交接） | 8步480次allocate_slots累计11.557ms；predictor2.922ms、allocate_new_blocks2.954ms为其嵌套项。 | 只能提示重复调用入口，不是当前422开销预算，不能相加或外推到168秒服务。 |

当前没有新证据支持“已定位主要host瓶颈”，因此不扩queue3、同步移动或线程重叠。尚未测试的单点候选是普通MiniCPM路径 `_prepare_inputs:2141` 的 `num_accepted_tokens.gpu.fill_(1)`：已有framework消费者审仅发现spec/hybrid/Mamba消费者，当前常规text未消费；保持CPU fill、原buffer/事件，只有完整消费者与fallback证明后才考虑删除该GPU提交。它有可删工作的机制，但无独立时间预算；本轮不实现、不与已测H2D或allocator叠加。framework确认未见该点后续实施/否决。

hardware补充host pinned slab：两次SAVE的cgroup增量约1.415GB、payload约718MB，可能与42×32MiB分配粒度一致，但实际Corex分配器未证实；现headroom约10.8GiB，slab不减GPU KV/传输、亦无alloc-time分项，不能认收益，不另扩诊断。

## 当前下一步

root已批准framework独占 `tmp/next-kv-noop-allocate` 做普通decode无新增页/完整hash时的最短CPU判别。本人只审其原方法来源、完整guard与计时是否包含全部新增成本；hardware主审页/hash/placeholder和empty对象语义，彼此共享风险而不重复测试。CPU无净省即停，有净省再由root决定当前422最薄服务门；无SSH/GPU、无新算子。

425 pitched FULL最新性能pair仅same_KV不一致（521840/521936），其余31项中的30项通过，gain=null；不扩大或继承422 accuracy。425 reader的SQLite修复 `d45de2f8…` 已获hardware增量静态通过，root实际验收结论见CURRENT和原分析，不在此重复运行。


root为CPU准备期安排的baseline-only launcher `tmp/allocator-noop-baseline/launch.sh` SHA `f480ab0d1c8f4c582b967804c437536621eac91a1ddb54642204011192f63de8` 已全文及七处生成替换只读审，无新增阻断。固定旧422/82514完整map及213134来源，只切baseline选择、decode4k和run标签；原bc51/SERVER/seed721201/VERIFY0/finiteunset/Qartifact、双栈即时idle、driver锁/占用检查、DB与PID owner保持。未跑旧门/脚本或设备。4K短负载不保证SAVE/FULL触发，后续reader不能照搬长负载“必须有恢复事务”的验收前提。


追加同一192308摘要的预算约束：`fill_scalar_func_kernel_rank_1`共7次/0.026052ms，均3.7217us；虽与7恢复步相等，缺operator关联不能确定全归accepted fill。该单点若后续可行，主要假设是省host提交入口，现有GPU时长不支持“大收益”判断；Other类101.203348ms含1253个不同kernel，不能统归metadata。未重跑trace/设备。


allocator CPU稿fc410a4a/helper、abb0a7fb/check、e876f792/receipt已只读增量审来源与完整guard计时，无阻断。首稿32批thread_time判据存在Windows量化问题，已与root指出并改为2048批ABBA的perf_counter wall中位数，thread仅诊断；ClassDef decorators/页边界/kvgroupid三次纯fixture前置失败由作者保history，均在有效计时前。N30/31/64原链约107.927/114.393/231.233us，对候选32.339/37.409/69.438us，省75.588/76.984/161.795us，热guard/kwargs/property/count全含；仅本地CPU片段，未验证生产构造或GPU，新页/hash测试只到原写入口即停。root已准固定422→423薄服务，对既有225044基线；本人下一审生产scope/install/actual marker与launcher，hardware主审allocator页/hash/placeholder/empty语义。没有重复跑CPU合同/旧门或设备。

423生产接线新增只读审通过：helper `7393aa23cbef2c795faed23e32504a028ad1a867226089c45ad5c43026a9f3e9`、preparer `a8264488f522c88da237eeee7d9f9c216b6a50b73374921e411db2495e62e7d9`、最终launcher `72f82a7c12b48e9ef4bb0b851b7c7d36121fd8bba42c19073c0500934036bdd7`。原422 init的protocol安装后才追加独立helper；完整map只增helper/改init，runner、SAVE/FULL、算子不变。首次Core入口只读自然加载来源与模型/Full/Async/UniProc scope，原Core在观察except外恰一次；root指出的缓存bound `engine.step_fn`风险已修为双identity归还实例入口和类属性，首多请求selected_delta后撤观察，异常不重试。hardware另审页/hash/placeholder语义，本人未重跑CPU/旧suite或设备。

新launcher保持原bc51 decode4k/seed721201/VERIFY0/finiteunset、即时idle及driver唯一owner，并在启动前核225044 baseline前后与candidate-before DB三SHA。初稿f422使用ARMED作启动门；作者发现bc51在smoke前检查marker，而ARMED要首次Core step才发生，故最终72f82只将启动marker恢复原`BIV150_KV_PROTOCOL_INSTALLED`，reader命令契约无需改。本人初审将该差异只看作后验契约，遗漏此时序；最终单词修正已确认。`ARMED`只代表安装，后验仍必须同Engine多请求`FIRST_SELECTED`及完整原件验收；不能宣称GPU完成或全程覆盖。最终KV、candidate-after DB及服务收益仍待实际配对。

root已收423实际配对：225044→230741均64/0，36.510462→36.839126s，但KV521936→521840，31门仅same_KV不通过、gain=null；真实多请求命中成立，仍不默认集成，原件和CPU代码由root封存commit `3dbc9c3`。本轮不重验原件。

已验422完整官方测量薄接线 `tmp/q-gqa-kv-official/launch_q_gqa_kv_official.sh` SHA `c720998168374ea4b8a96f89b6aad010b3b26a56dc291e8f56324a71c9465f02` 新增只读审通过。相对旧815f只改固定213134的422源/map82514、唯一official/control标签、accuracy215836引用、显式VERIFY0与KV安装marker；完整源复制前后map闭包保留，原79119/35d owner、锁、端口、清理和6h上限不变，原0813两case×4/原SERVER/第2–4轮均值不变。未执行脚本/旧门或设备。启动标记不是实际覆盖，完成后仍核同Engine Q/GQA、原协议事件、源与DB前后；只报422绝对吞吐/压力表现，不与不同DB的旧414算因果收益。root为唯一设备owner。

其后继封存脚本 `tmp/q-gqa-kv-official/seal_q_gqa_kv_official.py` SHA `d9a363ee14e4f5172b7df23c7e055f277ad76a1e272ee624def8e98e6dc773d8` 窄审通过：直接diff原bf2ec87c仅固定真实`20261022T231746Z-q-gqa-kv-swap-official`、422源/map/launcher身份、VERIFY0 argv、KV marker、归档文件名和独立accuracy引用。旧八行CSV/两摘要/第2–4轮均值及CSV SHA、实际Q/GQA、DB完整性、源/installed身份、owned PID/双栈端口/idle清理判定均未改。未执行main、CSV validator、旧测试或设备；此静态结论不提前认定仍在运行的官方任务完成。

231746导入器已准备：`tmp/q-gqa-kv-official/import_official.py` SHA `abd7f79b71f31d3dc6fcc92a80359e23f8eff5288a37312b2ad727483c93175b`。只固定该run并给Windows cwd加既有extended path兼容，逆去两delta恢复旧`8c0eccbc265baa94c703a1c635c6b07e43bff94b62f72174a027b06c245a783f`全文；仅compile，无导入/CSV重验。保持size/SHA、路径/类型/重复、`extractall(filter='data')`、完整inventory、exit/result和原validation。CLI仍为`python tmp/q-gqa-kv-official/import_official.py 20261022T231746Z-q-gqa-kv-swap-official <bytes> <sha256> <sealed_count>`，数值须由root真实封包回执填，不能预填。

后续host-device筛选只复读现成192308摘要：恢复mixed段可见跨度2.85552s/并集2.80746s；48ms未覆盖不是CPU空泡证据，图节点完整性未知。N2尾部21.15ms/计数步与N1含shutdown的27.89ms不能相减归因。结合约7us/步prepare等待和allocator仅CPU局部省，当前仍不支持单独占卡补泛化host诊断。先收231746绝对性能及压力；若需进一步定位，现有证据缺的是稳定puredecode窗口同一时钟下的CPU API提交与实际graph/GPU活动对应，不是再宽扫恢复段。无新实现、测试或设备动作。

root随后要求先补工具可行性。最小只读SQL发现旧042609已有5条独立GPU `cuda_graph`与5条`cudaGraphLaunch`按pid/correlationId一一对应，graph.ts−api.ts等latency；均约80ms的GPU duration不等API时长。042609/192308的clock_snapshot均含MONOTONIC→trace ts映射，旧offset280–573ns/135–641ns、BOOTTIME offset0，ixsys均V4.4.0。192308既无graph也无GraphLaunch，故仅混合恢复窗口无法回答当前纯decode问题；这一新证据支持一次窄诊断，不需要graph内部节点完整性。

经root批准，CPU准备 `tmp/q-gqa-puredecode-native/`：helper `637550a0a3b850422127700d7ea6ce5983678984078f636cae079f8f7bed772b`、preparer `f88182a215ab66e90c5fd44b332d582084220466e1c28e082767964fb026ab10`、driver `4fc1ae7e9f76cf1e63b4ab2560e0059b55df5b5dccf754a2655f79531058fd6b`、launcher `a634ea7d2861ebf997005ec7cb7756d99cb66e149e0d117b07034343cbf4cbe8`，六部署件完整pin见preparation-check。不能旧footer追加runner，因422原协议强核cc442；改用原7393冷scope/首Core双identity归还模式，只init+独立helper，422→423诊断源，runner/protocol逐字节不变。两次稳定同reqIDs资格后采唯一8次execute+sample CPU端点，第9入口按旧native边界stop；失稳只mixed_abort、不重新选窗，waiting unknown。原owner除validation块外逐byte同c0e，原longscreen/seed/SERVER/单owner不动。仅compile/fullinit/actual输出字段AST/Bash-n通过，无上传/SSH/GPU/旧suite/整源复制。

附带29137薄CPU metadata plan计数经framework收窄：冷核单attn_group/实际Triton，只读首metadata；8步窗口和普通q1不扫offset，窗外每64execute稀疏partial，shutdown有则末次。q1不等确认decode、plan不等forward，unsupported/错误/覆盖边界明示；long1024单波的0遗漏不外推官方多波或旧128out。起止边界排空queue2与disabled-Q闭包会影响诊断，CPU return不当GPU完成，图间隔仍含sampler/metadata/kernel/memcpy，不能直接叫idle。hardware独占同目录离线reader；最终新原件须重新核时钟及完整相关GPU intervals，当前尚未运行。

framework已对上述最终637550a0/f88182a2/4fc1ae7e/a634ea7d新增风险静态终审通过，无当前部署阻断；复用源/owner旧结论，未再运行合同、程序或设备。root已收ready，后续只有root可上传/串行启动。

一次依赖队列 `queue_after_official.py` 初稿535e6d32仅等待231746 exit0，再运行已审d9封存器，成功后调用a634原launcher；双次pin、同目录started-once、串行调用及无重试静态通过，未执行。建议root只补exit0后固定官方PID382479最多60s的/proc消失/Z等待，避免exit-code先于最后进程退出导致sealer安全拒绝；其余PID/idle仍由原sealer核验。派发后receipt/state写失败不能反推子任务未启动，应读保留stdout/PID且禁止自动重试；不新增GPUowner或设备轮询。

队列最终 `4f020e5bfa618e481b82ff6079054f51643ce212bff6d59ed61e78d36e34123b` 已按上述建议补固定/proc/382479/stat等待，新增14行只读审通过：消失/Z放行，60s超时或其它读取/解析异常停在原failed路径；不重试封存、不新增设备轮询。原双pin/封存成功/唯一launcher顺序不变，未执行任何脚本或设备动作，由root唯一上传。

root队列PID387488等待官方时，CPU准备唯一薄摘要器 `tmp/q-gqa-puredecode-native/summarize_mixed_coverage.py`，SHA `cf551ca342d5d0634fdeebcf8d81eb3d2c078ce7a929f86c6f0b70b8ef805a4b`。现有native reader不导出coverage，故该入口仅读新run的native-events.jsonl最后一份累计快照，不叠加partial；六列N/M/Dall/Dprefix/outside/plan_prefix_tokens配频次，保metadata合格、unsupported/error/skipped及末次execute范围。outside比例按Σoutside×频次/ΣDall×频次，另列未入plan比例；无样本为null，无K加权、非forward/性能，1024单波零遗漏不能否定128或多波。仅compile，未运行分析或旧测试；原件回来后使用`python tmp/q-gqa-puredecode-native/summarize_mixed_coverage.py --run-dir <实际目录> --output <新JSON>`，新JSON独占创建避免覆旧。

cf551ca3由framework按实际637550a0输出schema只读互审通过，未运行数据。官方717原件下载后，旧abd7导入在Windows tarfile.extractall混合分隔符目录stat处WinError123中止；原包/远端不改。root派生`tmp/q-gqa-kv-official/import_official_longpath.py` SHA `dc34b8808816574b1c7084212ee7cb4f9c0f6a5b798864f475f0680939f0c9dd`，本人窄审相对通用d3aa仅ROOT层级、official目录/固定run/禁止controllerseal、result.json及原validation输出；逐文件parts join、安全成员/完整seal/sizeSHA、已有不同字节拒绝覆盖、独占新建及最后完整集合hash核对保留，无删除。未执行新导入/reader；root在不完整导入后先运行的16链事务结果须等全717封存通过、输入logSHA一致后才能复用，不以先行PASS替代完整原件验收。

002156原长输出诊断root初验exit0、8CPU步/8graph；其完整覆盖原件尚未取回时连接publickey被拒，只有root处理连接。按root授权仅CPU准备独立`tmp/q-gqa-mixed-coverage-only/`：helper8c5b1e2d、footer75f43944、prepare4002824d、launcher1739c232、map82514，完整pin见cpu-preparation.json。原637550a0没有计数模式，本包显式白名单在第一次安装前核mode，沿冷scope传递；mixed_coverage_only跳profiler资格/起止且不装sample wrapper，原metadata计数不变，422→423只init/helper，cc442/911不变。直接原bc51 context-screen16K/128/c64/32req、seed721201/原SERVER和owner，独立events/Qartifact、VERIFY0/finiteunset，无ixsys/trace/新增CUDA同步。仅精确逆回、compile完整init/2heredoc、Bash-n；没有运行框架、源copy、模拟套件、SSH或GPU。hardware受托只审新增mode/launcher；root拿002156全量覆盖再决定是否启动，本任务静态收尾后停。

hardware已对8c5b/75f4/4002/1739新增mode与接线只读审通过，无阻断。随后root于00:44恢复SSH并取回002156全部490原件（tgz3002843B/SHA前缀a9514412），两reader各一次完成；本人仅读保存JSON并按授权更新registry既有行186与CURRENT开头，不重跑reader/原件检查/team。native完整8CPU/8graph；mixed末次2109execute/252mixed，4032个q1中outside及未入plan52=1.28968%，不是此前局部hist误判的零遗漏。DB前后554/20517三hash不变。随后短覆盖上传SCP累计三次公钥拒绝，005000Z仅目录标签、非实测时间，远端只有空目录且未上传/启动；继续由root处理，无替代连接或排卡。hardware汇总graph中位52.3947ms，下一图已提前50.798–51.199ms提交；五gap2.0620–2.1179ms，可见GPU1.9035–1.9332ms（sample0.8775–0.9006/LM head0.9293–0.9420），未覆盖0.1582–0.1985ms不称idle/收益。已同步两处接续，不支持由本窗口再猜queue3/提交空泡。

root新增原422短baseline编排 `tmp/compute-order-owner/launch_baseline.py` SHA `90554d08b1a274458e355ad7c7da739740c52da0a5045aee48eea16757447abe` 窄审通过。全422map对82514资产及213134原reference，源码归档前后闭包、DBbefore、原bc51/快照脚本pin、BI32GiB/68,0/无进程/双栈9031空闲均保留；仅原context-screen16K128/c64/32req/seed721201，VERIFY0/finiteunset/绝对Qartifact并拒残留诊断env。只Popen一项交原driver持锁/清理，不自动candidate/pair；PID派发不等终态成功，后续仍核候选源/DB/KV可比性。未运行脚本、测试或设备，未碰作者tmp/compute-order实现。

候选编排 `tmp/compute-order-owner/launch_candidate.py` SHA `995d27bc3295bd54d90a213aeb94b0cda072c0f9b3d5f718adf8f8301056699c` 只读窄审通过；prepare_candidate_launcher九处替换/逆回90554与check.json一致。只新增冻结b1a804 builder/5ce6 helper、全新423副本及四路径变更、ea64 runner锁、候选标签与准备归档；builder完整模式CLI/receipt output_map/源码与归档map闭包已核，原bc51/SERVER/context-screen/seed/DB/Qartifact/VERIFY0及唯一owner复用，无自动pair。root说明实现已由另owner作6+2门；本审核不重复执行。真实32/0/命中仅集成和短筛信号，不继承422准确率，收益仍需实际命中及同DB/KV等配对；未执行任何builder、launcher、测试或设备，未改作者候选源码。

054306→060425配对reader已准备于`tmp/compute-order-owner/compare_service_pair.py`，最终SHA `e3ae768c5fe251c3a634472fd86871e536ec3cd835aae6047e18be09dedb7961`。复用noop模式的8c0→03e全部20公共可比门，只薄改context-screen目录/标志和32/16384/128常量；新完整423map来自冻结87af19c9的files-prepare.json，核四路径/准备归档、同Engine FIRST_SELECTED/forward返回/N等sampler_rows/NONE/原请求序声明及无SCOPE_REJECTED。原Q/GQA、DB四端、KV、SERVER/负载/CPU/外部源码/后态清理门不放宽；任一失败gain=null，新runner不继承原accuracy。初稿cc6df34c误假定owner目录有base-map；root指出后改直接复用compute-order现有82514，并将marker资格收紧0<Dprefix<Dall以匹配helper。仅源pin、脚本与动态库定义compile，没有读取实际两run或运行compare/旧suite，receipt在pair-reader-preparation.json；交hardware增量只读审，root唯一运行。root已知两run各32/0且DB554/20517稳定，但KV521936→521840失配，不重启凑容量。

最终e3ae由root作为另一owner全文新增静态审通过，包含上述两处修正；取消额外第三层互审，保持冻结。root负责唯一真实pair运行，061500准确率另由原35d/root单卡执行；本人未读取实际pair或操作设备。

root唯一执行e3ae后，仅读保存的`analysis/compute-order-service-pair.json`完成阶段登记：31项30真、仅same_KV false，gain=null；两侧32/0，候选99.536272152s/5308.456792453对基线104.312939462s/5065.373507102，表观+4.7989%不能归因。追加registry登记#188（060425），方法说明同步保留候选/失配证据、061500准确率pending且不继承，build_team_view只生成一次，188登记/185run。未重跑reader、原件核验、GPU或Git发布，CURRENT/AGENTS由root处理；reader保持e3ae不变。root按新协作要求将本组baseline/candidate及失配结论批量更新实验PR，代码PR独立。

accepted-token GPU fill独立原422候选新增窄审通过，无当前设备短测阻断：preparer `410b2c6e07018e745406cec62213fe982945edc6a29c599e3d3696bf6ff4c043`，runner `03a0e007e820644d55ac5eaf3331416da3fb0e58147a4f57928d363cc8ff6fb2`，worker68def179/protocoleab62b84仅重定runner锁。实际GPU accepted消费者只在async-spec correction、spec Mamba/GDN metadata、hybrid后处理；冷scope排除这些配置，原CPU fill、buffer/地址/event保留，0e/1bb/KV协议和worker无额外accepted消费者。ctor False，原KV初始化成功末冷核；profiling/未知/冷检查异常False，固定Engine配置内热路只cached bool，dummy不走此prepare。仅静态读新diff/消费者并核三源SHA，未运行新旧suite、框架或设备，也未改作者文件。ENABLED只冷资格，同Engine其后既有CPU_METADATA_FIRST_SELECTED才佐证实际prepare经过切口；不当全程/GPU完成/数值/收益，热bool净成本及实际启用待root最短设备验证，不继承422准确率。
