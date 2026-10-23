# 当前工作与 API 接续

## 最新状态（2026-10-22 18:17 UTC）

- **唯一GPU作业：`framework/20261022T181739Z-bq16-chunk-chain-gate`，timeout owner336933。** 原6f/C2/C3，仅比较两种七段Attention调用几何；a30c gate/a784 launcher，strict输出/KV/RNG与侧流门后才32ABBA。不是scheduler实现、模型准确率或端到端性能。记账服务180643/181134均exit0、64/0，458/457原件已本地全seal验收，正核配对环境，暂不宣布收益。

### 基线启动记录（已结束）

- **唯一GPU作业：`framework/20261022T181134Z-async-bookkeeping-service-baseline-decode4k`，runner335602。** 180643候选已exit0、N63/M63真实sample首次命中、413源码及设备清理通过；待当前同负载基线完成且核KV/DB后才比较。其后运行已互审冻结的BQ16七段链门a30c7206，原算子不改。

### 候选启动记录（已结束）

- **唯一GPU作业：`framework/20261022T180643Z-async-bookkeeping-service-candidate-decode4k`，runner334356。** CPU输出记账候选已双owner静态互审及必要新增写入门，helper c7c91ece/footer7e8196ad/preparer a27e5295/launcher212131d6；413源只runner+helper，真实sample_tokens后命中才算激活。原4K/128out/64请求/c64负载，先候选、清理后基线；本地CPU片段百分比不可代替服务收益。BQ16链门已冻结a30c7206/launcher a7848995，待framework最后增量复核后接单卡队列。

### 上一阶段终态

- **本轮三个GPU作业均已完成并清理，当前无自有GPU任务。** 173203观察、174402 skip候选、174712干净基线分别460/460/459原件逐seal核验并落盘，registry155条/152run。两服务各1成功0失败、同原服务和16K/128out/c1负载；但KV为521840/521936失配，表观吞吐+0.201392%不能认收益。候选保留为“确有CPU死工作且真实skip激活”的机制候选，未过官方准确率，不补反复大测。分析见analysis/prefix-skip-service-pair.json；关闭EngineDeadError原样保留。
- **下一队列正在CPU准备，尚不能当已上卡结果：** hardware负责`tmp/next-bq16-chain`，在原算子上比较7个chunk的16-token对齐形状链，真实恢复窗口预计K循环少0.66677%、步数及固定MM tile数不变；framework负责`tmp/next-async-bookkeeping`，批量CPU记账本地片段N30/31/64的wall约53.8/56.35/113.95→14.95/14.67/19.83us，未验证BI实例或服务收益。算子仍交队友，主线是调度/框架适配。

### 基线启动记录（已结束）

- **唯一自有GPU作业：`framework/20261022T174712Z-no-cascade-prefix-baseline-single16k`，runner332488。** 候选174402已exit0、实际skip激活、413源/设备清理通过；当前串行同负载干净6f基线，待结束回收比较。下一调度候选为实际query粒度16对齐，已CPU重放恢复窗口：7步不变，K循环预计减少0.66677%、固定MM tile数不变；仅是计算工作量模型，未实现或测收益，不能沿用旧准确率。

### 候选启动记录（已结束）

- **唯一自有GPU作业：`framework/20261022T174402Z-no-cascade-prefix-candidate-single16k`，runner331509。** 新包helper仍e17、init b588、preparer6d809、driver38d8/launcher79a99，candidate只init+helper，原服务/单16K128out/c1不变。实际无cascade后端的单请求省前缀扫描；framework互审和双CPU准备通过。待退出与清理后同包baseline运行；只有同KV/DB/参数和完整原件核对后才比较，不以173203观察成绩作性能基线。

### 上一诊断终态与下一项

- **173203公共前缀观察已完成，当前无自有GPU作业。** 1请求成功/0失败，实际ARMED；128次N1累计CPU10.453319ms，32→128的96次平均107.610052us（含clock成本、不是吞吐收益）。413源/DB前后三SHA一致，460原件本地逐seal核验；关闭EngineDeadError保留，9031闭/设备68MiB0。已登记153条/150run，见analysis/prefix-cost-observation.json。正准备复用同helper的skip候选与干净6f最短服务对照。
- 队友PR12与C3的只读兼容检查发现：C3原forward动态读取backend全局unified，PR12已同步更新该绑定，mixed中的decode会进入新GQA，不存在需要修的漏路由。该方向停止，避免重复改算子。并行评估CPU输出记账批量化；调度chunk对齐须使用实际query tile16（不是BLOCK_M128，后者含8个GQA head），先核净收益，不据padding比例上卡。

