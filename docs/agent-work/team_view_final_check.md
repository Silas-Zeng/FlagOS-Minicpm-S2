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

accepted-fill最小owner编排已在`tmp/accepted-fill-owner/`完成：launcher SHA `e972c800915a319acbd29823e13abb590e56ced8f584bbf4fa2ddfe15c3a7960`，emitter `f7256df469309cb8260edd0b268f4c9dd53535a215cc25c9feeba551cdf88aa6`。复用原995d/bd0076，仅9/4处冻结资产、标签、422三路径pin与比较限制替换，完整逆回逐字节相同；语法通过，diff与owner-preparation.json留同目录。builder410b/base-map82514直接读取作者冻结目录，未改候选，未运行builder/emitter/框架或设备。原bc51/SERVER/context-screen/seed721201/单卡与端口即时检查/DBbefore/归档/VERIFY0/finiteunset/Qartifact/原owner清理全保留，不自动pair。054306只参考，DB若变化由root另排基线；冷ENABLED与真实prepare路径后验、可比性和准确率边界仍保留。已交framework仅新增diff只读审核，root唯一后续部署。

framework已对e972/f725实际SHA与新增diff只读封口，无当前短服务接线阻断：422三路径、原参数/owner/DB/归档均保持；未运行builder、emitter、旧门或设备。仅CPU资产ready，部署与新DB/KV可比性仍由root统一判断。

独立computed H2D方法PR材料完成于`tmp/computed-h2d-pr/`，仅本地未发布。GitHub CLI只读固定框架main9a43eb1/tree2b59d761（#12 GQA/#13 C500已合），runnercc7f和CPU metadata0e961实核；原23d三段迁移后runner `195cc806a127ab4e43b6838aaee70ef70a4d8b2f02dd38df6f0e815374202b88`，仅一文件。当前全部类方法AST同受测cc442、候选prepare AST同97f41，逆回精确恢复main其余字节，语法通过；没有强保旧整runnerSHA/覆盖队友树。manifest4f7213a5、中文PR.md4e2f9519及method.patch留身份/依赖/旧215040→215331可比30门和+0.619291%单pair。只读保存分析，未重跑reader/方法门/设备/accuracy；新main整树未测。原helper没有vendor开关，因此C500可能也符合scope，Draft合并前需其负责人确认；不修改#14。发布由root按最新main局部应用，不自动合并或force。一次静态生成类名误写在输出前失败，修实际ModelRunnerFL后完成，细节仅README保存。

framework对computed-H2D PR迁移已只读复核实际AST并通过：maincc7f全部类方法同原cc442，195cc806的prepare同受测97f41，仍仅该方法三hunk；C500无vendor开关的合并前确认边界保留。未重跑测试/设备/网络或改文件。

计算序辅助答案门新增窄审通过，无当前运行阻断：`tmp/compute-order-answer-gate/run_answer_load.py`6dafbfbe、owner9b6453df、launcher19853b1f实核。32条固定tokenIDs/16384、temp1/top_p.95/max128/ignoreEOS/add_special_tokensFalse，无request seed；CPU prompt seed不传采样器。逐条保存原请求响应，首完整answer tag真值及usage16384/128全过才接受，错误不重试；candidate只取本负载前后新增合格FIRST_SELECTED，pid来自冻结helper的os.getpid()，原单请求smoke不符合mixed资格。原bc51只新增CLI和替换一次load，finally清理不变，没有生产源变更。只读客户端/新增diff/必要相邻出口及实际SHA，没有运行client/tokenizer/owner/测试/设备。限制：marker在forward返回后、sampler前且无rid或输出token位置，部分首tag可能早于命中；32答案+至少一次命中仅辅助事实，不能证明逐请求逆映射、官方accuracy或性能，baseline自己不过则inconclusive。已将明确通过与限制交root/作者，不扩关联实现或旧门。

compute-order shadow新增预审：实际Attention3414在direct/custom-op两路均用kv_cache_dummy_dep保证每层writer→attention，不能据此省去物理slot证明；须本步写slot唯一且不交任意请求旧prefix。root明确允许原序_prepare_inputs+forward后P重新prepare，不重复_update_states/sample/history。窄读ea64实际prepare/inputIDs：strict noSpec/noMM/noLoRA主路径只重建staging，prev_sampled_token_ids/prevmap只读、prev_positions自身缓存重建；需shadow logits.cpu()完成后再重用host staging，原prepare event域保持，并排accepted-event/embeds及KV scales首次校准等副作用。已与作者/root对齐，代码尚待落盘，当前仅机制预审而非可部署结论；不重审旧门/不GPU/SSH。

