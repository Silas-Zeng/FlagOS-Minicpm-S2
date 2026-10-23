# 当前工作与 API 接续

更新：2026-10-23 06:35 UTC。计算序423短服务及配对分析已保存；新准确率061500正在运行。结果只维护一张总表及原件链接，代码按方法PR，源码未变不为发布重测；本地批量上传与远端实验并行。root正在维护现有实验PR #2；官方上游仍只读。接续框架/KV/调度主线，新增算子由队友负责，root是唯一SSH/GPU owner。

## 当前设备与下一步

- **唯一在途GPU任务**：`accuracy/20261023T061500Z-compute-order`，原35d owner PID3241、server3255、Engine3407、eval3663；source `code/compute-order-20261023T060425Z`，固定423/map6cf2e1d7。原6e045 Math500 Level3/105题、原SERVER/参数/阈值不变；VERIFY0/finiteunset/Qartifact绝对路径。06:35实核103/105、GPU28684MiB/85%、owner活跃。尚无COMPUTE_ORDER实际命中，即使最终准确率通过，也不能当作新排列路径的数值验证。launch回执在同名`-progress/launch.json`，不可启动第二GPU任务。
- **计算序短筛已完成并独立比较一次**：060425 candidate32/0、99.536272152s、5308.456792453 total tok/s；054306 baseline104.312939462s/5065.373507102。31门30真，唯一same_KV失败（521936→521840），DB四端554/20517三SHA一致，`gain=null`；表观+4.7989%仅作下一准确率的候选信号。Engine2350实际N17/M2048/Dprefix1/Dall15/outside14、原17采样行，forward返回；不等同采样/GPU完成。原eab7封存484文件全核导入。唯一reader e3ae及结果`analysis/compute-order-service-pair.json`，不要重跑。
- **发布节奏按最新用户授权执行**：GitHub应用连接器暂网络失败；GitHub CLI已实核Silas-Zeng账号、私有`FlagOS-Minicpm-S2`及开放PR #2（`codex/framework-experiments-20261022`）。PR #3是队友算子记录，不改。当前批量补从上次已发布9b451d8之后的完整实验增量、负结果及中文导航；不更新main、不等代码合并。下面旧“本阶段GitHub只读”是已被本条更新的阶段状态，非当前限制。
- **054306基线已结束**：`framework/20261023T054306Z-compute-order-baseline-context16k`；原422、bc51 owner PID1147已Z、server1160/Engine1312退出。16K/128/c64/32请求，32成功0失败、104.312939462s、5065.373507102 total tok/s，560原件核对导入；原SERVER/seed721201、VERIFY0、finiteunset、无profiler。KV521936，DB554/20517三SHA前后不变，最后68MiB/0、双栈9031关闭。完整回执在同名`-progress/completion.json`；不得与旧诊断算收益或重跑凑KV。
- **CPU接续**：计算序四路径已冻结并上卡，资产及CPU合同在`archive/ai/20261022-framework-kv/compute-order/`和`compute-order-review/`，root编排在`compute-order-owner/`；真实原异步input AST 6场景、实际Plan 2场景通过，非GPU数值证明。framework_innovation独占`tmp/accepted-fill/`准备独立原422的无消费者GPU fill候选，保持CPU fill及fallback；尚未上卡，后继设备由root统一安排。
- **上轮计数诊断已结束**：`framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic`，原bc51 driver PID79已Z、server92已退出；source `code/q-gqa-mixed-coverage-only-20261023T044216Z`。32成功/0失败、exit0；487原件已封存导入，最后实核设备68MiB/0%、双栈9031关闭。PID编号与旧容器不同，现场状态以本run原件为准；回执见同名`-progress/launch.json`及`completion.json`。不要重复启动旧002156/旧串行队列或本run。
- **短输出排列机会已确认存在**：`analysis/q-gqa-mixed-coverage-only-short.json`只成功分析一次；显式计数模式，无profiler。末421execute/259metadata/250mixed，prefix外及未入plan均759/3000=25.3%，unsupported/errors0；长输出原002156为52/4032=1.28968%。两者都是CPU metadata计划计数、非forward/确认decode、无K或耗时加权；不能称25.3%性能收益。原KV521840，DB554表/20517行及三hash前后不变。下一步按runtime混合形状判断compute-order净成本，先最小正确性实现，不直接集成或用计数外推分数。
- **SQL规则复核**：2026-10-23读取官网公开赛题详情，原件及回执在`archive/rules/20261023-sql-compliance/`。现有ad84只缩小SQLAlchemy表结构反射，原配置键/选择/读写/自动调优保持；按当前规则可保留，不等同任意改配置行或组委会单项审批。详原`analysis/2026-10-21-sql-reflection-plan.md`顶部增量。本轮未改受测代码、未重跑旧SQL测试，GitHub只读。
- **002156诊断已完整取回**：`framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic`及同名`-control`，Engine390300；490原件已由root逐文件核验导入，tgz 3002843字节、SHA前缀a9514412。独立reader和mixed摘要器各运行一次，结果为`analysis/q-gqa-puredecode-native.json`与`analysis/q-gqa-puredecode-mixed-coverage.json`；不重跑GPU、reader或全量封存检查。
- native支持完整8 CPU步/8实际GPU graph，固定N=M=31、同PID/时钟/相关ID映射及完整窗口检查均过。hardware汇总graph为52.3207–52.4271ms（中位52.3947），下一图已提前50.798–51.199ms提交；五个内侧间隔2.0620–2.1179ms，其中可见GPU活动1.9035–1.9332ms，sample占0.8775–0.9006ms、LM head占0.9293–0.9420ms。剩余未覆盖0.1582–0.1985ms不是idle或收益，当前窗口不支持把间隔当CPU未及时提交；边界同步及观察开销仍限制外推。
- **mixed实际有少量遗漏**：末次shutdown快照到2109次execute，261次合格metadata、252次mixed；unsupported/observation_errors/multiple_builds均0，8次native窗口及1836次标量pure分支按设计跳过。mixed q1共4032，其中outside与未入plan均52，即1.28968%，集中于两个N29步骤各26（M259及2048）。此前只看局部hist而称零遗漏已更正。该比例无K加权、q1不保证确认decode身份、metadata plan非forward，仍不保证全负载覆盖；不能据此直接估算收益或外推128输出/官方多波。
- **官方231746已完成**：717原件全核，8行raw/2摘要、原第2–4轮均值、1536成功。4K总4957.95/output991.59 tok/s（264.56s），16K总3669.74/output215.87 tok/s（607.19s）；固定原422、VERIFY0、finiteunset、KV521840、无profiler。16个独立key的SAVE/FULL/DROP/runner/output链完整、rollback0。完整记录`analysis/q-gqa-kv-official-final.json`与`q-gqa-kv-official-transactions.json`；仅绝对结果，不算与旧414的跨条件收益。
- 官方最后封存DB为554表/20517行，之前544/20246；snapshot c8ba0a91、schema c7699d51、logical682b3a90。002156前后554/20517且三hash不变。准确率继续引用原422的103/105；VERIFY1字节资格为独立213134，不把本轮VERIFY0或诊断称新准确率/回读。
- 官方后串行队列已完成：`queues/20261022T235007Z-after-official`、原PID387488为Z，终态`diagnostic_dispatched`，先d9封存再a634启动002156；不重启队列或另手动封存官方。官方tgz为3549913字节，SHA fb9b4957090a4cf202620bff4ad1f9540ab4f01cc57df8672b5fe555f38aba1c。
- 原官方导入器abd7在Windows扩展路径的目录lstat阶段失败；改用既有逐文件方式派生dc34，717原件/718既有文件含seal全部匹配，无覆盖或新增。事务reader在首次失败后已跑一次，之后其输入log SHA与实际及seal三方一致才接受结果，未重跑。修复及原失败在`archive/ai/20261022-framework-kv/q-gqa-kv-official/import-repair-check.json`。
- CPU下一候选仍是内部compute-order与原sampler-order分离：dispatcher51f63275已证明限定mixed模式无padding；原N行采样/RNG调用不变，逆映射使用原logits gather，额外CPU页表/metadata/logits索引搬运须计成本。若改runner，protocol/worker两处整SHA锁须显式重定。128输出已观测25.3%机会而1024输出仅1.28968%，不能按输出长度硬编码或跳过净成本判断；后续实现及上卡结果见顶部060425/061500。
- `tmp/q-gqa-mixed-coverage-only/`五件冻结资产通过单SSH上传并运行上述044216；原bc51 owner/SERVER/seed721201，显式mixed_coverage_only关闭profile分支、不挂sample wrapper，原runner/协议不变。原eab7 sealer/普通framework封包导入已完成，tgz2890680字节、SHA48b1d0e7。首次误在SCP尚未退出时调用导入，被尺寸门在写入前拒绝，摘要也因缺原件未生成输出；等待传输exit0后才成功导入/分析，没有重跑GPU。原失败简记completion回执，不重复旧门。
- 计算序候选另须计入NumPy临时缓冲：[官方take文档](https://numpy.org/doc/stable/reference/generated/numpy.take.html)说明默认mode=raise的out会buffer；实现时结合实际版本和合法P验证选择复制方式，不按零临时副本预算。未据此改运行代码或做性能外推。
- 多槽扩展暂不实施：00:08在途Prometheus累计抢占11与协议保存/恢复/输出各11相符，3710次fast_reject不是漏SAVE；metric可能滞后，不能称最终全部覆盖。原观察保留在官方`-progress/preemption-observation-20261023T000800Z.json`。
- 新增算子由队友负责，本轮只做框架/KV和观测准备。SSH公开入口仍为`lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io:2224`；不读私钥、不改host-key校验。GitHub本阶段只读，本地代码、原件与中文记录批量保存。

## 刚完成的证据

| 方法 | 结果 | 边界 |
|---|---|---|
| 当前Q/GQA+KV保存恢复422准确率 | 215836：103/105（98.0952%），105成功，0错误/截断/空答案；721原件全核。 | 此评测只有FIRST_CHECKED、无SAVE/FULL，真实事务字节证明另见213134。不是精度提升声明，也不是425的accuracy。 |
| 独立H2D pitched门 | 222047：真实1043页单层17088512B，66→14次（4线性10二维），selected/gap/guard/非零offset/同流消费者+事件/RNG全过；88原件。 | 新SO实际编译通过；无性能计时，不替代42层事务。 |
| 新FULL恢复425 VERIFY1 | 222222：32成功0失败；R16704/1044页/718405632B，SAVE210、FULL672、c95f回读2772、zero0，42层源/目的字节及runner六checks/consumer8/host释放通过；492原件。 | 实际是16段/层，不硬套单层门14段；182.781526s含诊断不算收益，425准确率未跑。 |
| 原422性能单pair | 213757→214326吞吐+0.846849%，TPOT−1.438678%，同KV521936/DB540、30门过。 | 保留单次正信号，非稳定统计。 |
| 独立省computed计数H2D | 215040→215331吞吐+0.619291%，同KV521840/DB540、30门过。 | 保留独立单pair，无新accuracy，不与KV收益相加。 |
| QGQA414官方 | 202736两case×4共1536成功0失败；4K总5002.10/output1000.42，16K总3679.39/output216.43 tok/s。 | DB532→540，只报绝对值；旧414 accuracy为101/105。 |

- 422 accuracy保持原模型/35d owner/6e045 Math500 L3脚本/SERVER/95%阈值及完整422源码，实际Q/GQA同Engine N8/M349各42次首次命中。关闭阶段警告保留；postflight确认设备68MiB/0%、端口及owned进程清理。
- accuracy当时令DB540/20112→544/20246；历史三SHA（官方后的554见上）：physical `e2c42bf6b40c39516e0f8ba0cba60f54c253baa581b049eefeba5c52ecf96152`、schema `dd221bc69bd0d4bab1fb5f9f21091820d88d671cd1db75af1fb5aceb9de9126b`、logical `a00ef835df710c2cb320dbbdc31902fe8875cea83f273df51954bc709f1b5de8`。222047及222222前后稳定544；因此本轮重新取共同基线，不复用旧DB吞吐。
- 分析入口：`analysis/q-gqa-kv-swap-accuracy.json`、`analysis/kv-pitched-restore-method.json`、`analysis/q-gqa-kv-restore-pitched-verify1.json`。真实425 reader最终d45de2f8已PASS。
- reader首ba5失败仅为Windows扩展路径转SQLite URI的%3F authority；d45仅在原fingerprint入口去扩展前缀，181/180字符短路径，原逻辑DB校验仍完整执行。原件和设备未改、没有重跑GPU。过程在reader-sqlite-uri-check.json。

## 实现、留痕与后续

- 资产与交接：`archive/ai/20261022-framework-kv/q-gqa-kv-restore-pitch/`；CPU工作稿在同名`tmp/`目录。新helper a7439c2c/cpp48295ffd；worker草稿9f178a70只用实际已验SO替换None。VERIFY1 builder f29f23e7/launcher352bc6b2均已互审。
- 原FULL页所有权/绑定/fence/真完成事件/VERIFY回读/异常settle不变；提交前强持host/raw/descriptors/bridge/stream。新桥异常即使submitted=0也要settle，禁止重试旧路。最终性能必须含首次加载、prepare及提交成本。
- 社区异步H2D只条件保留：在当前同步RPC里加线程不能消除等待；真正重叠需额外pending/事件代际/取消/调度状态和独立工作预算，当前不排新实验。资料与否决依据记`docs/agent-work/hardware_innovation.md`。
- 负结果复用：finite准入曾消除抢占但KV失配，默认关闭；不加假buffer/改固定KV凑条件。旧“Q/GQA更快所以swap不可行”已撤回，192308目标恢复prefill实录1.587201499s支持本轮测试。
- 单层门保存原`seal.json`，不往其control增添文件以免破坏425 builder完整集合。导入使用`tmp/import_saved_gate_longpath.py ... --controller-seal`；普通服务省略开关。Git用`git -c core.longpaths=true`。
- 原件统一`experiments/`，总表`experiments/registry.csv`；团队视图由`scripts/build_team_view.py`生成，阶段末批量更新。子智能体更新现有`docs/agent-work/`交接，不另造报告。
- 新诊断mixed摘要器`tmp/q-gqa-puredecode-native/summarize_mixed_coverage.py`（cf551ca3）经framework新增窄审，只取末次累计CPU快照、不重复相加；已对002156唯一运行并保存上述analysis，不再重复。三处社区参考说明既有持久batch重排和per-request seed映射不能直接替代本站global RNG合同，链接见原hardware交接。
- 检查点410d398保存422准确率、222047单层门、222222真实425门；de64f1c补充VERIFY0两侧1133原件、不可比结论及接续。当前allocator基线及下一候选另行保存。
- 本阶段仅本地保存，遵守本轮现有GitHub只读要求；不量化/推测解码、不升级框架、不改官方参数。最早接续见[阶段历史](archive/ai/CURRENT_WORK-through-20261022T215331Z.md)，旧PID/计划以本页和实核为准。