### 本轮启动记录（已被终态取代）

- **唯一自有 GPU 作业：`framework/20261022T173203Z-prefix-cost-single16k-observe`，runner 330014。** 固定 clean6f，原服务参数，单请求16K/128out/c1/seed721201，仅观察公共前缀扫描CPU成本；源码只追加init与helper，不跳过扫描，不报告性能收益。启动前卡68MiB/0、9031双栈关闭，driver aef76c40/launcher4ba8c9。原结果自动保存，结束后核实际ARMED与partial计数并收尾。新增KV页zero已按真实FullAttention路径否决：热路径不执行，只有启动池初始化，故不实现不测。
- 框架后继需考虑队友的[GQA decode PR #12](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/12)，只读时head为cf1f44876e6cf9e16e8e53f160d630972e535109、尚未合并；其收益是队友报告，当前实验仍固定旧6f，不能混算。当前智能体不新增算子实现。

### 上一轮终态（2026-10-22 17:06 UTC）

- **165525恢复窗口诊断已完成，当前无自有GPU任务。** 32请求成功/0失败、native-valid，原6f仅追加footer，412源码/DB527表19702行三SHA及设备清理通过，461原件已下载逐seal核验。首次实际preempt同rid从payload2944恢复到16704，共7步/13760目标scheduled tokens；前6步D29/P2019，末D29/P1646，CPUknown不是GPU完成floor。3696可见kernel总3430.398ms，2D58.1271%、GEMM22.6206%、3D15.5462%；kernel首末跨度3476.593ms包含其他请求，不能全归victim或报吞吐收益。分析：archive/ai/20261022-framework-kv/resume-native-analysis/165525-analysis.json。
- 复用此轮累计puredecode直方图1838步，N30=463/N31=319/N2=477/N1=362（含smoke）；相邻档位GEMM同tile、空Attention早返，暂不实现图档加密。no-cascade公共前缀扫描只准备observe模式，未知真实CPU预算，不单独为它跑5分钟；skip未批准上卡。framework已结合旧FULL/pageorder/删ZERO/pitchedSAVE结果，判定目前无新增恢复机制可显著删工作，暂停扩swap/短R/恢复优先级；抢占到resume的43.1s是其他请求推进，不是GPU空闲收益。转常态框架路径，下一只读候选为普通新增KV页zero的真实必要性/成本（区别恢复页已测省ZERO）；先核write-before-read、未写尾NaN及既有轨迹，不实现或上卡无收益方案。新增算子交队友。

### 本轮启动记录（已被终态取代）

- **当前唯一GPU作业：`framework/20261022T165525Z-resume-native-diagnostic`，runner326831**，原clean6f仅追加runner诊断footer（e13d4613→runner01d7bc01），完整412文件其他不变，原16K/1024out/32请求/c64/seed721201。首次实际preempt的同rid恢复且q>1才采最多8个连续execute，下个入口stop保sampler；CPUknown/computed不当GPU完成。puredecode N稀疏直方图随同保存；profiler成绩不可算吞吐收益。入口前实时68MiB/0、9031闭，启动器与增量CPU合同/硬件互审均过，root唯一设备owner。资产tmp/framework-kv-next，待终态与raw回收。并行CPU准备no-cascade公共前缀扫描小项；不叠本诊断或改算子。

- **主线已按用户最新要求转向框架/KV 管理/调度/批处理与硬件及现有算子配合；新增算子优化交给队友。** 三个子智能体分别复核实际调度路径与历史负结果、BI-V150 约束及社区可移植机制；root 仍唯一负责 SSH/GPU。
- `accuracy/20261022T155446Z-q-fragment-hoist` 已于16:21:03Z完成，逐题核对 **101/105（96.1905%）通过95%门**，105请求成功/0 transport错误，1题(index83)达32768输出上限；无空最终答案。实际N8/M349步骤42层命中，不能据此报全程覆盖。关闭阶段EngineDeadError及ResourceWarning原样保留。DB前后527表19702行三SHA一致，413 live源码和归档源码身份核验通过，285原件下载逐seal核验完成，独立post已确认GPU68MiB/0%、9031闭、owned PID结束。已保存本地提交74fa242dde6cfd427f41d51d493f1416cc2d0c9a（151记录/148run），未发布GitHub。
- Q方法保留为**已过准确率的单轮短服务正信号候选**：吞吐+1.71126%、TTFT+1.3185%、TPOT−5.3841%，尚未完成稳定性或完整官方性能确认，也尚未开代码PR。后续框架探索复用干净6f组合，避免混入队友算子工作；Q源码与证据可供交接。

### 上一轮启动记录（已被上述终态取代）

- **唯一活动GPU作业：`accuracy/20261022T155446Z-q-fragment-hoist`，runner `321967`**。使用已测413源码 `q-hoist-service-candidate-20261022T153947Z`（helper77b489 / runner06c69f），原官方Math500 Level 3门。launcher43c3009只增加独立artifact目录、Q安装marker、已测源码及原35d30dfa驱动身份核对，已交叉只读审阅。等待终态，旧6f的102/105不可代用；下一任务前必须确认卡/9031清理。
- Q fragment已有4K/16K单层strict门均过，wall分别省16.1026%/20.1058%。真实服务153947与基线154518都64/0、同KV521936、DB四端三SHA一致、原参数/负载相同且仅声明两源码差异；短吞吐7051.2507 vs6932.6158 tok/s（+1.71126%），平均TTFT+1.3185%、TPOT−5.3841%。**只认一次可比短测信号，保留待准确率，不报稳定或官方完整收益。** 比较见analysis/q-fragment-service-pair.json。
- 两服务474/451原件已本地逐seal核验，全部结束并清理；153947实际N2/M2048单步42层命中，两cold recipe都ff64，缺最终summary，不能报全程覆盖。新接口直接上卡验证，未完成CPU mock已标draft且从未执行。子智能体记录在docs/agent-work及archive/ai/20261022-current-gpu-hotspots/q-hoist-service。复用缓存检查只读，未据此扩白名单。

## 已完成

- 用户已明确要求按依赖合并并复用既有验证。框架十项 PR 已按 #5→#6→#7→#8→#9→#10→#1→#2→#3→#4 合并；#11 仅更新中文 README。当前 main：`87ed53719126208eaa9ba1cab698b14a5693eb5d`。官方上游和原公开 fork 未改，旧快照与本地实验版本保留。
- #1/#2 的 runner 冲突使用已验证组合 `6f918ae6…`，保留两 helper、回退及 SQL→C2→C3。代码合并提交 0f2b9255 的全部 425 文件与预期组件组合相同，未重复测试。精确提交、双亲冲突解决及最终身份见[合并回执](archive/github/20261022-framework-merge.json)。后续代码与文档维护均通过 PR，不直接写 main。
- CPU组合070004/070452短测完成，两轮64成功/0失败、同KV521936/同DB，吞吐单轮+0.6986%、平均TTFT−0.1250%；小幅性能信号保留待确认。105839完整Math500 Level 3准确率102/105（97.1429%），通过95%门；此结论仅属于干净6f918组合。两CPU PR已附中文短测结果。关停EngineDeadError和一次DB快照误比均已留原件，不能写成日志无异常。
- 新一轮已收尾：085923 hot-key 门输出/KV/RNG正确但未命中，100149诊断确认默认 HookChain 对象被误当作非空 hook 拒绝；均 exit1、没有性能结论。100830 CPU组合短测64/0、38.867665s、6955.2931 tok/s，10:10:29Z exit0；随后用户要求直接合并，未再跑反序基线，不能据此形成新配对收益。三轮原件和校验包均已回收至本地 experiments/framework/，待下一实验记录批次发布。
- 10:43–10:56Z 连续完成六轮新验证，原件已回收并逐文件核验：hot-key v2 在长/短形状均未见收益，当前实现放弃；C3 view 清理在 D29/P128/KV1024 单层耗时降低5.9714%、CPU提交降低7.36%，保留待真实服务对照。大形状只见CPU下降，不能外推整体吞吐。
- 当前组合输入等待诊断：4K短测64/0、16K长输出32/0；最后快照分别256/2048步，等待占预处理0.0408%/0.0970%，长测有一次KV抢占。快照是部分累计，不报诊断吞吐收益；暂不优先拆输入同步。六轮已追加registry，连同前阶段三轮已发布到实验记录库PR #2（未合并），总表129条；远端分支603bce1a、tree f974d86e。

## 团队入口

实验记录库现名为 `Silas-Zeng/FlagOS-Minicpm-S2`（GitHub ID 1427279927），原名 `FlagOS-S2-Minicpm-throughput` 的链接仍重定向。2026-10-22 本轮首次发布在名称校验处停止、未写入；适配现名后重新发布，保持三个协作库分工。

[实验总表](team/experiments.md) → [按方法与平台查阅](team/README.md) → 每轮短记与原始证据。registry是唯一登记源，python scripts/build_team_view.py生成团队视图。README只负责导航及当前有效结果，详细历史从[归档入口](archive/README.md)查阅。

团队整理已发布为实验库提交 `7362fee812b786bb38a757a3b644ca21c33d4b68`，21810 项与来源 tree 完全一致；回执为 `tmp/publish-team-rebuild-final-20261022.json`。最新合并状态与协作规则通过单独的记录库维护 PR 同步，不创建重复仓库。

## 当前并行工作与下一步

- 准确率105839已于11:22:10Z完成、exit0，105请求成功、102正确、无输出截断或空最终答案；原件已下载且全部逐文件校验通过。102/105不能代用于C3views或新gather。其后112338纯decode CPU gather门通过7种情况、4步图重放、RNG与完整有效GPU输入检查；真实服务负结果见下条。
- 两个服务候选已收尾：112548基线6936.7042 tok/s；113326 C3views6937.9311（表观+0.017687%，KV521936 vs基线521840失配，不能认定收益）；113627 gather6881.3277（−0.798311%，同KV521840），均64成功0失败、同DB527表19608行、源各仅两处变化且实际命中。C3保留局部信号候选，gather当前实现不集成；不继续扩CPU细项。三个服务及准确率/gather门共5包已下载并逐seal核验，登记总数134条，尚未同步远端PR。
- GPU短诊断114435已于11:48:06Z完成，32成功0失败，native-valid；原件465项已封存并回收到本地，总表135条。当前6f仅追加诊断，3步均N2/M2048/P2047且完整包含采样；1656个可见kernel总1063.156ms，2D Attention占60.2339%、GEMM31.7161%，不能当全负载占比或吞吐成绩。源仅runner29d98aee、DB同527/19608，设备清理已核。
- w16单点120226于12:02:49Z收尾，exit0；真实D1/P2047/KV16K上界下严格bits/全KV/RNG/新指针/非默认流/scale门全通过，但32ABBA wall11.089565→14.605917ms（慢31.7087%），event慢31.9930%。实际regs101/spills0/shared65536/warp64；原全局已恢复。放弃此点，保留w8，不扩tile扫描、不接服务或大测。policy c27a4da7/gate27942414及33封存原件已回收核验；该KV不是上一轨迹记录出的精确seq_len。
- 121701 V-late门已收尾并登记，总表137条：共享内存64→48KiB、regs102→100，严格正确性通过，但wall慢1.4523%、event慢1.3014%，当前配置不集成；35原件已本地逐项核验。单项负结果不排除有硬件机制依据的A＋B，hardware与team子智能体正查BI-V150实际资源限制及社区组合经验。
- 两个无profiler长基线均已结束并各核验451原件，均16K/1024out/32请求/c64、32成功0失败、1次抢占：122216为219.973985s/2532.372182 tok/s/KV521936/DB527表19608行；125135为219.996000s/2532.118768 tok/s/KV521840/DB527表19702行。各自DB前后一致、412源相同，但跨轮DB和KV不匹配，不算配对收益或自然波动证据。
- 末层尾段裁剪两门已收尾：123334因真实TP组未初始化而失败，无数值/计时；124358补真实world1后初始化/清理过，默认输入bitwise，但换值+新指针+非默认流用例maxabs0.0234375/0.017578125未过原0.01容差，无计时，暂停此实现、不放宽门。其运行使DB新增94行。原件480/482项分别封存，v2数值失败不能归因单一stream或舍入因素。
- 124857实际SDK属性查询已保存17项原件：16SM、warp64、每SM shared128KiB/regs262144/threads8192、L2 16MiB；仅只读报值。shared64→48KiB的两者粗界均2CTA，不支持驻留翻倍。actual loader在shared>48KiB时设置PREFER_SHARED的阈值已核，故追加A+B三臂。
- 130038三臂门因base/spec来源pin错误在任何cache修改前停止；130457修正实际spec身份后严格门过。原wall11.091868ms、A默认Vlate11.227600ms、B仅设独立函数PREFER_SHARED11.258116ms；B较原慢1.49883%，B对A的event仅快0.02373%、wall慢0.27180%，不认定收益、不集成。A/B同binary而module/function各异，setter rc0、carveout rc801不可观察，dynamic上限原已128KiB且未修改；38+38原件已核验。
- **当前自有GPU作业均已结束，K lookahead收益复审不通过、不上卡**。用户要求组合前充分判断收益，预计无收益就不测；三个子智能体已恢复。root已只读回收原版/Vlate的8份真实编译IR，全部匹配130457所存SHA，位于analysis/source/current-attention-ir；没有新编译、GPU执行或修改远端代码。hardware/framework独立复审一致：虽有next K/PV潜在重叠窗口，但未证K等待暴露；不减bytes/dot/CTA，不提高共享内存粗驻留上限，carry和页表等待可能反增成本，因此无可信净收益依据。保留tmp/next-v-late-k-lookahead未测草稿，README已明确停止；静态正确性ready不授权部署。下一步先CPU核已有IR的重复搬运及框架可删工作，有具体收益依据再立候选，不为卡空闲强行测试。
- 第三位子智能体筛选的“跳过未完成prefill的LM-head/采样行”也未获上卡批准：当前D1/P2047仍有decode，同批删一行未必省权重读取或launch，却增加行映射/RNG保真成本；社区已有做法不能直接外推本机收益。短结论复用archive/ai/20261022-current-gpu-hotspots/community-interactions.md。此次3位子智能体均已收束，均无新GPU、编译或实现；后继不能把上述未测草稿当就绪队列。
- 八轮GPU阶段已批量更新实验库PR #2：远端提交3d52b3f577cf08ae313d19c104da0b929fdd6b3d、tree e6b5b173e3eedb35410fcb6fa6155e75342832cf，对应本地9b451d8ab3d590e0496b6abbdf806595a3c0510c；144条登记/141个run，中文正文已追加并核对，未写main。回执archive/github/20261022-gpu-hotspots-pr2-update.json，原发布state在tmp/stage-pr-updater-gpu/update-state.json。下一批必须以9b451→新阶段增量适配，不能复用旧476/5f997基点覆盖已发布路径。
- 用户进一步明确必要时做性能分析：有可信机制但缺关键瓶颈证据可补短profiling，不能仅凭未证明收益否定诊断。真实IR确认Q fragment在每个K tile重复读取32KiB shared，hardware准备tmp/next-q-fragment-hoist，仅外提该local_load、保原数学/同步并通过独立ir_override编译；仍未上卡。team准备tmp/next-q-shared-diagnostic原路径128次指标诊断，framework按新增风险互审。13:39:23Z实测卡68MiB/0、9031/9032闭；ixsys实际支持BI-V150 set2/general及set3/throughput，记录analysis/source/gpu-profiler-capabilities。后继启动仍须新鲜占用检查；性能成绩不取profiler运行。
- 用户最新主线：收尾以上两个服务候选后回到当前优化版本的GPU热点。hardware/framework子智能体复用现有轨迹，必要时仅补一次短诊断，按真实耗时选实际路径上卡；CPU小收益保留作并行补充。不要延展新的CPU细项阻断此主线。
- 六轮对应ID：104349 hot-key-v2、104449 c3-views、104544 input-prep decode4k、104920 input-prep context16k-long、105536 small-hot-key-v2、105635 small-c3views，日期均20261022Z。已测代码在 `patches/framework/candidates/`、`scripts/remote/` 与每轮source；CPU合同和子智能体交接在 `archive/ai/20261022-framework-short-queue/`。未测的新方案留tmp并在准备完成时补归档。
- 阶段记录PR使用 `scripts/publish_experiment_pr.py` 的增量发布器（从最新远端main新建codex分支，保留队友改动），不要复用旧脚本直接更新main。已合并十项方法不重开，新的有益方法独立PR；负结果留实验记录。
- 单卡实验仍由root唯一负责，始终串行。代码版本/命令/环境/原始结果自动保存，结论、失败原因、下一步只写几句话；阶段结束批量报告/PR，设备运行时CPU准备下一项。
- 所有维护说明与PR保持自然中文，英文专有名词、命令与原证据原样保留；BI-V150与C500证据分别报告。未确认准确率的组合不冒称最终提交资格。

[完整旧交接原文](archive/ai/CURRENT_WORK-before-team-rebuild-20261022.md)保留，旧文中的相对路径以项目根目录为基准；它是历史，当前安排以本页为准。

- 134939诊断在warm observer未命中时失败，未进128窗（worker failed/外层误报0）；v2 135558修初始化与退出聚合后128次完整、384条kernel、五项不变性检查全过，13:56:22Z清理结束。目标窗口各metric仅2记录、带宽项0，实际记录跨度56.8/1347.1ms，不支持瓶颈或吞吐结论。两轮33/34原件均已本地逐seal核验，registry146条；资产及结论分别在archive/ai/20261022-current-gpu-hotspots/next-q-shared-diagnostic和-v2。
- **Q fragment外提135941出现明确局部正信号**：14:00:03Z exit0，root已回收并核验46原件，全部自有GPU作业已结束。80d63/6a7f042冻结稿在D1/P2047/KV16K合成上界上，strict bits/完整KV/RNG/新值新指针/非默认流/回退均通过，32 ABBA wall11.028874→8.811433ms（耗时−20.1058%）、event10.930428→8.604557ms（−21.2789%），所有窗CPU无throttle。实际循环内Q读消失，shared64→32KiB、regs102→114、spill0；不据资源粗界宣称实际occupancy。独立JIT cache且原cache/forward恢复。仅单层信号，未有真实服务、graph或模型准确率结论。原件experiments/framework/20261022T135941Z-q-fragment-hoist-gate；包SHAca9f7851966098047bd42b58fcc727fac5d87e8f52a32ccd6b62f308f402331c。下一步CPU准备适配真实编译recipe的接入，不能将fixture固定TTGIR无条件推广；必要时最短服务诊断捕获实际recipe后再做干净服务对照。

- 152020同一80d Q-hoist仅将合成KV从16K缩为4K，15:20:42Z exit0；strict全部通过、同ff64→1543机制/regs114/shared32KiB、CPU无throttle，wall2.464499→2.067650ms（−16.1026%）、event2.358253→1.871339ms（−20.6473%）。46原件已本地逐seal核验，原件experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate。短长均保留局部信号，不做更多长度扫描。当前GPU无自有活跃任务，service最小适配在tmp/q-hoist-service，final pin/CPU增量合同与独立review尚待完成；只有作者冻结并复审后root才部署。

- **当前唯一GPU任务153947 Q-hoist真实服务短测已启动**：runner319143，source q-hoist-service-candidate-20261022T153947Z，原官方参数/bc51 driver/decode4k/seed721201。helper77b489a8、preparer8c6b687b，独立private JIT只编译实际ff64；未知IR原路并限量保存。原6f完整412文件仅runner追加+helper变为413；13项footer CPU合同与两人增量静态审已过，复杂helper mock明确未完成未执行，新增接口直接上卡判别。GPU启动前68MiB/0、9031闭；root唯一owner，先核真实命中及64请求完成/DB-KV/终态，不把本轮单独分数当收益，不并发另启任务。

- 153947候选服务15:41:51Z结束、exit0、64成功/0失败，38.338730s/7051.250728 tok/s，KV521936；actual execute第37次N2/M2048出现42层selected，两个cold recipe均ff64，非仅安装标记。DB前后527/19702，三SHA相同（logical dd3c10ee…）；413源码/设备清理通过，474原件已远端封存，包bb569ddd…/2785546B正在下载。**当前唯一GPU任务154518为原6f组合短基线**，runner320485，同bc51/decode4k/seed；等终态与KV/DB四端核验，尚无端到端收益结论。