跨职责新增只读审通过（team_view_final_check）：helper `90ad14d1b9696c6d8a801b7e30d3c2aec615ef40c7f76bc00bf42d0be906d705`、runner `f8b0a5212786d7d6f2cea1d84f1eaabce7ccea2b714c3b4454fc12f07236f8f8`、preparer3df35；root薄owner b5fc218f/部署76985匹配同424五路径。初稿两个属性名会令资格提前unsupported，已修为真实TritonAttentionBackend.forward_includes_kv_cache_update与impl._kv_quant_mode并锁backend身份。逐物理token mask排当前slot重复及任何旧prefix相交、两序实际slot D2H、42层非alias/非校准、shadow logits阻塞独立CPU快照后才P prepare、原event域与上一轮sample只读均已核；dispatcher/状态更新/采样/history没有第二次，生产异常不回原路重试。finish比较FP32快照的int32位模式并保存原始误差，发生在ExecuteModelState/采样前；原owner参数/锁/清理不变。可安排一次短诊断，但首次未命中或unsupported不算覆盖，completed不自动等价/accuracy，额外forward/同步不作性能。此次未执行任何新旧套件、模型、SSH或GPU。


075210 shadow数值差异独立CPU排查：原件result显示N17/M2048，q=[1,834,1×14,1199]；原GQA行0和两prefill行1/16逐位相同，新转GQA的14个outside q1全有差异，5行top1不同，max11.828125/mean0.672828。窄读冻结5ce6/90ad/f8b0的Plan逆序、原请求prevsample scatter、双prepare和metadata链，暂未发现确定映射或重复状态更新错误；prevsample/prevmap只读、原logits阻塞完成后复用pinned、所有写slot与旧prefix不相交均保留。仅只读两个原npy计算17×17 MAE，差异不呈一致的另一行排列，不能据此排除输入值错误。最需区分的是14行首Attention输入/metadata是否同值，还是原Q-hoist 2D与新GQA输出分歧；当前slot证明不覆盖inputIDs/seq/QKV，不能先归罪某算法或放宽容差。actual3414 custom-op在774动态调用实例impl.forward，支持只第0层原callee各一次的薄观察，锁实际对象并identity归还、不改compile/graph/采样；由作者准备新probe，未运行任何新GPU/旧suite、未修改原件或候选。


新增只读互审已完成：helper `d958a1b660dc643ccc63b49e00e7bae07edfee52ee3dae3ffc34c71177172254`、`files-final` runner `af830c1e971f0f040afa03134329e55034463c2c0e36e2f47ae3bc84abfe287a`、preparer cd3475ac、receipt 9a85f079；旧files初稿不部署。actual3414 custom-op动态impl接点、staticcontext实际第0层对象/原a129 bound、原请求q1行对齐与实际input/position/QKV/seq/table/slot/output快照均核。初稿phase0后异常归还缺口已用两phase各forward外局部try/finally修正，原callee各一次、无采样或旧路重试；Q/GQA计数字段与当前源一致。当前可进入一次短诊断；新增gather/D2H同步可能掩盖时序问题，首层相等不代表后续层/全模型等价，不改容差或称性能。只静态新增风险审核，未运行合同、模型、SSH或GPU。


082246新增证据由root回报：15个q1的actual input/position/QKV/slot/seq/有效table逐位同，首层Attention输出最大差0.05712890625；原route Qselected0/fallback1/GQA1，P为1/0/1。这里原outside实际走未命中Q变换的2D，P的Qselected属于prefill suffix，不能归给outside。独立复核actual writer f18224（tmp/remote-source/bucket-support/triton_reshape_and_cache_flash.py）的native BF16只按slot分解写mask内两头256维；3414保证writer→attention，当前slot不碰任何active prefix、42层pool不alias且首层当前K/V同，未找到会改这行历史prefix的实际源码反例。因此赞同最小一次P首层callee后选本次最大差outside行、沿actual页表/seq抓完整约17MB K/V，以受guard的writer不变性作两相共同上下文，再做独立CPU FP32 oracle；不抓15行/42层，也不把P回读写成原相实拍。仍不能外推底层硬件无bug、后层/全模型准确率或性能，不改容差。作者在独立tmp/compute-order-oracle-gate准备，本人只读源码/协作，未访问设备。


单行oracle新增窄审通过：`tmp/compute-order-oracle-gate/biv150_compute_order_shadow.py` addebb0c21e48e1ba72be63504e9f823f46607cba032410e1c04bc5410ac95c6，CPU reader 7205b95ef183cad52ef456e9b47ae4b1dd23a4c5a6a470ee88d5265e0eb6f943；runner af830/builder cd347与082246不变，实际receipt完整424map仅shadow helper一项差异。动态在outside q1中按本次Attention输出最大差选一行，先要求全q1实际输入/QKV/slot/seq/有效页表同bit；actual页表按seq取完整页并CPU按K/V页内顺序截断，检查末slot与cache末token等于已观测K/V。实际scale/16Q2KV128及全因果无窗口/softcap/量化等门匹配；NumPy按h//8的FP32 QK→稳定softmax→PV独立于待疑kernel，BF16原bits转换正确，可选FP64仅稳定性参考，无通过阈值。单P相/条件共同上下文标志与原hook finally归还保持，无当前一次短诊断阻断。只读新代码/receipt/精确SHA，未执行reader、旧suite、模型或设备，不改原件或作者源码。


085500后独立P主线判断：不再以原2D逐bit相同作P正确性门。已可复用actual outside input/position/QKV/slots/seq/有效table同bit、Plan逆序与原N logits/sampler顺序、单次采样/history更新/strict fallback及RNG证据；单行GQA更贴FP32也只定位该首层现场。仍缺新路由真实作用于多步答案的语义证据，061500的0P覆盖和070816基线4/32均不能填补，whole-M结构门同样不能替代答案精度。唯一建议的后继短验证：固定少量（例如4题）原Math500真实题与原评判/采样参数，不补随机padding或人工tag，在同一已验服务的原16K短背景负载中生成；两臂同payload，稀疏关联实际outside q1的reqID与生成进度，只认可该题最终答案之前的P作用。先baseline本身答对且candidate有真实覆盖才有判别力；无覆盖或baseline不过即停止，不继续造易题/改温度/调容差。通过仅补分支功能与精度信号，不是新的完整95%成绩或稳定收益，最终仍需原评测门和可比性能证据。若最薄reqID/答案前关联也无法复用现有owner，建议P暂保留、不默认；理由是多步隐藏状态/KV与随机采样的答案质量尚未覆盖，而非两算法bit不等或收益小。只提供方案，未实现/上卡/改原件。


随后root明确不采用上述背景Math方案、不新造客户端，优先一次最薄真实结构门；以上语义门仅讨论，不实施。增量证据分界已回root/作者：085500的full-M两序slot已实际对CPU几何（不限15q1），以及42pool/prefix不交、15q1 IDs/positions/QKV/seq/有效表和采样前RNG均复用；已有6+2 CPU合同及原AST证明P双射/ends、_sample/bookkeeping/update与调用次数未改，不重做。尚未实拍的实际接线只有其余prefill token的完整M IDs/positions H2D重排，以及实际GPU N logits_indices值是否等于按原reqID/q独立计算的ends；可沿原shadow各补一次小快照，N全seq/有效页表顺手覆盖两prefill即可。sampler若需现场佐证，只同execute入口InputBatch/reqIDs/row map/sampling_metadata/generators身份、N行数与唯一调用；不复制全hidden/重复LM logits，不深扫历史或要求sample后history不变（原_sample内异步history刷新及bookkeeping是合法原行为）。结构门不宣称多步答案质量或新accuracy，原101/105、独立reference各保原覆盖范围。未写实现、运行新suite或访问GPU。

compute-order 最薄结构门新增窄审通过：helper `12076fa9e2cbde1e0fd4fc93ba722bd8f6577bdc130435ec1007ea5e34c8547c`，仅部署 `files-final` runner `3e99f5751d425c488021eca07e47c55fae7b7e47adce25ed4280e3c8fc67cec7`，builder c719b115。原序只 prepare 后同 current stream 的完整 M IDs/positions 阻塞 D2H，完成后再重写共用 pinned staging，原 prepare event 域保留；不跑原序 model，不新增 RNG/LM/采样。期望 token inverse 与原 N logits 行由原 reqIDs 和 SchedulerOutput.q 独立构造，不用被测 Plan.ends/inverse。原 _sample 本体及调用次数不变；actual InputBatch.update_async_output_token_ids 仅原位更新所需 history，不替换 sampling_metadata，前后 identity 检查可成立。回调同 execute/scheduler/logits 身份关联且原 callee 不在异常回退中，失败不重试采样。没有当前一次短诊断阻断，验收须 sample-link.json 的 structure_and_actual_sample_link_completed、同 PID marker 及正常服务收尾；仅 structure.json 是等待实际采样，不能当完成。复用旧 slots/seq/table/42 层及 scope 证据，不证明多步答案质量、新 accuracy 或收益。只读新增 Session/runner diff/必要相邻实际源码与 SHA，未执行新旧 suite、模型、SSH 或 GPU，未改作者资产；已回 root/作者，后续部署由 root 独占。

math4 独立混合诊断新增窄审通过：helper `29b95266476c0c26e3ee755ccc3eab95cdf700c4e0a2ce446c74fd784fc00a3a`、EvalScope capture `9e1f6bcf44c0b3c78226e87d2b8ccc0b5a95aa6d5af98a2eeab6f66a41d74aa5`、builder 0f4f7fc4，基于冻结423、无结构shadow或额外模型前向。仅实际 P 的 chatcmpl outside q1 留原CPU computed/prompt与原sample一次返回；q1/noSpec下预测输出下标 c−prompt+1 与实际positions来源一致。原_sample本体、sampling_metadata对象及随机值不动。实际 EvalScope completion_params/on_response 保原hook一次，只增加 return_token_ids 与原响应旁存；actual ModelOutput保 completion.id，原choices转换与judge未改。背景原 /v1/completions 不与 chatcmpl 题目混淆；internal RID相对response.id追加8位随机后缀须后验精确匹配，不能直接相等或模糊前缀。原6e045参数经shlex保留，仅workdir/limit4改变；210s内部deadline与两组各5s TERM/5s KILL在原240s内，原bc51只CLI/load两处、无编排重试。当前无新增短诊断阻断，owner最终CAPTURE/LOAD身份锁待作者冻结后只补核闭包。processes_completed仅进程结果；需原题index0..3/原judge/四份真实响应token及答案前P作用位置后验，缺覆盖/少题/超时均inconclusive，不当官方105题准确率或性能。未执行HTTP、客户端/模型、旧测试/新suite或设备，未修改作者资产；最新root已批准此原题四条方案，覆盖此前不实施背景题诊断的阶段决定。

math4 最终闭包已封口：load `03a0c9027063b239dad66b8d15d87bb867d6e93a1ccf0286882284140d9030e6`、派生 owner `4552fb7f8f92e27af417239488198c01407f0f5474875740d38b5b60decb246a`、root launcher `2d1f62f41d37e9293778983b45894e3bbbb9ba11b7bab9a30765e5537910eec4`、deployment10f674e7。最新编排改为仅候选、背景先行，先记本轮server.log byte边界，只读取后续完整 FIRST_SELECTED 行才启动原EvalScope；仍统一210s期限，背景先退出/无marker即未覆盖，不重新选题或重试。三个诊断资产pin、同目录owner→load→capture、math4-artifacts ENV及尚未创建的client-capture路径相符，原bc51两切口及root隔离五路径/源map/清理未扩改，无当前一次短诊断阻断。放行marker仅证明背景激活，四题P outside及答案前时点仍须逐题后验。已回root与作者ready；本人未执行任何owner、客户端、测试或设备。

math4 reader `6b49cffb5672904f949f366d919a5c670a927b3ddf8be21994151c74e774fe05` 仅本轮0outside路径新增窄审通过。定点读取061500原prediction/review各首条核schema，实际行序可乱但keyed按index0..3固定question_id，原sample_id/score.status/accuracy路径正确；四个raw response.id与prediction.id一一对应，真实token IDs长度/usage保原judge，无新判卷。events为空时decode_needed=False，不导入transformers/decoder，逐题outside=False和答案时点None，汇总0覆盖不称P通过。root已核505原件且实际事件目录为空，调用必须指向已封存存在的math4-artifacts（rglob不存在目录也会空）；本次不改冻结reader、不扩有事件/boxed分支审计。未执行本轮reader、读取本轮响应、解码、旧门或设备，已回root/作者无当前零事件分析阻断。

PR #15 实际提交完整准确率最薄包装新增窄审通过：`tmp/pr15-accuracy/launch_pr15_accuracy.py` e884b4b29ba36c96d28afc947527d14f87d68e4108a4254035eaab1a7b810951。固定commit638c4ac0/tree d6a9597、tar a61e717f；先核单根/成员路径与类型/全部432 Git blobs及mode后再filter=data解包到指定全新source。唯一configs/moe symlink以link文字计算Git blob，前后resolve限制本树；常规SHA跟随已确认本树目标，control保link并复核两种map。实际runner195cc806/helper0e961对应PR源码，末两项仅main-tree归档及原env移除名记账。原35d/6e045/SERVER/105题/阈值/单卡锁/DB/cleanup均复用，不新增源码观察器、Q环境或旧组合补丁。SQL只作请求前启动门；同Engine的原CPU_METADATA_FIRST_SELECTED后验，在195cc与noSpec helper成功路径下证明pending computed copy确实被省略。作者唯一check-only实测23b9原稿，最终e884仅记录delta且语法过，本人仅读新增逻辑与精确SHA，不重复check-only/解包/214819/旧suite或设备。无当前启动阻断，root唯一部署；本轮尚未取得105题结果，不能继承旧组合准确率、外推C500或将历史pair当PR整树性能。

PR15准确率本地导入器新增symlink分支窄审通过：`tmp/pr15-accuracy/import_pr15_accuracy.py` b6c1e0f7ee452cad0da5e30de1fc5eb888f3c5acd7ed59e7e59c225ba5ce9aef。只允许固定112356 control/plugin-source中的nvidia.json别名，linkname及e0f Git blob逐字锁、sealed432 Gitmap唯一120000；同目录H100目标必须tar regular，目标Gitblob及目标/别名两处原seal内容SHA均一致，不能形成循环或escape。本地以普通文件材料化原目标字节，保持旧size/SHA/完整seal集合与已有异字节拒覆盖；stdout单列materialized_symlinks的原路径/linkname/blob/目标，不改原tgz、不向sealed树加说明。parents[2]项目定位和Windows扩展路径保留。仅静态新增风险/实际SHA审核，未执行导入、读取本轮包、reader、下载或设备；已回root/作者无当前本地导入阻断。

PR15 importer最终8e2d67dc9c32d0fff49cc1396f04cbd0b712ede965cf91a12eb6e4c2ddb48e38仅根定位改为当前文件祖先中registry.csv+AGENTS.md双标识唯一根，零/多根拒绝，再用原Windows扩展路径；已静态通过，可归档后复用。原b6c链接/seal门未重审，未运行测试或导入。

compute-order pending决定复核（仅现成证据/源码）：目前保留但不集成合理。054306→060425表观+4.7989%因KV521936/521840失配仍gain=null；061500原105题与104132原4题都无目标P覆盖，不能和100604完整结构通过、085500单行GQA更近CPU参考拼接成新路径答案质量通过，也不因不同Attention输出bit不等直接否P。现成044216短输出metadata记录的759/3000 outside中，30请求步位于当前P拒绝的Dprefix0两步；按形状至多70mixed步/729 outside（总250mixed），未核逐步其他guard/forward。002156长输出至多2步/52 outside，不能外推官方多波或短输出。以上均非K/耗时加权，192308的1.587s 2D是prefill且29decode已GQA，不能整段当P可省。082246另证P把suffix变纯prefill后Q-hoist从fallback变selected，因此净差包含outside→GQA及suffix已有Q-hoist启用，不能重复或全归outside。私有页表np.take按短快照形状累计约36.97MiB（N16/17每步0.5/0.53125MiB CPU复制），其后页表H2D替代原同大小copy；其余Plan/metadata/索引成本未获实际临界路径计时，没有可靠秒级收益上限。

下一最有信息价值的条件建议是同KV/同DB、原context-screen且实际P命中的最短对照，直接计入私有重排全部代价，不再为填预算造长profile或重试Math题/到达时序。匹配pair有净正信号才推进必要的新路径质量验证，仍不直接集成；匹配pair非正则保留已有实现与负结果、停止当前P额外诊断投入（不称单pair证明永无小收益）。再遇KV失配就继续pending，不强凑容量/重复挑好结果。真实质量门仍是默认集成的独立条件，不被性能正信号替代。已与framework/hardware交换现成覆盖与预算缺口；未新增代码/长报告、运行旧suite或访问设备，原文只补本段。

root采纳一次原context-screen短pair，复用422/423，不再加Math覆盖门或profile。现有两个emitter携带冻结82514完整map，原bc51/SERVER/seed/VERIFY0/finiteunset及单owner保持；通用seal_framework_screen.py按run ID补源码/清理/DB后态可沿用。旧save_baseline.py含旧包SHA、结果和registry写入，不能复用；旧pair reader须只更新新RUNS/launcher pin，保31门。DB最早在baseline封存后核两端，candidate db-before后可与其比，但现owner紧接Popen而无自动比较闸；完整四端须候选清理后db-after。KV最早在server.log出现GPU KV cache size时可知，原bc51 ready后自动smoke/load，没有启动KV拦截闸。任一失配就gain=null/pending，不循环重启、改容量或挑结果。

本轮新candidate launcher `tmp/compute-order-retest/launch_candidate.py` SHA63abd494f5831c5d35393dbcc88bafa1a776a7930e24fb4afc9f699ee4bdc24a已只读封口：仅purpose.comparison_baseline由054306改为实际120949基线，单锚逆换逐字节等于995d原稿；423 builder、命令和清理未改，无新增运行阻断。本人未执行owner、设备、旧suite或重新compile；root唯一运行本轮，最终仍以新pair真实KV/DB及实际P命中验收。

新pair reader `archive/ai/20261022-framework-kv/compute-order-retest/compare_service_pair.py` SHA7a891612ee6492d7669a83f0d6dc3b6d2ac38b7589b26d796726c7ab4db895cc窄审通过：对e3ae原稿仅两RUNS改120949/121541、candidate launcher pin改63abd及ROOT改registry+AGENTS祖先定位四处，当前祖先唯一命中项目根，原31门、DB/KV失配gain=null及marker验收逐字保留。未执行reader、旧测试或设备。

事件驱动Math4新增observer窄审通过：`tmp/compute-order-math4-event-gate/biv150_math4_events.py` 7f929c0460a467cae5689be20e7bb8c6cf7f7160a31f35c1223c1944435c0e43，仅部署files-final/与对应425六路径receipt；runner7e1104及原29b952 outside/sample不变。原_update_states/make_plan之后只读CPU几何，A须真实finished且本步absent，四Math本步q1/达到prompt、Math位于row0、B位于非零低行且后有Math；按互审建议补B本步q1/达到prompt，不能只用过去both-q1。actual completion链582b确认header→cmpl-header→-0→8hex，manifest字段engine_input_request_ids保存完整子ID，匹配仍严格唯一8hex；未知不猜行号。完整JSON关闭后一次rename发布，观察异常禁新信号，不改批/模型/采样/GPU，也不重试原callee。新目录无旧信号及client按manifest验收仍待加载端闭包审，CPU事件不证明实际P或答案覆盖。仅只读新增代码/diff/最终SHA和镜像，未运行代码/旧suite/设备。

事件Math4客户端/薄owner最终窄审通过：load f7013086、benchmark gate 7cf010d7、warm f630f5e5、owner6999477、launcher33f2e7f3、deployment03f2d1da；payload恰14允许路径且字节/base64/SHA一致。四题到原generate入口ready4后才起同一次原32请求，actual ready test的None ID直通，主32沿原sample ID/payload；首2真实both-q1放行四题，尾30只等同PID/configSHA release，observer失败/几何丢失即终止。新events目录及旧信号拒绝、210s统一期限和两自有组各TERM5/KILL5清理闭合，原240s owner只改load名/pin，不加请求、模型或采样改动；可进入root唯一一次短诊断，实际逐题outside/答案前作用及原judge仍须后验，退出0不等于覆盖通过。本人只读新增源码、必要actual调用点与资产身份，未执行客户端、测试、reader或设备。

原read_math4.py 6b49非零outside/boxed分支补充窄审通过：q1/noSpec下c−prompt+1为本次新采样生成token下标，ids[:index]只含此前生成token；raw response/完整internal RID唯一关联及usage/prompt长度/范围、原sample一次门保持。需使用本轮sealed事件与已核8hex内部ID、同设备版本MiniCPM tokenizer（reader不自行锁tokenizer）；prefix任意完整box含空box均拒边界，full无box/无decoder不作断言。该标志只证明首个完整\\boxed闭合前，P仅生成闭括号也可能True，不证明实质答案内容受P影响或完整新路径精度；须逐题沿原judge解释，unattributed/无命中不当全四题覆盖。本次仅读分支及原事件字段，未执行reader/解码/模型/设备；若仍0outside，此审查存档而不触发补跑。
