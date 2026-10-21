# 当前工作与 API 切换交接

## 用户恢复持续优化（2026-10-22 00:40 起，北京时间，最新有效指令）

用户明确要求“不断探索优化”“小收益也要上卡测也要保留”，并强调根据硬件特性、输入特点创新调度、KV 等框架机制。这覆盖下面的阶段性冻结。已完成的 SQL+C3 官方对照作为稳定基点，原始证据和受测实现不覆盖；继续以性能提升为主，优先框架层及大收益机会，也为小收益候选安排最短上卡实测，不设收益百分比淘汰线。正确性失败不启用，代码与负结果照样保存；噪声中的信号标待确认。验证仍先最短必要门，必要时才扩大，保持官方模型/参数/评测脚本。

root 正完成上一阶段私有实验库同步及离线归档，三位子智能体已恢复只读分析新候选；新GPU实验尚未启动。下一轮候选包括硬件与真实输入驱动的调度/KV/mixed 执行路径、CPU 已算 metadata 的复用、已有 async token 融合的小收益端到端测量、固定 tile MLP CTA 分组及已有 prefix-mask 小信号。它们都是待测方案，不能混入已验收稳定候选或提前声称收益。GPU 仍仅 root 串行使用；设备操作前必须重新读真实占用。下方“冻结”描述仅属上一阶段。

## 最终收尾与协作状态（2026-10-22，北京时间；覆盖下方历史进度）

用户已停止新增探索，本轮原版测量已完整结束，没有新 GPU 任务。**仅本实验分析库按天数 BI-V150 / 沐曦－曦云 C500 分平台整理环境、分析、证据和中文报告。两个代码库是团队共用库，不要求按平台拆分目录或分支。** 当前全部设备实测仅属 BI-V150；C500 由另一位队友负责，尚无其结果。

三个协作仓库均为用户自己的实验专用私有库，官方上游不动：

- `Silas-Zeng/FlagOS-S2-Minicpm-throughput`：本实验记录库，按用户最终指定大小写命名；发布版本以该库 main 最新提交为准。
- `Silas-Zeng/FlagOS-S2-vllm-plugin-FL`：新建独立私有框架副本，已发布 main `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`，完整 tree `82e37f8f263eeb09563a4790359ec95a0de1ca17`，410 项内容/模式均核验。原公开 `Silas-Zeng/vllm-plugin-FL` fork 按用户选择保留。
- `Silas-Zeng/FlagGems`：私有共享算子库，已发布 main `d7e5cef98344cd068df2e425748f849c94681048`，完整 tree `e8ba50863b7bfabc725cc6aaff97d3548d7daf0f`，4,769 项内容/模式均核验。固定 v5.3.5 / 4df，上游代码未改。

两个代码库的本地副本在 `collaboration/`；其本地历史 commit 与远端 API 快照 commit 不同，但完整 tree 相同。浅历史边界、bundle 和恢复方法见 `docs/offline-recovery.md`。Git HTTPS 传输失败后使用现有 gh 授权的 Git Data API 上传；曾被自动审批拒绝的临时 deploy key 没有创建，不得重试新增凭据。两位协作者用户名仍未收到，因此没有发出邀请。

**原版官方已完成并独立验收：** `20261021T122607Z-original-baseline`，benchmark 于 2026-10-21 16:14:45Z 结束，driver 于 16:14:50Z 结束，exit 0；8 raw / 2 summary，无失败。归档和远端实际源码 225 项全匹配，Attention 仍为原 bab2；candidate 230 项亦通过。完整 run/control 已取回，下载包 SHA256 `15ed19365bcec9cfe61e57d83336d2f5cab63e7f741294bdd2777da36e98249a`。postflight 为 68 MiB / 0%、9031 双栈关闭、无 GPU 进程；server/benchmark/EngineCore 均退出。runner 166637 已退出为 Z，PPid 1 尚未回收；首次 seal 仅在要求 `/proc` 不存在的末尾断言失败，原记录与补充说明都保留，不能称作仍在运行或篡改为不存在。

现有 e9dc 只读比较入口已 exit 0，结果在 `analysis/2026-10-21-official-final-comparison.json`：4K 1905.46→3683.65 total tok/s，1.9332×（+93.32%）；16K 861.9867→2729.0733，3.1660×（+216.60%）；Mean TTFT 分别降低 61.16% / 70.92%。准确率仍为 103/105（98.0952%）。原版 KV 521840 / 候选 521936；初始 DB 原版 512 表 19130 行 / 候选 489 表 18384 行，不能称缓存完全匹配、稳定因果增益或比赛总分。原版 DB 后态 516/19270，候选后态 501/18789。

本轮没有待跑的设备验证。交付收尾为中文正式报告/PDF、三库同步与全工作 ZIP；最终发布及归档位置以 `docs/github-collaboration.md` 和 `output/handoff/` 为准。重启 API 先读本节，再读子智能体索引及各自 handoff；下方保留全部探索时间线，旧“在途/未上传”状态不能覆盖本节。

## 历史协作快照（2026-10-21 15:35Z）

用户已授权在原版测量继续时上传GitHub协作、三个相关库设私有并邀请两位协作者；用户名仍待用户提供。实验记录库已按最终指定大小写改名为 `Silas-Zeng/FlagOS-S2-Minicpm-throughput`，私有；本地origin已同步。三个库描述已改自然中文。`Silas-Zeng/FlagGems`已创建私有；GitHub HTTPS clone两次网络失败，本地正式协作clone/上传尚未完成。现有 `Silas-Zeng/vllm-plugin-FL` 是公开fork，不能直接改私有，完整备份HTTPS也失败；不得删除或假称已私有，需安全处理独立私有协作。当前没有邀请发出。

**双平台团队总库：天数BI-V150由root负责，沐曦－曦云C500由另一位队友负责。** 用户已明确C500型号；现有全部设备证据只属于BI-V150。root建立 `platforms/iluvatar-bi-v150/` 与 `platforms/metax-c500/` 入口，原始证据不移动。三位子智能体正按分工中文化项目维护文档，保留命令/哈希/日志/上游源码原件；没有恢复性能探索。

**15:35Z设备状态：** 原版official122607已7raw/1summary，16K第3轮2584.31秒、128请求全成功，正在最后4/4；原Attention仍bab2。唯一owner仍root，runner166637；本轮不启动新GPU实验。结束后尚须完整postflight/live源225项核验、取回全run/control、执行e9dc只读对比、终审、最终PDF和全工作ZIP。

离线恢复准备已完成：`recovery/git`保存root与原13eb浅库bundle和状态；普通clone浅bundle失败已留档，先写shallow再unbundle成功、fsck0，完整4aba补丁得到精确候选tree5c14并可逆。`docs/offline-recovery.md`给出说明。archive builder已补tmp/pdfs源脚本与两个真实symlink entry、mode/mtime；最终ZIP未创建，Git状态须在最终写入/提交后刷新。此前bundles只覆盖当时HEAD c07eea1，后续GitHub提交必须更新恢复材料。

最后更新：2026-10-21 22:47（14:47 UTC），Asia/Shanghai。每次启动新会话先读本文件、`AGENTS.md`，再检查真实设备占用。顶端冻结/收尾状态覆盖下方历史条目；同一区域以最新时间为准。不要把历史空闲状态当作实时状态。

子智能体工作总入口：[docs/agent-work-index.md](docs/agent-work-index.md)。包含上一组团队成果、本轮任务与容量失败记录、三个当前子任务的持续交接。切换API必须一起读取，不能仅依赖聊天记忆。

## 用户最新要求

- 延续本项目已有探索，**优先框架层优化**：调度、执行图、元数据、显存、CPU/GPU 交互。
- 框架与算子并非隔离；有明确证据时允许修改算子，但不优先从算子重写开始。
- 用户明确要求多智能体并行搜索硬件特点、比赛经验和框架机制；GPU 实验仍由一个负责人串行执行。
- 严格遵守比赛规则，验证优先最短必要流程；只有候选值得继续或风险无法排除时才跑大验证。
- **小而稳定的收益也值得保留**，不设1%研发淘汰线；低于波动只能记待确认，不能冒充收益。官方计分门槛仍单独遵守。
- 最新优先级：**自主探索、以性能提升为主、优先大收益**；小收益保留但不应占住主线。允许框架与算子共同改造，有证据的算子方向也可以做。
- 持续保存工作记录，切换 API 后须能恢复，不依赖聊天记忆。

### 2026-10-21 13:30Z 收尾范围冻结（覆盖此前自主探索要求）

**14:47Z 真实进度：** 原版 official122607 已完成4K四轮、16K两轮（第二轮128请求全部成功，2585.11秒），开始16K第3/4轮；当前6raw/1summary，无退出文件，安装Attention仍bab2。继续完成最后两轮，不新增上卡实验。观察器可停止/重启但绝不能误停原runner166637；最新只读状态在本地 `experiments/official/20261021T122607Z-original-baseline-control/progress-latest.json`。framework和systems仅重新参与已有归档/证据验收收尾，不恢复性能探索。README已把完整4aba候选设为团队复现入口；Git历史恢复材料、最终比较和ZIP仍待收齐。

用户最新要求停止新增探索，保存现有工作准备 GitHub 团队协作；随后明确“把已经开始的做完”。当前原版 official122607 继续完成原两档四轮并验收，不能中途停掉后冒称完整。已开工的 CPU 源码审阅/设计草稿收成完整可交接文件，尚未开始的实现不扩大；不再安排新方向、新变体或新的 GPU 筛选。三个子任务已收到冻结指令。root 收齐原始证据、完成分档对照、报告和复现包；所有未验证原型明确保留为未集成。GitHub 当前只准备交接材料，未推送或对外发消息。

13:40Z 收尾状态：三位子智能体均已保存最终 handoff，C3 coverage 与 MM grouping 都只有设计/证据、无新 runtime 或 GPU gate，不安排上卡。`docs/candidate-usage.md` 已改为完整4aba一次应用入口并前置依赖污染约束；systems审阅通过。`docs/technical-report.md` 已生成3页在途版 `output/pdf/report.pdf`，字体/表格/页码已逐页检查；待基线完成更新数值并重新渲染。PDF builder为`scripts/build_technical_report_pdf.py`，PDF skill的create marker已成功执行一次。`scripts/build_handoff_archive.py --dry-run`通过，18744文件约626MB，包含Git忽略的SQLite及scratch原件，排除Git元数据/凭据/缓存/归档自身；尚未生成最终ZIP，必须等正式原件齐全及报告更新后执行。最新13:39Z远端仍16K1/4，原依赖bab2，4K4raw/1summary已齐，无退出文件。

## 最新结论速读（2026-10-21 13:26Z）

- 本轮直接接续上一 AI 的 083455 在途实验，未重开优化路线；原073309 SQL+C2和080656 SQL+C3源码冻结复用。
- 已过准确率：SQL+C2 101/105（96.19%）；SQL+C3独立103/105（98.10%，零请求错误/零截断）。SQL独立4K短测43.199/43.091s对匹配旧基点120.471s，约2.79倍吞吐，仅短测结论。
- 最新可比16K长输出（32请求、1024输出）：已热SQL+C2 231.322s，SQL+C3 220.368s；KV均521840，DB均483表18119行且三类hash一致。mixed约+4.97%单次吞吐信号，未称稳定收益或官方分数。
- 官方092944已完整exit0：4K3683.65 /16K2729.07 total tok/s，原8raw/2summary及230源SHA均独立验收；尚无matched原13eb总体加速比。
- 当前唯一GPU：official/20261021T122607Z-original-baseline，runner166637，原13eb隔离source091033/原791driver+官方原脚本两档各4轮。已空闲锁内备份并将已安装Attention从54c精确恢复为原始bab2；此baseline期间禁止导入任何retained/C3平台模块以免写回。尚无完成结果或总体分数。
- 12:57Z实查：原版4K已完成2轮，开始3/4；16K未开始。runner/server/EngineCore/benchmark均活跃，安装Attention仍bab2。原始CSV仅2行，尚不能算最终基线。完整SQL+C3补丁4aba已完成212份源码/一步应用/逆向恢复的独立包装审阅；未覆盖默认、未提交或推送。团队协作交接节点见 [docs/team-github-handoff.md](docs/team-github-handoff.md)。
- 13:05Z交接准备：只读CPU比较入口`scripts/compare_official_runs.py`（e9dc056c…）已交叉读审，原791/官方benchmark未动；唯一实际不完整baseline+完整candidate smoke返回pending/gain=false，完整成功分支未测。待原版完成、真实清理并下载全部证据后按 [docs/official-comparison.md](docs/official-comparison.md) 运行。当前baseline本地目录仅固定启动manifest/command/started时间，不能误当已完整取回。三位本轮子智能体均已落盘并完成，无人有GPU权限。
- 13:24Z最新实查：原版4K已4raw/1summary全部成功，官方均值1905.46 total tok/s、MeanTTFT12310.56ms，已进入16K1/4；依赖仍bab2，无结束文件。进度原件在本地control/progress-latest.json。当前仍只有该baseline占卡，不计算整套增益。已新增 [技术报告草稿](docs/technical-report.md)，修复candidate-usage顶端完整4aba一次应用入口，代码未改。
- 13:16Z已再次派活同三位子智能体，仅本地CPU：framework核查剩余host/cache机会；hardware依据真实prefill MM trace准备固定tile CTA grouping最短候选（未GPU/未服务集成）；systems独立审复现文档与报告。各自更新原handoff，root在途baseline不受其干扰。
- 下一步：保持原版official独占，确认实际服务/benchmark及依赖bab2持续不变，完整结束后独立审8raw/2summary与DB/KV/清理，再谈总体提升。V2 warm无收益/TTFT更差，prefix-mask单层约0.3–0.45%信号均保留未进默认。先短筛选择候选，再最终准确率/官方复现及原13eb整体对照，默认补丁尚未覆盖。
- 三项新创新均已实现并交叉审阅，隔离源码code/{bucket,growth,hidden-gather}-20261021T105930Z。bucket的105930真实两形状及后继decode逐位相同，不代表整模型数值/准确率；105526为留档工具目录hash错误，负结果保留。

## 恢复时先记住的重大经验

- 插件隔离不等于依赖隔离：旧a0c runtime会写已安装Attention。原13eb官方baseline必须是bab2，候选是54c；当前baseline期间禁止任何retained/C3导入。恢复备份与锁内操作见末尾12:27Z和dependency-restores记录。
- 冷形状的调优会伪装成回退：bucket231.619→warm220.390s，growthV2 238.113→warm221.234s，均确有新增DB配置。只补必要warm，原始失败/冷轮不能丢。
- INSTALLED不是执行证据：growth第一版实际被V2 guard排除，完整screen无效；最短constructor诊断定位后才出现真实CHECKED/DEFERRED。
- 抢占减少不保证吞吐更好：V2 full-output预算抢占1→0，warm吞吐无改善且TTFT约+7.51%，不集成、不扩大accuracy。无收益也必须保留。
- 短微测易被计时管理污染：overlap4calls表面wall+2.50%，64calls仅+0.35%且event持平略慢；prefix-mask预record事件32calls仅0.3–0.45%层信号。小代码保留，不能写成E2E收益。
- 已定位的CPU大瓶颈是具体SQL反射，不应继续泛称JIT：8步profile中SQL13.405s、建模型10.780s，已有按目标表反射方案及重复短测；完整原版官方对照仍必需。
- 本轮新探索均未覆盖默认补丁。已验证SQL+C3的103/105及两档绝对官方结果可复用；单层bitwise不能替代整模型准确率/官方重复。

## 已有工作，不能丢失

- 本地记录仓库 HEAD 起点：`c07eea1`。现有 GitHub 仓库均为只读参考；未经明确指示不要推送。
- 已选提交补丁：`patches/vllm-plugin-FL-biv150-performance.patch`，prefill attention + 确定性 histogram top-p。
- 精确主办方 math_500 Level 3 曾通过 96.2%；decode attention 候选仅 83.8%，已拒绝。完整官方吞吐复测未完成，不能声称官方得分。
- fused sampler 仅为独立候选，端到端结果有升有降，不默认启用。
- 既往 block64、batch4096/8192、关闭 prefix cache、sampler compile 筛选使用同时运行的 4K/16K 短负载。只证明该混合短负载的结果，**不足以彻底排除串行单场景收益**。
- 原始证据与说明：`analysis/2026-10-21-attention-top-p-candidates.md`、`docs/measurement-log.md`、`experiments/remote-evidence/`。

## 当前连接与设备

- 用户提供的公共连接命令：`ssh lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io -p 2224`。
- 身份使用本机已有专用 SSH 密钥；私钥不在仓库中，不输出、复制或提交任何凭据。
- 2026-10-21 本轮只读连接已成功，容器 hostname `000cf2952330`。
- **当前唯一GPU：official/20261021T122607Z-original-baseline，runner PID166637（12:26:07Z启动）**。已安装Attention为原始bab2，baseline中禁止导入retained/C3插件以免a0c写回54c。候选103/105及绝对官方成绩已有，当前原版对照尚未完成。恢复先看本文末尾并实时检查，禁止并发GPU。`ss` 不存在，使用socket检查。
- run ID 用远端 `date -u` 的实际 UTC 生成并避免覆盖，保存时钟来源。服务日志和bench文件名使用UTC+8（例如03:03Z对应11:03），不能把它们直接当UTC比较。
- 所有新实验必须在 `/workspace/experiments/minicpm-s2/` 下有唯一 UTC run ID；保留命令、源文件哈希/版本、环境、原始日志、GPU采样、退出码、结论。

## 本轮正在做

1. 已读本地 AGENTS、README、队列、候选说明、硬件分析和实验日志，恢复已有探索。
2. 并行 CPU/资料研究已分派：
   - `biv150_hardware`：硬件一手资料 → `analysis/2026-10-21-hardware-research-v2.md`。
   - `competition_systems`：整模型比赛系统层经验 → `analysis/2026-10-21-system-competition-research.md`。
   - `framework_review`：框架源码与元数据方案独立分析 → `analysis/2026-10-21-framework-review.md`。
   子智能体不拥有 GPU，不得启动远端实验。
3. 已核实远端保留候选为干净 `d60b023`，官方参考目录仍为原始 `13eb9be`。远端 `block_table.py` SHA256=`b3a6649b968fba0b48c333d7ac96e65cc713a86133cc7eef0a8399f5339ec600`。官方 benchmark SHA256=`0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565`。
4. **本轮GPU owner是主负责人，当前已启动B0串行短筛选：**
   - 远端目录：`/workspace/experiments/minicpm-s2/framework/20261021T030349Z-b0`。
   - runner PID：`93166`；服务PID在该目录的 `server.pid`，只能用实际文件核实后管理。
   - 执行脚本：`scripts/remote/run_framework_screen.py`。脚本持有 `framework-device.lock`，保持官方服务参数，先32token贪心smoke，再串行跑4K(16请求/32输出)和16K(8请求/16输出)。本轮短筛选不是官方分数。
   - B0已完成，exit-code=0，原始证据已取回 `experiments/framework/20261021T030349Z-b0/`，服务自动退出。
   - B0源目录：`/workspace/experiments/minicpm-s2/code/vllm-plugin-FL`。
   - C1已完成，exit-code=0：`/workspace/experiments/minicpm-s2/framework/20261021T031102Z-c1`，runner PID原为 `94866`。源码副本 `/workspace/experiments/minicpm-s2/code/biv150-framework-dirty-20261021`，由d60b023 archive创建，仅加候选模块和runner footer安装/退出统计。证据已取回同名本地experiments/framework目录。
   - 脚本会自动停止自己启动的服务，写入 `exit-code` 和 `finished-at.txt`。恢复后先检查runner日志/退出码和实际显存，再启动任何任务。
5. 最小 dirty-block-table 候选与CPU状态机测试已完成：`patches/framework/biv150_block_table.py`、`tests/test_biv150_block_table.py`。通过 `ContextVar` 仅在真实 `_prepare_inputs` 允许skip，dummy/capture commit保留原路径。10/10 CPU测试通过；fixture已保存进tests，不依赖tmp。root已交叉审查，远端消费者没有直接CPU表写入。尚未最终集成。
6. B0最短结果：4K16请求32输出=47.138s、1401.16总tok/s；16K8请求16输出=29.569s、4437.04总tok/s；全24请求零失败。4K median ITL146ms而P99 16.5s，存在显著离群，不能把下一轮差值直接当优化效果。两档cpu.stat各增加5次节流，当前CPU瓶颈仍未证明。C1结果后需按必要性做一次短控制复测，不能跑完整大评测来掩盖短测混杂。
7. C1结果：4K=32.903s/2007.36总tok/s，16K=28.357s/4626.75总tok/s，24零失败。**不能声明加速或正确性通过**：B0/C1单请求greedy smoke文本不同；不同服务的KV容量还相差96tokens（521840 vs521936）。C1跑测期间曾进行一次额外CPU导入检查（原意验证安装），可能干扰host负载，所以此pair仅集成证据。候选INFO日志被过滤，未导出服务内统计；退出后CPU导入证实scope_installed/table_installed均True。不要把缺少INFO等同于未启用。
8. 最短真实metadata gate已通过：`/workspace/experiments/minicpm-s2/framework/20261021T032830Z-metadata-gate`，本地证据已取回。32步真实H2D/slot_mapping状态机、3次CUDA graph replay均过；35次scope commit中21次跳过、14次完整复制。稳定表micro是最佳情况，样本变异大，不是端到端收益。
9. B0重复smoke控制已完成并清理：`20261021T033437Z-b0-repeat-smoke`，原runner PID97756，exit-code0，证据已本地取回。只3次同prompt/temperature0/seed71/32token请求，r1=r3但r2不同，基础自身已有输出不稳定。首处分歧index11：r1 `understand` vs `make`分数差0.0625，r2两词tie。不能单凭C1与B0文本不同归因补丁，但也未排除补丁风险。不扩大math500；先用同输入算子/metadata严格检查。
10. 大收益第二轮资料研究已分派：`biv150_hardware` → `analysis/2026-10-21-large-gain-hardware.md`；`competition_systems` → `analysis/2026-10-21-large-gain-framework.md`。优先减少整段重复工作、计算形状/图覆盖、有效KV容量，不再只围绕小H2D点。`framework_review`独立排查greedy差异，未找到可直接解释首个batch1请求的dirty漏标。
11. 大收益微测已经完成：`20261021T035322Z-attention-dispatch`，原PID99595，exit0；后续`20261021T035611Z-mixed-dispatch`，原PID100021，exit0。本地证据全部取回。首个失败run `20261021T035155Z-attention-dispatch`，原PID99400，exit1；原因仅留档脚本把`__pycache__`目录当文件hash，发生在任何attention候选比较前；已修正is_file，失败记录也已取回。
   - Direct 3D decode：旧generic resolver使用 `q_start//BLOCK_Q + seq` 带holes的虚拟CTA映射，BM16/GQA8下64seq会发96query CTA，约1/3早退。只改grid会漏尾部请求，不能这样做。候选同时在IS_3D constexpr分支直接seq_idx=pid0、local_qblock=0，并grid0=numseqs；2D、tile、warps、16segments、reducer均保留。`patches/framework/biv150_direct_decode.py` 和6项CPU映射proof已完成并交叉审查；GPU门槛尚待当前run结果。
   - Mixed Attention split：当前prefill的BM128/Q16/T64/2D策略会同时处理single-token decode，后者仅8/128行有效。先不改请求次序，只对天然decode-prefix混合batch在Attention边界分流；GEMM/KV写保持整批。decode走原BM16/T16/16segments，prefill保留已验BM128；归约变化有精度风险，先单层微测。
   - 主负责人已写 `scripts/remote/bench_attention_dispatch.py`，使用新run/source的独立模块副本，不改site-packages；守同device lock、端口和显存guard。先4K64/16K30 direct逐位相同门槛，再padded/zero-query/2D fallback；direct通过后测2个2048总query的mixed workload。只有时间信号明显才接服务，不做大验证。
   - 已下载实际attention/helper到 `tmp/remote-source/`，SHA分别 `54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f` / `59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1`。C1完整runner已下载，独立diff确认只增加17行footer。
12. Direct decode结果：5类有效输出（64x4K、30x16K、zero/padding、2D fallback）逐位相同，maxdiff0；4K64单层median1.6998845→1.6783500ms（约1.28%），16K30为3.0202694→3.0151076ms（约0.17%）。小候选保留，未默认集成，不能当整模型提升。
13. Mixed分流反证：D16/P2032有1.5%/3.0%单层信号；更贴近驻留并发的满chunk D63/P1985/4K仅0.46%，D29/P2019/16K仅0.70%；4K短尾D63/P127慢0.61%；16K短尾D29/P127快6.84%。prefill输出均逐位相同，但decode数值有0.00024~0.00244差异。计时不含metadata成本，所以不优先集成，仅保留tail条件候选。详细反证已写两份large-gain研究文档。
14. Native诊断已完成：前两轮无效；第三轮抓到整图，内部节点仍不可见。
   - run：`/workspace/experiments/minicpm-s2/profiles/20261021T040856Z-native-decode`；runner PID101071，实际ixsys PID见server.pid，实际vllm子PID就绪后记service.pid。
   - 源副本：`/workspace/experiments/minicpm-s2/code/native-profile-20261021T040856Z`，d60b023 archive + `scripts/remote/native_decode_profile_footer.py`，只调用ProfilerStart/Stop，不改模型/调度/采样。
   - 脚本：`run_framework_screen.py --native-profile`，ixsys包装官方服务命令，先32token单请求smoke，再64并发64请求4K/32输出的一档诊断；只在batch>=16且全1token时从第3到第8个decode step抓5步。profiler运行不作性能分数。
   - 目标：确认实际graph内kernel/形状/耗时。裸F.linear旧micro只约11ms/42层，不能自动代表服务图内FlagGems mm。下一步据真实trace决定GEMM优化，不盲目扫描。
   - runner持同device lock，自动清理自己vllm子进程并让ixsys落盘。恢复先读runner.log、server.log中的NATIVE_PROFILE_START/STOP、exit-code、真实显存；若失败修正，不能并行另开GPU。
   - 首轮exit1：ixsys将带空格的JSON参数拆开，vllm解析compilation-config失败（没有加载模型/比较候选）。已改由`server-entry.sh`用shlex.join精确保留官方argv，ixsys仅启动bash脚本。保留该失败日志，不是优化负结果。
   - 第二轮`20261021T041625Z-native-decode`，原runner101840，退出0、64请求32输出全完成并已释放设备；**诊断无效**：无START/STOP，SQLite cu_api/cu_kernel/cuda_api_data/cuda_kernel_data/cuda_graph_data均0。尽管扩展名json，ixsys输出实为SQLite。原始证据已取回`experiments/profiles/20261021T041625Z-native-decode/`。不能将该run作热点或性能依据。较可能是短输出使旧请求在prefill结束前完成，>=16的纯decode不足3步；源码footer/hash和WorkerFL动态调用均已复核，尚无证据表明wrapper被绕过。末尾EngineDeadError发生于立即abort清理阶段，不代表64请求负载失败。
   - 第三轮`/workspace/experiments/minicpm-s2/profiles/20261021T042609Z-native-decode`已exit0、清理，原runner PID103802；source=`/workspace/experiments/minicpm-s2/code/native-profile-20261021T042609Z`。仅诊断输出32→128，官方SERVER参数不变。native-events.jsonl证实EngineCore正确导入与执行，常规Start/Stop result0，5步纯decode62/62/61/61/60，native-validation.valid=true。3157 API/163外部kernel/5整graph，graph总401.683256ms、中位80.322144ms，外部kernel总13.416306ms。**ixsys没有展开图内MM/Attention节点**，所以有效抓取仍未解析内部占比，不由外部kernel占比推断整图GEMM。完整证据已取回同名本地profiles目录，CPU只读汇总脚本`scripts/summarize_native_trace.py`和summary.json保留。实际ixsys帮助没有graph-node选项，不套用NVIDIA nsys标志。
   - 最短下一诊断能力门`20261021T044007Z-graph-events`已exit1并清理，证据取回本地framework目录：CoreX的`torch.cuda.Event(enable_timing=True, external=True)`在tiny graph replay+sync后elapsed_time报`ixErrorInvalidResourceHandle`。尚不能断言所有event形式不可用，但当前最小方案失败，**不扩展成全模型插桩试错**。不改算数、没有候选比较或性能结论。
15. 后续GEMM研究：`analysis/2026-10-21-gemm-launch-research.md`。先核实实际C0配置，再独立试warps8→4、仅M>32时BM32→64；BK/stages/SPLIT_K/累加保持。候选需bitwise gate和实际图内占比。actual installed mm源码已下载 `tmp/remote-source/iluvatar_mm.py`，历史裸F.linear结果 `tmp/remote-source/linear-shapes.csv`。
16. **较大单层信号已发现**：`/workspace/experiments/minicpm-s2/framework/20261021T044807Z-decode-launch`，原PID106510，exit0并已清理；完整本地证据在同名framework目录，launcher附件为`-decode-launch-control`。固定BM16/T16/16segments/grid/reducer，仅3D warp/stage设置。转换器`patches/framework/biv150_decode_launch.py` SHA256=`b4f3698c2a1404d056f223d6ee0983dbd2f4c7be8d4677a93c18316132619708`，脚本`scripts/remote/bench_decode_launch.py` SHA256=`cfb07b0032a56491ed3c02022dd8f93934e3015a232646ec17510d1df5beaee5`。root/framework_review均已交叉审。C0五case自重复、四variant各五case与10个post-graph check全部逐位相同。实际默认4warps/3stages/warp_size64；显式w4s3与C0一致。
   - C0→w2s1单层graph中位：4K64为1.6955577→0.9973730ms（约41.2%延迟降低）；16K30为3.0243616→1.8032769ms（约40.4%）。只是单层信号，**还没有端到端或math500新结果**。
   - w4s1为1.1763884/2.1224806ms（约30%降低）；w2s3为2.0241847/3.6160500ms（倒退），不能只减warp而保留3stages。
   - 新runtime接入`patches/framework/biv150_decode_launch_runtime.py`：代理audited Triton kernel的`__getitem__`，只覆写严格BF16 MiniCPM 3D原配置的(2,1)，不写site-packages，不改2D/任何数学。source/helper双hash/vendor/backend alias守卫；CPU精确kwargs和15个排除条件pass，其他owner已独立审过。在d60独立archive接入，按短服务对照决定是否扩大准确率。此候选不与dirty/direct小补丁叠加，便于归因。
17. B0接入控制`/workspace/experiments/minicpm-s2/framework/20261021T045834Z-b0-launch-pair`已exit0并清理，原runner PID107465，source=`/workspace/experiments/minicpm-s2/code/vllm-plugin-FL`；完整证据已取回。官方服务参数不变、无profiler、seed721101，原短负载4K16请求32输出/c16为33.412913s/1976.720823total tok/s，16K8请求16输出/c8为28.237920s/4646.234497total tok/s，24零失败。**此负载不与下面长输出decode-screen横向比较**；之前native32output已经证明不能保证高并发纯decode，主性能对照改为覆盖目标阶段的matched新pair。
   - C2 source已准备：`/workspace/experiments/minicpm-s2/code/decode-launch-20261021T045816Z`，d60 archive+runtime+footer。CPU导入已确认DecodeLaunch；安装前已加backend alias与function.__globals__守卫，strict causal/无sliding等feature scope。runtime SHA256=`e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f`，`biv150_hardware`独立审通过，并用真实wrapper的fake tensors证明5shape grid/全部kwargs/reducer与微测source完全等价。
   - 可复核候选增量：`patches/candidates/vllm-plugin-FL-biv150-decode-launch.patch`（基于保留d60，不是完整基础补丁）。本轮仍未将它选为默认或声称新准确率。
   - C2`/workspace/experiments/minicpm-s2/framework/20261021T050517Z-c2-decode-screen`已exit0并清理，原runner PID108975，完整证据已取回，包括postflight.json的68MiB/0%/port_closed。上述C2 source，seed721101，`--decode-screen --require-log-marker BIV150_DECODE_LAUNCH_FIRST_SELECTED`。官方SERVER argv不变，无profiler；仅一档4K64请求/128输出/c64，64完成0失败，总8192输出token，119.224039s/2267.462181total tok/s。EngineCore有installed与first-selected标记，capture阶段已启用。**此时只有候选结果，尚无匹配B0，不能声称E2E提升。**
   - 匹配B0`/workspace/experiments/minicpm-s2/framework/20261021T051639Z-b0-decode-screen`已exit0并清理，原runner PID110830，全部证据已本地取回；原d60 source，同`--decode-screen --seed721101`，同4K64请求/128输出/c64、无profiler，64/0完成。B0为120.671052s/2240.272178total tok/s；C2为119.224039s/2267.462181total tok/s，单pair吞吐+1.2137%/耗时-1.1991%，**只是小信号未确认，未完成官方重复或新accuracy**。SERVER/seed/driver SHA256(`fc351acfc8f579844f13fc8b61a1d8800512ff6a70eda9ef6a3ccb702a02fb97`)一致。KV容量B0 521936 vsC2 521840（少96tokens），远小于当前负载驻留空间但仍明确记录；两负载各新增4次CPU节流，累计throttled_time增量并不相同。medianITL反而C2 225.9ms/B0 213.9ms，不能把单层40%当E2E40%。保留小候选，主线转向mixed框架分流。不要与045834或profiler数据混比。
18. Mixed-fast机会筛选`/workspace/experiments/minicpm-s2/framework/20261021T051426Z-mixed-fast`已exit0/清理，原PID110582；完整证据本地同名framework与`-mixed-fast-control`。脚本`scripts/remote/bench_mixed_fast_decode.py` SHA256=`e91e8d2c5882122f22cb0059186737fad577a67f77796393ac2352b041ef60c1`，whole retained2D vs split(w2s1 decode+retained prefill)。四形状单层中位：D63/P1985/4K 3.944012→3.249423ms，D63/P127/4K 2.048785→1.361700ms，D29/P2019/16K 13.796485→12.391527ms，D29/P127/16K 4.723950→3.181777ms。满chunk约17.6%/10.2%降低，tail约33%；此前慢decode split的<1%不是永久否定。prefill均bitwise/maxdiff0；decode有限但maxdiff0.002441/0.001953/0.000488/0.000488，**不是accuracy通过**；metadata normalization计时外，属于乐观上界而非E2E。
   - 框架最小集成计划已由另owner保存`analysis/2026-10-21-mixed-fast-decode-plan.md`。实际backend不保证decode-first；首版不改全局RNG/排序，只处理自然连续1token前缀D，builder一次生成子metadata，42层复用，forward两次调用原Attention（KV写/GEMM不重复）。natural prefix命中受row swap/condense影响。后备attention内gather/scatter可能保持全局token/RNG顺序，但暂未实现。pure3D w2s1 bitwise并不证明相对mixed2D bitwise；最终仍需准确率。
   - `framework_review`已完成`patches/framework/biv150_mixed_decode.py` SHA256=`a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42`，10项必要CPU tests=`tests/test_biv150_mixed_decode.py` SHA256=`c6a212564d4dced10b433fabc6d007a37730b93f7e454aaa0cf065fbf75f0fbb`。root/hardware另一owner审过，无阻断；本机Anaconda首轮libiomp冲突，测试子进程KMP_DUPLICATE_LIB_OK/OMP1/MKL1后两owner均10pass，这不算GPU证据。
   - actual backend SHA owner核实=`1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605`，新B0的backend-source.sha256留档。新suffix cu tensorstrong reference+跨producer/consumer stream的wait_stream/record_stream，无新增全卡sync；纯decode无plan，实际capture回退；普通dummy同guard可split，不猜seq_len作排除，不加runner scope。严限无sharedKV等features，None key/value回退。
   - 真实gate`/workspace/experiments/minicpm-s2/framework/20261021T054501Z-mixed-gate`已exit0并清理，原PID113390，完整证据已取回同名framework与`-mixed-gate-control`。脚本`scripts/remote/validate_mixed_decode.py` SHA256=`b6275ee86f4fb24824091e72fccd774d174247975f8189d360400f333a20351f`，root修正安装顺序、framework owner复核：先EngineArgs.create_engine_config，再重新import attention，再runtime/mixed.install，因为platform配置会sys.modules.pop/重新绑定attention。调用VLLM_PLUGINS=fl/PYTHONPATH原d60 source。
   - 真实VllmConfig/FullAttentionSpec/Builder/Impl，无权重；四mixed与独立手工split整张（含padding sentinel）bitwise/maxdiff0，每次fast_decode_launches==1，输出alias相同、prefill相对whole2D仍bitwise。whole2D→split decode差异最高0.00341796875（真实KV update后），仍未accuracy通过。
   - crossstream consumer_registered=true，suffix强引用存活、删除metadata/plan后且consumer sync前Python对象确实释放true；allocator churn没复用旧地址，不能把此样本说成穷尽allocator竞态证明。puredecode无plan、eager与1次graph replay均逐位相同。预检/编译API/全部原源快照在manifest/source，不依赖tmp。
19. C3 `20261021T054922Z-c3-mixed-screen`已exit0并清理，原runner PID113884，原EngineCore114061；全部证据已取回本地同名framework目录。source=`/workspace/experiments/minicpm-s2/code/mixed-decode-20261021T054922Z`，d60 archive+原e5runtime+原a129mixed+两段ModelRunner footer。官方SERVER不变，同seed721101、同`--decode-screen`4K64请求128输出/c64，无profiler。两安装marker和capture中的fast first-selected均存在。
   - 64完成/0失败，262144输入/8192输出token，117.259174s/2305.457148 total tok/s。相对matched B0约+2.91%吞吐，相对C2约+1.68%，**仍是单次未确认信号，不是稳定收益/官方分数/accuracy通过**。medianITL213.673ms，B0为213.860ms。C3 KV521936tokens与B0相同，C2少96tokens；其他运行差分由报告详细记录。自然prefix命中未量化，安装marker不等于每步均split。
   - 当前无GPU job。新主线查明decode graph约80ms与服务低输出吞吐之间的差距：CPU/JIT/形状/同步均只是待验证假设，不根据外部kernel表猜图内占比。framework_review准备最短walltime诊断，biv150_hardware独立研究，competition_systems整理C3原始证据；均只本地CPU。保留C2/C3小候选，暂不扩成math500；最终默认集成仍需新accuracy与官方复现。
20. 新大收益线索（尚未设备验证）：已将native trace的只读SQL提取保存`experiments/profiles/20261021T042609Z-native-decode/host-gaps.json`。5步形状62/62/61/61/60，同shape graph起点间83ms，换shape间1.898s/2.793s；API窗口7.766s而graph总0.402s，已见API调用总耗时不足解释空档。实际安装FlagGems `index.py` SHA和源码已取回`tmp/remote-source/decode-gap/`，arg_key含完整input shape，首次shape生成/exec新的Triton module，且存在autotune。更可疑的是runner `_prepare_input_ids` 在请求退出/reorder时的prevIDs gather+scatter；hidden_states通常padded64，不能仅凭输出active数变化归因那里。
   - 准备唯一bounded host-profile（非性能对照）验证归因：只8个puredecode step cProfile+方法walltime，不加GPU sync/改RNG/改服务参数。脚本`run_framework_screen.py --host-profile`，footer由framework owner准备。hardware owner准备独立整数gather→scatter融合候选以消除动态input-shape编译，保留原CPU调度/H2D/unchanged fast path；未GPU/未集成。另owner审阅后先最短正确性gate。
21. host-gap `20261021T061506Z-host-gap`已exit0/valid=true/清理，原runner PID116384；control为同路径`-control`，source=`/workspace/experiments/minicpm-s2/code/host-gap-20261021T061506Z`。精确d60 archive+单LF+`decode_gap_profile_footer.py`，footer SHA=`f1ca51128d771963a989f97e96c9883a24af25077283b764de6163f2eb2dfaf0`，root审过、4项stdlib CPU proof通过，framework owner快审launcher/runner通过。官方SERVER参数不变，seed721101、4K64请求128输出，仅八步CPU profile；不能与B0/C2/C3作速度比较。06:21:40Z postflight证实68MiB/0%/端口关闭；完整本地下载进行中。
   - **已证实更具体根因是调优缓存数据库反射，不能继续泛称JIT主因。** 八步62/62/61/61/60/60/59/59，wall13.9476s/threadCPU13.9441s；`_prepare_input_ids`13.446s、SQL get_config13.405s、get_sql_model/build_sql_model_by_db四次10.780s、automap.prepare9.115s、schema.reflect6.229s。四个动态index inputshape63/62/61/60的wrapper各约3.34s。这是profile诊断归因，不是性能分数。完整pstats/walltime/source快照保存；结束后另读实际models/sql.py并保存SHA供更通用框架缓存方案研究。
   - hardware融合整数候选`biv150_async_token_update.py` SHA=`1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc`，transformer=`e5a84a3cd90a81ec7134a3646b36921454be647ba1cb2a1936460c849a2daf8c`，生成runner=`ce1860c89760c851c2f6b3bb4c35dd334e01e7927844c5460ec35f407633fdbc`。6CPU proof通过，root/framework另一owner交叉审无阻断。保留原CPU映射/两indicesH2D/unchanged快路径，只实现一次动态int32 gather→scatter；无FP/RNG修改。competition owner正准备真实_prepare_input_ids最短GPU gate，尚未GPU验证或默认启用。
22. async-token gate `20261021T063353Z-async-token-gate`已exit0/清理，原controller PID118453，全部证据已取回本地同名framework与control目录。12个原/变换实际方法case全部整storage逐位相同，padding/stride洞/H2D调用均保留，5类非法CPU映射launch前拒绝；62/61/60固定地址/dtype/stride样本cache均只有1个相同entry（不是全局一kernel证明）。无权重/服务/性能分数，也不是新accuracy。独立整数融合候选保留，不叠SQL短测。
23. **当前唯一GPU job：`/workspace/experiments/minicpm-s2/framework/20261021T064632Z-sql-reflection-screen`，runner PID119292**，control同路径`-control`，source=`/workspace/experiments/minicpm-s2/code/sql-reflection-20261021T064632Z`。d60 archive+`biv150_sql_reflection.py` SHA=`ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e`+footer默认install；不叠C2/C3/dirty/direct/fused。只把actual FlagGems SQL静态反射实现改为SQLite当前name表，其他engine/vendor回退；配置行/keys/调优结果和缺表语义保持，源码guard=`6dc19cb...`。两owner独立6项真实SQLAlchemy CPU gate通过（多表只目标、缺表后新增、quoted/FK、跨DB并发、actual get/put配置等）。方案`analysis/2026-10-21-sql-reflection-plan.md`与完整版权fixture已保存。
   - 官方SERVER不变、同seed721101、同4K64请求128输出/c64，无profiler；`run_framework_screen.py --decode-screen --require-log-marker BIV150_SQL_REFLECTION_INSTALLED`。新driver只额外留档SQLsource/SQLAlchemy版本，待结果后先评估大信号再最短matched复核，不混用profile或声明官方得分。先查看exit-code/server.log/真实设备，再启动任何后继GPU。

## 已发现的候选线索（尚未证明提速）

- `experiments/profiles/a3-hist-top-p-profile/decode/trace/rank0.1792531794497726472.pt.trace.json.gz` 含每步 `[54..56,8192]` int32 block-table H2D，约1.8MiB；单次拷贝设备时间示例69.473微秒。
- 官方 vLLM `v0.24.0/vllm/v1/worker/block_table.py` 的 `commit_block_table` 每步调用 `copy_to_gpu(num_reqs)`，即上传所有活动行的完整131K上下文容量。
- 候选：只在 block table 变化时上传，或缩小上传有效列；必须处理 add/append/move/swap/clear、行复用、异步CPU buffer生命期、图捕获的固定指针/stride，不得在没有实际证据时宣称端到端收益。
- 日志 KV 容量约521936 tokens，使16K负载只能同时驻留约30条；需要区分物理容量瓶颈、graph占用和重计算。
- 已验证 cgroup v1：quota600000 / period100000=6核；累计nr_periods339885、nr_throttled888，不足以断言当前CPU瓶颈，按短负载前后差分判断。
- 不要按官方并发64硬编码砍掉更大 graph；不能用评测特化方式制造收益。先测真实graph内存/运行成本。

## 恢复后下一步

1. 读取远端 `/workspace/vllm-plugin-FL` 和候选 worktree 的 HEAD/status，实际 Python import 路径、已启用补丁；核实官方基准脚本哈希。
2. 只读采集 cgroup、设备、端口；确认无其他 GPU owner 后再启动唯一服务。
3. 以已通过96.2%的保留实现作为本轮共同起点；用同参数串行、无profiler、不同seed的短负载，明确区分筛选与官方分数。
4. 用 trace/source 选择最小框架改动；交叉评审和正确性后做相同负载A/B。无收益也写记录。
5. 每个里程碑更新本文、实验目录和结论。最终集成仍需独立评审、准确率与官方复现门槛。

## 2026-10-21 07:16Z 恢复与 SQL 短测结果

- `20261021T064632Z-sql-reflection-screen` exit0，06:48:35Z已完成；原始证据取回本地同名framework与control目录。64请求零失败，262144输入/8192输出，43.19865510286763s，6257.972600217696 total tok/s，median ITL129.494255ms。KV521840；实际SQLAlchemy2.0.48（本地CPU gate版本2.0.43）。相对旧基线只是强信号，先补当前同driver控制，不声称官方得分或准确率通过。
- 07:15:47Z实测68MiB/0%/9031关闭；postflight已保存远端。当前唯一GPU job是 `/workspace/experiments/minicpm-s2/framework/20261021T071554Z-b0-sql-pair`，runner PID121834，control同路径`-control`，原d60 clean source，当前相同driver/seed721101/decode-screen，无profiler。`scripts/remote/launch_sql_pair_baseline.sh`。必须确认完成与设备释放后再启动后继。
- 用户继续授权多子智能体、多查资料；已恢复三位现有owner，CPU/文档/公开资料并行，不另启GPU。

## 2026-10-21 07:22Z 匹配基线已完成，SQL 重复中

- `20261021T071554Z-b0-sql-pair` exit0，07:20:51Z完成：120.4714753809385s/2243.983475301355 total tok/s，64完成0失败，262144输入8192输出。KV521840，与064632 SQL完全相同；同当前driver/seed721101/官方SERVER/硬件/包版本，候选源码仅预期SQL实现差异。新基线也复现旧基线约120s，排除仅旧driver造成强信号。原始证据取回本地同名framework及control。
- 07:21:53Z postflight68MiB0%/9031closed。**当前唯一GPU job**：`/workspace/experiments/minicpm-s2/framework/20261021T072153Z-sql-reflection-screen`，runner PID123165，control同路径`-control`，source=`/workspace/experiments/minicpm-s2/code/sql-reflection-20261021T072153Z`。使用原SQL launcher/driver/code/seed做最短重复；不添加其他候选。此前064632已结束。
- 下一步：确认重复性与清理，审查代码交付delta；强信号稳定后才跑官方math500 Level3准确率门槛。framework owner准备独立accuracy runner，原screen driver保持不动。

## 2026-10-21 07:25Z SQL 重复已通过，准备准确率门

- `20261021T072153Z-sql-reflection-screen` exit0，07:23:56Z完成，43.09057237813249s/6273.6692756764005 total tok/s，64/0、262144in8192out、medianITL124.503668ms；KV521840同前两run。07:24:45Zpostflight68MiB/0%/9031closed。全部raw/control取回本地。
- 同driver/seed/SERVER/包和KV的SQL两次43.199/43.091s对新B0 120.471s为强重复短测信号，约2.79倍吞吐；**不是官方分数，尚无新准确率**。共享持久调优库前后无快照，不能断言初态逐byte相同，更不能外推全新空库收益。
- SQL delta `patches/candidates/vllm-plugin-FL-biv150-sql-reflection.patch` SHA2825325e926024572e744c47125c85ffbbb306fa9bd95c5c36ef78ed3bf34bee，另一owner在原13eb+retained patch scratch应用及逆向检查通过；runtime仍原ad84。独立delta尚未选为默认。
- 当前设备空闲。下一步确切SQLAlchemy2.0.48 CPUgate，然后独立官方accuracy；准备CPU readonly SQLite backup/指纹留档，绝不删改原调优库。

## 2026-10-21 07:33Z 下一项最短组合筛选

- 确切环境CPU门 `20261021T072702Z-sql-cpu-gate`：Python3.12.11/SQLAlchemy2.0.48，6/6通过0.853s；完整fixture/test/runtime/命令hash/raw已本地取回。无GPU调用。
- accuracy runner准备期间，根据SQL后新收益基数，先最短SQL+C2组合筛选：**当前唯一GPU job `/workspace/experiments/minicpm-s2/framework/20261021T073309Z-sql-decode-screen`，runner PID124917**，control同路径`-control`，source=`/workspace/experiments/minicpm-s2/code/sql-decode-20261021T073309Z`。
- d60+原SQL ad84 +原C2 e5f6，仅两个原footer；不含mixed/C3/dirty/fused。同screen driver22a076...、官方SERVER、seed721101和4K64x128，需first-selected marker。此项决定是否值得将已逐位相同的launch调整随SQL进入较长accuracy，不能用旧C2的小收益直接推断新收益。
- 在负载前只读备份实际 `/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db` 到control/db-before。已确认启动shell无FLAGGEMS_DB_URL/CACHE_DIR覆盖、installed triton源码3.6.0；其dist名不是triton，importlib.metadata.version('triton')失败不能代表未安装。helper `snapshot_tuning_db.py` SHA0f2a57...，mode=ro/query_only+backup，不删改原缓存。后置snapshot待服务结束后采集。

## 2026-10-21 07:37Z 官方准确率唯一任务已启动

- `20261021T073309Z-sql-decode-screen` exit0，07:35:11Z完成：41.15406773984432s/6568.876780514884 total tok/s，64/0，262144in8192out、medianITL92.260662ms。KV521936比SQL-only多96；约4.7%增量只是单次信号，非稳定/官方得分。SQL+C2交叉审无安装冲突，两个installed及FIRST_SELECTED均有。07:35:58Z68MiB/0%/9031closed；原始证据及DB before/after正在取回。
- **当前唯一GPU job：`/workspace/experiments/minicpm-s2/accuracy/20261021T073644Z-sql-decode-level3`，runner PID126107**，control同路径`-control`；source仍上述 `code/sql-decode-20261021T073309Z`。禁止启动其他服务、micro、benchmark或profiler。
- `scripts/remote/run_accuracy_gate.py` SHA35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54，经root/competition owner审查、3必要CPU合同检查通过；`launch_accuracy_gate.sh`保存控制命令/PID。准确率使用原始official script SHA6e045c1cda5a6379ddff1bf7c41ab1e4cbaaddd51b2ca9b4b1d2a92cfa8bb5f4，不改temp1/top_p.95/max32768/Level3/batch8/timeout3600。
- 归档完整plugin/安装关键源码/模型配置/公开dataset与脚本哈希，服务前后readonly SQLite backup，独占lock、保存GPU采样、退出清理owned process groups。默认外层监管6h不改官方单请求timeout。result的accuracy_gate始终unassessed，**exit0不是准确率通过**。
- 验收需105唯一question_id及pred/review对齐、无请求/评测错误，accuracy二值求和≥100/105（至少.95）；统计max_tokens截断，不强制0（旧通过a8有1次）。先看exit/result/eval log，结束后另用ixsmi和socket检查68MiB/0%/closed，不把仅free>=30000的runner postflight当完整无残留证明。

## 用户补充：优先直接上卡（2026-10-21）

- 用户明确澄清“上卡验证”：允许直接真卡验证；如果前置验证比上卡本身更麻烦，就尽快上卡，不要为准备/证明搭建过重流程。
- 后续保留比赛合规、设备独占、必要正确性和清理检查；有可运行方案优先最短真卡实验，以真实结果决策。停止无新风险依据的重复CPU测试或过度验证框架。
- 当前仍为073644 SQL+C2官方accuracy唯一GPU任务，未取消也不并发。最近读取约32/105进行中；结论尚未出来。

- 073644 accuracy最近读取98/105、无ERROR行，尚未结束。联合delta已保存 `patches/candidates/vllm-plugin-FL-biv150-sql-decode.patch` SHA66099c14c30dd8ee0664df7f0247c8c568f18eaa99faa5737fd4203025299e65；直接接retained，不能先叠两个独立delta。应用后runner SHA7ddf885ac0fc95af291a67f7e6289224af00ccdde7cbf286deb5302780bd6953与073309控制SHA完全一致；默认performance.patch未改。
- 下一项串行上卡脚本已准备 `scripts/remote/launch_sql_mixed_screen.sh`，复用已验证原SQL/C2/mixed代码，不新增复杂前置测试；必须待准确率服务完全清理后再启动。其mixed数值相对whole2D有差异，不能继承SQL+C2准确率。

## 2026-10-21 08:07Z 准确率通过，mixed 已上卡

- **SQL+C2 官方准确率通过：101/105 = 0.9619047619（报告96.19%）**。`accuracy/20261021T073644Z-sql-decode-level3` exit0，评测07:37:39Z→08:05:12Z，runner08:05:16Z退出。官方原命令，105唯一Level3题，105 success，零transport/评测错误；104正常stop、1题达到32768输出上限（index101），空答案/提取为空均0。只读验收 `accuracy-review.json` 已保存；不是吞吐分数。
- 08:06:29Z完整postflight68MiB/0%/9031closed、无进程。完整run压缩包 `accuracy/...-control/evidence.tgz` 正下载并解压本地。报告SHAae8a6878b96efd6bbb7c608fb5b2660d0e1f1cb680d91a9d911b7e6cd83bdc05。组合delta66099c...对应的实际source/runnerhash已核实，不替换旧默认patch，仍缺官方吞吐复现。
- **当前唯一GPU job：`/workspace/experiments/minicpm-s2/framework/20261021T080656Z-sql-mixed-screen`，runner PID129471**。control同路径`-control`，source=`/workspace/experiments/minicpm-s2/code/sql-mixed-20261021T080656Z`；d60+原SQLad84/C2e5/mixeda129+原安装footer，原screen driver/seed/官方SERVER。直接复用已上卡过门实现，不增繁琐前置验证。SQL+C2通过不能自动给mixed数值分流背书；先看短测收益。

## 2026-10-21 08:11Z 本轮真卡结果与最新恢复点

- `20261021T080656Z-sql-mixed-screen` exit0，08:08:59Z完成，39.16018311912194s/6903.338505278714 total tok/s，64/0、262144in8192out、medianITL94.862198ms。KV521936同SQL+C2；相对SQL+C2 41.154068s为约5.09%吞吐增量单次信号，保留但未确认稳定、未有mixed新accuracy。全部raw/control/DB快照取回本地同名framework目录。
- **当前无GPU任务**：08:10:57Z最后真实postflight68MiB/0%/9031closed/无进程，见080656/postflight.json。恢复时仍应实时检查，不能仅信历史空闲。
- 已正式通过准确率的新增版本是SQL+C2（101/105，96.19%，105success/0error），联合delta66099c...；不是SQL+C3。原默认performance.patch保留不覆盖，两个新组合均有独立源码/命令与证据。
- 最新优先顺序：直接最短真卡验证16K代表负载及mixed增量可重复性；值得继续再对mixed跑独立accuracy。SQL+C2可作为已过accuracy的主线基点，仍须原官方4K/16K benchmark复现才能声明官方吞吐成绩。官方脚本本身4次/丢首轮，禁止改脚本减少轮次；短筛选与其分开。
- 资料研究结论已落盘：next-framework-research、prefill-graph-feasibility、memory-lifecycle-feasibility。已有prefill Inductor编译；暂无>1GiB可回收内存证据，不为这些低证据路线追加复杂前置验证。用户明确允许直接上卡，保持单卡串行与必要门槛。

## 2026-10-21 08:30Z 继续真卡16K对照

- 用户要求继续自主工作。**当前唯一GPU job：`/workspace/experiments/minicpm-s2/framework/20261021T083031Z-sql-decode-context16k`，runner PID131764**，control同路径`-control`，source原`code/sql-decode-20261021T073309Z`（runner7ddf885...，原SQL+C2）。08:30:20Z启动前68MiB/0%、9031关闭。
- 新screen只增加独立`--context-screen`负载分支与manifest字段，官方SERVER不变：16384输入/128输出/32请求/c64/seed721201，无profiler，仍32token smoke一次，负载timeout240s。后继SQL+C3使用同一新driver；不会拿新driver的16K数据与旧4K当同档比较。launcher为`scripts/remote/launch_context_screen.sh`。
- 短负载触及容量边缘，但不等价官方1024输出/128请求多波次。若必要，仅把32req输出增至1024做最短后续；避免用128输出短筛倍数推官方成绩。
- 官方两档原脚本完整字节SHA0813eba...已再次取回`tmp/remote-source/benchmark_throughput_serve.py`。本地部分reference b667是CRLF差异，不将其误当原始hash。官方4轮/丢首轮、吞异常可能exit0，要验8raw/2summary而非只exit码。独立owned official runner准备中，GPU尚未运行官方吞吐。

## 2026-10-21 08:35Z 16K基点完成，mixed同档运行

- `20261021T083031Z-sql-decode-context16k` exit0：131.73937312606722s /4010.8282547721406 total tok/s；32成功0失败，524288输入4096输出，medianITL394.592467ms，KV521840。完整raw/control/DB快照取回本地。08:34:54Z68MiB/0%/9031closed/无进程。
- **当前唯一GPU：`/workspace/experiments/minicpm-s2/framework/20261021T083455Z-sql-mixed-context16k`，runner PID133045**，source原`code/sql-mixed-20261021T080656Z`。同新driver/seed721201/16K32req128out/c64/官方SERVER/no profiler。control同路径`-control`，其源码仍原SQL+C2+mixed。
- 官方owned runner `scripts/remote/run_official_gate.py` SHA79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579已两owner审查：原script0813...、固定官方两档、四轮丢首，8raw/2summary、成功数/tokens/finite和按原第2–4轮均值核对，不重写CSV。正式吞吐尚未启动。历史完整4K四轮约47m53s仅作运行预算，不能据短筛2.79倍外推正式分数。

## 2026-10-21 08:47Z 16K短测信号与长输出复核

- `20261021T083455Z-sql-mixed-context16k` exit0，120.67024365533143s /4378.7431266751655 total tok/s，32成功0失败，524288输入4096输出，medianITL348.880037ms；全部raw/control/DB快照已取回本地。08:42:11Z完整postflight68MiB/0%/9031closed/无进程。
- 相对083031 SQL+C2的131.739373s为约9.17%吞吐单次信号，不能全部归因mixed：C2 KV521840 vs C3 521936（多96）；083031首次16K使调优库479表17982行增至481表18052行。保留准确原始结果，不把冷配置扩展成本算作稳定优化。
- **当前唯一GPU：`/workspace/experiments/minicpm-s2/framework/20261021T084659Z-sql-decode-context16k-long`，runner PID134721**，control同路径`-control`，source仍原`code/sql-decode-20261021T073309Z`。
- 直接最短长输出对照：16384输入/1024输出/32请求/c64/seed721201，官方SERVER不变、无profiler。新`--context-long-screen`只改独立screen分支，driver SHA28d6a03419c4f8bf3b4b50b79edc63343afd601912ef0fc9775957b1dba113b7，launcher SHA565da3fca67cf624c7f9a114e61c540e5322567fcdc6bde2ffb0f64d0f8ad334；外层监管仅此分支900s，其余240s。framework编写、root精确diff审查完成，无额外繁琐前置门槛。
- 后继串行使用相同driver/seed/shape跑原SQL+C3。每轮比较DB before/after；新cache可能改变初态时记录混杂。长输出筛选仍不替代官方128请求/4轮原脚本，也不替代mixed独立accuracy。

## 2026-10-21 08:54Z 长输出基点完成，同档mixed运行

- `20261021T084659Z-sql-decode-context16k-long` exit0，236.02503280621022s/2360.156435005664 total tok/s，32/0，524288输入32768输出，medianITL92.250940ms。原始raw/control/DB快照已取回本地同名目录；完整postflight确认设备释放后启动下一项。日志可见prefill结束附近再次autotune警告，DB前后新增情况待读取，不能预设相同初态。
- **当前唯一GPU：`/workspace/experiments/minicpm-s2/framework/20261021T085302Z-sql-mixed-context16k-long`，runner PID136129**，control同路径`-control`，source仍原`code/sql-mixed-20261021T080656Z`，driver28d6a034.../seed721201/16K1024out32req/c64，官方SERVER不变。
- 用户确认是否接续上一AI：已明确接续交接记录与083455在途实验，复用原073309/080656候选，保留所有原成果/负结果，不重新开始。不重做已有101/105准确率，mixed自己的数值变化仍需独立准确率。
- 后续正式总体加速比应选最终candidate与原13eb baseline各一轮完整官方两档4次；不能拿不同retained d60源或只有4K完整的历史结果当完整matched baseline。当前尚未启动正式吞吐。
- 交付候选已补齐但未选默认：`patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode.patch` SHA4b3e2e52b01d04a0f0477ae4e9b8dc3fed3c1f721360af3bbe6b01014572bbba，直接接retained补丁，不能先叠SQL+C2 joint；ad84/e5f68/a129三模块及e155a166 runner逐byte匹配080656。framework制作、hardware独立封装重建审查通过；仍待mixed独立accuracy。官方launcher `scripts/remote/launch_official_gate.sh` SHA41bd5830d79385fed1a6afaca2cd4c288e6ba8f49206d4afa6228ef0251c8ccf准备完成，未启动official。
- 084659长输出DB已证实481表18052行→483表18119行（+2表67行），物理a269d355...→a996189f...，KV521936。085302若有信号先补一次warm SQL+C2即可，无需整套重跑；未见preempt关键日志不是零preempt计数证明。

## 2026-10-21 08:59Z 长输出mixed完成，仅补warm基点

- `20261021T085302Z-sql-mixed-context16k-long` exit0，220.3681204696186s/2527.8429512076336 total tok/s，32成功0失败、524288输入32768输出、medianITL92.263439ms。完整raw/control/DB快照已取回本地同名目录，full postflight确认端口关闭/无设备进程后才启动后继。
- 第一轮long SQL+C2 236.025s vs mixed220.368s为约7.10%单次吞吐信号；C2首次长输出有新增配置，先不要把差值归因候选。最短补一次已热SQL+C2，不整套重跑、不清库。
- **当前唯一GPU：`/workspace/experiments/minicpm-s2/framework/20261021T085855Z-sql-decode-repeat-context16k-long`，runner PID137480**，control同路径`-control`，source原073309，same driver28d6a034/seed721201/16K1024out32req/c64/官方SERVER/no profiler。待该次结果和DB/KV比对决定mixed独立accuracy，SQL+C2已有accuracy不重复。

## 2026-10-21 09:06Z warm复核仍有信号，mixed独立准确率已启动

- `20261021T085855Z-sql-decode-repeat-context16k-long` exit0，231.32209699694067s/2408.140023075129 total tok/s，32成功0失败、524288输入32768输出、medianITL92.238018ms。完整raw/control/DB已本地解压。末段一次只读HTTP metrics观测preemptions_total=1.0已保存metrics-observed.prom及UTC，不是最终完整计数；日志未告警不能宣称0preempt。
- mixed220.368120s vs warmC2 231.322097s仍约4.97%吞吐信号，值得进入独立准确率门，不再重复整套短筛；KV及DB最后审计待读本地证据。该结果仍不是官方吞吐分数。
- **当前唯一GPU：`/workspace/experiments/minicpm-s2/accuracy/20261021T090505Z-sql-mixed-level3`，runner PID138867**，control同路径`-control`；source原`code/sql-mixed-20261021T080656Z`，原ad84/e5f68/a129/e155runner不变。使用已审run_accuracy_gate.py35d30...与原run_math500_level3.sh6e045...，官方SERVER/Level3/temp1/top_p.95/max32768/batch8/timeout3600不变，无profiler。SQL+C2已经101/105，不重跑；mixed目前结果未知，不能继承旧准确率。
- 准确率结束后：先确认exit/105唯一IDs/所有requests/reviews/阈值≥100正确与归档源码，运行scripts/review_accuracy_gate.py对实际时间戳目录审计；再真实ixsmi+socket检查并封存raw。后续再考虑选中版本对原13eb完整official两档4轮各一次总体比较。不要在本accuracy活跃时启动任何其他GPU。
- 新研究只CPU并行：硬件owner读真实SQLite副本发现083031新增四投影MM M=952（4best+60benchmark），084659为M=259；新index是BF16→BF16，更像hidden_states[logits_indices]，不能误归async-token int32融合。下一框架假设为通用mixed尾步M分桶减少形状调优；两owner仅研究切口/正确性/官方丢首轮后价值，未改源码或上卡。
- 最终warm pair审计补充：085855 SQL+C2 KV521840，与085302 mixed完全同；其DB before=after483表18119行，schema/logical/physical三hash与mixed before/after完全相同（物理a996189f...，实体SHA已两owner复算）。已去掉已知DB/KV初态混杂，仍只能报单次约4.97%信号。metrics观测UTC09:03:34.629064Z，累计preemptions至少1，不能推断mixed零预占。
- 09:06:40Z读取090505 server.log已真实进入官方chat/completions生成，8请求运行，非仅提交启动命令；评测在math500-level3子目录，控制日志名evaluation-launcher.log，尚无exit-code/准确率结果。独占PID138867仍由root负责，driver自带退出清理与DB-after。

## 2026-10-21 09:11Z 正式对照准备与准确率进度

- 090505唯一mixed accuracy实际进度36/105，evaluation-launcher.log暂无ERROR行，未完成/未判通过；不能使用进度条预估当可靠结束时间。
- 原13eb参考仓库只读git archive到隔离`/workspace/experiments/minicpm-s2/code/official-base-20261021T091033Z`，base-revision=13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0；runner446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64，官方benchmark0813eba...；不含retained或任何新候选补丁。没有修改/推送原仓库。
- 已上传official driver79119f...以及launcher新SHAa4fac213238e13ecb9ef78af9b7cfc419efce90308c0a04c9583c6172cac78c8；root最小修改、competition快审通过：第三个可选marker参数未提供时仍SQL marker，显式空串时省略marker供原13eb基线使用，服务models就绪检查不变。
- 后续候选命令：`bash /workspace/experiments/minicpm-s2/scripts/launch_official_gate.sh <selected-source> <label>`。原13eb命令需第三参数显式空串：`bash .../launch_official_gate.sh /workspace/experiments/minicpm-s2/code/official-base-20261021T091033Z original-baseline ''`。都只能在当前accuracy完成且设备释放后串行启动。尚无正式吞吐run。
- 09:14Z accuracy进度59/105，暂无ERROR行；这不是正确率59/105，最终需独立审核105评测记录与报告。
- 下一框架候选研究已独立保存：`analysis/2026-10-21-mixed-token-bucket-plan.md` SHAad5ffe15663acb267b4035939b5a49c2b49dd69a42a4a21835d127f3b475af79；`analysis/2026-10-21-mixed-token-bucket-source-review.md` SHA4f96dead654da2f5bc93c8fb02e746b4cafae45fca55ed9bc3ec7c1c4d83d1c5。仅设计、未实现/未上卡；通用mixed NONE M>=256、round128<=max，真实attention M/采样N不变，补inputID尾合法值/保留positions0及slot-1。尾attention out未初始化、MM数值/调优/峰值与官方skip1后冷收益消失风险必须按文档处理。不要因研究文档存在就把它算已启用优化。
- 本地报告helper `scripts/analyze_benchmark.py`已最小修复先过滤success再丢首轮的问题：现按原case顺序先丢首轮，再筛可用数据，少于3轮明确incomplete/CV不足N/A；不是正式gate替代。SHAadf1fd59181b4649fd20ff9565faef4d62119121f4ff6c4efeb9872950994c0d，competition实现/root diff审阅，2个针对性轻量检查与既有完整CSV数值不变核对通过；原始CSV/official benchmark/现运行器未变。
- 09:19:31Z accuracy进度97/105，evaluation-launcher.log暂无ERROR行；剩余题继续按官方32768输出上限运行，不提前终止。
- 数据留档提示：各control/db-before、db-after的snapshot.sqlite实体已下载且做SHA复算。*.sqlite被.gitignore忽略，rg --files默认不显示不代表文件缺失；用Get-ChildItem/Test-Path或pathlib直接检查，避免重复下载/误判证据不存在。

## 2026-10-21 09:30Z mixed独立准确率通过，正式两档吞吐已启动

- `accuracy/20261021T090505Z-sql-mixed-level3` exit0并清理：evaluation09:06:00.651727Z→09:22:12.738286Z，runner09:22:16.581155Z结束。原始评测目录`math500-level3/20261021_170606`。
- 只读reviewer验收 **103/105=0.9809523809523809，98.10%通过**，105唯一Level3题/105success/0transport或评测错误/105stop/0max_tokens/0空答案及提取；不将单次随机sampling结果比101/105高视为质量提升。源归档228项hash全部验证，SQLad84/C2e5f68/mixeda129/runner e155与080656完全相同。完整run/control/evidence.tgz已下载并解压到本地experiments/accuracy同名目录，包含accuracy-review.json/source-review.json/postflight-full.json。原result.json的unassessed不重写，以独立review为门槛结论。
- **当前唯一GPU：`/workspace/experiments/minicpm-s2/official/20261021T092944Z-sql-mixed-official`，runner PID141987**，control同路径`-control`，source原`code/sql-mixed-20261021T080656Z`，launcher a4fac213.../driver79119f...，官方原benchmark0813eba...、4K与16K各4轮丢首，官方SERVER完全相同，没有profiler或smoke。此时只是已启动，尚无正式吞吐成绩。
- 恢复先看run/result.json、exit-code、benchmark.log和benchmark_results，不只看benchmark exit0；需原8raw/2summary、成功数/tokens/有限数/原第2–4轮均值核对。runner独占锁、记录PID/GPU/源/DB前后、退出清理owned进程组。正式run必须结束且确认真实设备释放后才启动后继原13eb基线。
- 原13eb后继source=`/workspace/experiments/minicpm-s2/code/official-base-20261021T091033Z`，用同launcher第三参数显式空串关闭候选SQL marker要求，不改SERVER/benchmark。当前不要启动第二服务/benchmark/profiler/micro。默认performance.patch保留，候选联合delta4b3e...已经accuracy通过，仍待正式性能复现后选择提交。
- 09:31:35Z确认正式benchmark实际已启动：benchmark PID142458、APIServer142001、EngineCore142169；benchmark.log原文RUNS4/SKIP_FIRST1/TOTAL_CASES2，当前4K4096/1024/c64/256第1/4轮，server已有真实POST请求。无exit-code/result，仍运行。后续16K由原脚本自动继续，不能另起负载。
- competition独立本地复核090505 pass103/105、105IDs/index0..104、官方config/报告、105success0error/105stop/0cap/empty0、228归档SHA及四核心exact080656均通过；accuracy KV521840，fullpostflight09:29:01.800600Z68MiB0%closed。accuracy期间DB483表18119行→489表18384行（+6表265行），只记状态变化，不外推性能；正式run会保留自己的before/after。

## 2026-10-21 10:10Z 接续官方测量，重建并行创新与持久留痕

- 用户继续授权多智能体、多尝试/多探索/多创新，并明确所有子智能体工作必须落盘供下个API使用。已建立 `docs/agent-work-index.md`，根AGENTS新增Durable sub-agent handoff协议，README及本文已加入口。
- 旧三owner本轮恢复发生模型capacity错误（hardware连续2次、framework1次、competition1次），不是方案性能/正确性负结果。父任务随后创建继承当前配置的framework_innovation/hardware_innovation/systems_innovation，未指定模型覆盖。派发范围与失败记录见 `docs/agent-work/20261021T1006Z-dispatch.md`；旧团队成果索引见 `docs/agent-work/previous-team.md`。
- 三位新agent已实际建自己的持续handoff：`docs/agent-work/framework_innovation.md`、`hardware_innovation.md`、`systems_innovation.md`，中间发现、来源/代码/哈希/反证/未解问题/下一操作及最终回复都必须写入。root维护索引，子智能体仅本地CPU/公开资料，不SSH/GPU。
- 092944 official仍唯一GPU：10:03:49Z读取原raw显示4K四轮全部256success，原summary后三轮355.88s/3683.65 total tok/s/736.73 output tok/s/TTFT4781.64ms；16K第1/4运行中。live快照已本地保存 `experiments/official/20261021T092944Z-sql-mixed-official/live-20261021T1004Z/`。systems owner独立复算所有4K summary列一致，但整体未完成/无总体分数。
- 新创新候选：framework_innovation在原设计上准备独立mixed token bucket runtime/footer，初稿已落盘，尚未设备验证/默认启用。hardware准备独立review及额外框架路线，systems研究准入/重计算/host KV方向。不得修改当前080656 source或official driver，不与官方测量并发上卡。
- actual installed KV writer只读取回 `tmp/remote-source/bucket-support/triton_reshape_and_cache_flash.py` SHAf18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb，已通知实现owner复制到持久source目录并核负slot早返回；不能只依赖tmp或公开tag源码猜实际行为。

## 2026-10-21 10:24Z 重大经验与当前自主方案

- 用户将留痕要求收敛为“重大经验写下来，按自己的方案继续”；保留统一handoff索引，在关键结论/验证/失败处更新，不为过程记录挤占实验工作。
- 官方092944仍唯一GPU，runner141987；16K第1轮128success0fail、816.56s、2728.78total tok/s，10:17进入第2/4。只读metrics观测累计preemptions6、KV97.6885%、waiting34，保存在远端该run/observations/20261021T101706Z；不是最终分档抢占计数。4K已完成，整体未完成，无matched总体增益。
- 新bucket独立代码/专用footer已经实现并两owner审阅，路径与最终版本以framework_innovation/hardware_innovation各自handoff为准；8项轻量CPU合同不等于真实tensor/KV/accuracy，作者正写两个真实M259/952无权重设备门。未改当前080656或默认补丁、未并发上卡。
- 新硬件研究反证：LibEntry热命中绕过SQL，不能把残余重复SQL当每层主因；只改LibTuner配置key不能消除exact-M Entry miss；新的BF16 hidden gather与旧int32 token融合不是同一挂点。资料及来源落innovation-hardware和其handoff。
- 调度新方向：vLLM已经有reserve_full_isl/watermark，不能重复当创新；systems owner正在actual已取回scheduler/KV/coordinator/full-attention源码上准备独立输出增长预算准入实现，不持久ledger、不改请求顺序/参数，empty-running回退防饿死。未来预算会31→29驻留，可能损TTFT，必须真测而非承诺收益。
- 设备安排：让当前正式两档完整结束并核验/清理；随后先最短bucket真实门/短screen及有条件的growth准入短screen，再决定长accuracy/正式复现。原13eb整体基线对照仍必需，但后移至候选选择后，避免先占住后续创新数小时。所有新性能/正确性结论须另有真实run ID。

## 2026-10-21 10:44Z 三项独立候选备齐，官方末轮中

- 10:40:30Z官方092944进入16K第4/4，已有7raw行，前3次16K816.56/816.36/816.37s、128success各次；整体仍运行，不能执行新GPU。
- 已实现并交叉审阅的独立候选：bucket runtime d2620ff750beb3fab97f372d64a1ec0e5550ee133cc6ca33adb8ba3f43de4605 +专用footer21074c95；growth runtime9245dd089a310620840a1c056544e66fb2dd0ea24f41ef8f0e4b22721bac7e49 +init transformerb0d55166；BF16 hidden gather runtime109905b3d276d6e4ff6cc74a7b97dfe6e8ee31a517b0ac7c4fdb163cc37ad8fd +runner transformer881f2cf2。各自只保留一项新改动，均未设备验证/未默认启用，已有CPU检查不代替accuracy。
- 已上传最短gate：scripts/remote/validate_mixed_token_bucket.py SHA12b4c421325e209aeab5eb14ba27b91250c0404d3289087252c5164b6f2cac4e（真实Builder/Impl、M259/952污染尾及后继decode，无权重/服务）；launch_mixed_bucket_gate.sh带240s外层超时，调用gate自身共享设备锁。hidden gate最终SHA93fd88ae797fe2f377bed7beb244279889881847df0497d7e347ef32e3079dd1，cache能力inconclusive不是copy错误，不能据此盲目重跑。具体CLI/源guard见各实现说明/handoff。
- 已上传prepare_innovation_source.py SHAfa61e5e2662cb465937bdc7d24e316382a30176891edeef1f79cbdb67c339983，root读审通过。只接受080656原base，精确5旧SHA/候选assets，复制到ROOT/code全新直接子目录并写完整innovation-source.json，不导入CUDA/vLLM；尚未实际远端执行。三variant的本地213文件包装检查已过。
- 后续shortscreen driver新版SHA bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9：只额外留档init+六scheduler/KV源SHA、计时区间外GET metrics before/after，负载/参数/seed/timeout不变。每一新pair基点与候选都必须用同新版，不能直接拿28d6旧screen当matched pair。当前official79119f运行器完全未动。
- 后续动作：official exit后核验8raw/2summary/清理并封存；先 launch_mixed_bucket_gate.sh 原080656source（只测试modules，无修改source），如pass再 prepare_innovation_source.py --variant bucket/growth/hidden-gather 各隔离目录，以同新版driver做最短筛选。预计优先growth16Klong（需EngineCore FIRST_CHECKED PID证明）；bucket/gather先各自最短设备门。未经positive screen不扩大accuracy；默认性能补丁不覆盖。

## 2026-10-21 10:56Z 完整官方吞吐已验收，新候选首次设备门

- official/092944已exit0：benchmark09:30:39.405817Z→10:53:36.070467Z，controller10:53:40.090413Z退出。原两档各四轮全部成功，8raw/2summary/tokens/finite/原2–4均值全部通过，无cleanup_errors。4K summary355.88s/3683.65total/736.73output tok/s/TTFT4781.64ms；16K816.48s/2729.07total/160.53output tok/s/TTFT185063.65ms。仅候选绝对成绩，原13eb matched整体增益仍待对照。
- root核验230个source归档SHA全部匹配；原CSV哈希raw55d66218c71ba061d11ccf2be6a58edf534c3eb475e0b9be9ec20bcc98f29c61、summarye913ef2ebd16fb1011e97aa01fd9e30aae99eb2c8983cb47ea94daf989b5888a。完整run/control/evidence已本地下载解压experiments/official同名目录。fullpostflight实测68MiB/0%/9031closed后才启动下一任务。
- **当前唯一GPU：framework/20261021T105526Z-mixed-bucket-row-kv-gate，controller PID151230**，control同名-control，源模块runtimee5/mixeda129/bucketd262；launch_mixed_bucket_gate.sh外层240s，gate12b4拥有共享lock/preflight/原始source/result/GPU采样。无模型权重、无服务、无profiling；两真实M259/952污染尾与下一decode验证尚待结果。当前不要开第二GPU任务。

## 2026-10-21 11:06Z 新真实门通过，增长预算匹配对照在卡

- 用户最新要求按自主方案继续，只记录重大经验；仍持有全部既有优化与失败记录。官方092944已完成并独立审计，不重跑已有103/105准确率。
- bucket首门105526 exit1，未执行任何case：import生成__pycache__后留档hash误读目录。修复两处is_file过滤，gate新SHA65fcc4de41b62ede39c0ddee67ba44e2a328cb6712e3d23491fdf5061ed63b66；第二门framework/20261021T105930Z-mixed-bucket-row-kv-gate exit0。真实M259→384/M952→1024有效Attention+整个KV以及后继32decode逐位一致/maxdiff0，污染尾不泄漏、padding操作RNG不变。不是整个ModelRunner/整模型GEMM/采样准确率证明。两轮失败/通过原始run+control均已本地解压experiments/framework；11:01:49.406136Z postflight68MiB/0%/9031closed。
- 隔离source准备工具首次因原源码内部合法JSON文件symlink拒绝而失败，未产生候选输出。root仅允许仍指向base内部的常规文件别名，拒绝越界或目录link，记录target+bytes SHA；新工具0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca。远端三隔离目录bucket/growth/hidden-gather-20261021T105930Z均已准备并完整diff核对，不改080656。
- **当前唯一GPU：framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long，runner151990**，control同名-control。原080656源，新driver bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9，原官方SERVER/no profiler/16K1024out32req/c64/seed721201。额外metrics测前后GET在客户端计时外，保留实际抢占差值；不与旧driver结果当matched pair。source完整归档，DB-before已留。11:05:46Z仍真实生成，GPU28432MiB/100%。
- 基点结束后先DB-after/实际设备清理/封存，再用相同launcher/driver/seed运行growth隔离源码。必须EngineCore FIRST_CHECKED实际PID证明准入挂点，而非仅安装日志；比较抢占差值/吞吐/KV/DB初态，若下降也完整保留。bucket与hidden gather先最短门后有条件短筛；原13eb大对照排在候选选择后。

## 2026-10-21 11:09Z 基点完成，实际growth短筛启动

- 110149新基点exit0，raw/metrics/DB-after/control已远端封存；metrics测前0→测后1次抢占，11:07:46.868216Z完整postflight68MiB/0%/9031closed。
- **当前唯一GPU：framework/20261021T110747Z-growth-innovation-context16k-long，runner153353**。source=code/growth-20261021T105930Z，原官方SERVER、同bc51driver/16K1024out32req/c64/seed721201。原080656 runner/3模块均保留，仅新增growth模块9245与general-plugin init d9e2。下一步核EngineCore FIRST_CHECKED、输出tokens/错误/实测抢占/KV/DB，并评估吞吐是否值得。
- root预审hidden-gather门发现同类目录hash缺陷，已交作者在上卡前修复，旧93fd脚本不执行；不把测试基础错误算候选失败。待作者给新SHA再上传，后续设备门保持串行。

## 2026-10-21 11:19Z growth未命中保留，hidden行拷贝门在卡

- 110149基点220.49432305898517s/2526.3961097582546total，32成功0失败/524288input32768out，实测preemptions0→1。
- 110747 growth短筛exit0，220.3689999799244s/2527.832862384218total、同tokens/32成功0失败，实测preemptions仍0→1。EngineCore153534仅INSTALLED、全日志无FIRST_CHECKED，**未证明实际执行，不能将微差当优化收益**。11:18:03.698898Z完整postflight68MiB/0%/9031closed，raw/control/DB-after已封存，完整下载进行中。
- 下一growth动作是新隔离source一次constructor真实scope descriptor/逐guard诊断，用最短smoke-only，不再先跑32req长负载；systems实现/framework独立审，原080656和105930及本轮证据不改。不凭猜测放宽scope。actual安装reserve_full_isl默认True、水位0、FullAttentionSpec有non_causal=False/headv补齐已只读核实。
- **当前唯一GPU：framework/20261021T111804Z-hidden-row-gather-gate，controller155011**。launch_hidden_row_gate.sh存精确命令/hash，原080656 runner e155、runtime1099/transform881f，新gate65cb8affd4ae08af877ccb4b4cfca6822eec5ba3f83770f39999ee677c546863提前修复目录hash，bounded380s/worker300s。无权重/无服务/不报性能，检查BF16 payload与跨流、动态specialization。
- 新并行研究只保留一项：C3 split内部decode/prefill两流重叠，整个KV写完后同源只读/输出不重叠/主流join后再O/MLP。hardware准备单层门、framework独立审，实际16SM资源争用/无并发可能使其无收益，尚未上卡。不更改在途模块/服务参数。

## 2026-10-21 11:21Z hidden拷贝门通过，整模型短测已启动

- 111804 hidden-row-gather-gate exit0/pass：四形状259/952/2048/64(62active) BF16完整位模式、形状/新storage/RNG全过；固定地址dtype/stride下动态M/N观察到同一1entry，int64、8类fallback、private负/重复/重排copy、跨流均过。不是任意indices public保证，也不是full ModelRunner/LMhead/采样验证。原source/result/worker/rawGPU+control已本地解压experiments/framework。11:20:21.548652Z完整postflight68MiB/0%/9031closed。
- **当前唯一GPU：framework/20261021T112021Z-hidden-gather-innovation-context16k-long，runner155377**，source=code/hidden-gather-20261021T105930Z，实际runner e68d6886d788a2f56d470fccaee62558d4622545eede2a59fbeb083a5264016e，新增runtime1099，保留原SQL+C2+C3。same bc51driver/官方SERVER/no profiler/16K1024out32req/c64/seed721201，对110149新基点做吞吐筛选；必须实际FIRST_SELECTED并核DB/KV/metrics，不继承旧accuracy。

## 2026-10-21 11:27Z hidden短筛未证明收益，growth最短诊断进行

- 112021 hidden整模型screen exit0，EngineCore155570真实FIRST_SELECTED；32成功0失败/524288input32768out，220.35732742911205s/2527.966764251134total，preemptions0→1，KV521936。对110149基点220.494323s/2526.396total仅约0.06%且基点KV521840少96，不能称稳定或因果收益；保留独立实现和门，不优先扩大accuracy。11:26:02.786329Z完整postflight68MiB/0%/9031closed后归档raw/control/DB。
- **当前唯一GPU：framework/20261021T112603Z-growth-descriptor-smoke，runner156773**。source code/growth-diagnostic-20261021T112402Z，仅在growth105930加诊断模块4a6eaefa0b40358307f48c586b9be7dc4a801f4b8eeeda752ff2db5275619b99及init5c11fd1f97057d9a820cb048690a8135bce41fea8d1160127c238653f181e163。两owner已审纯观察/异常兜底，trusted exact9245 AST逐29guard共享globals，无RNG/调度改动。
- launch_growth_descriptor.sh用同bc51driver --smoke-only --require-log-marker GROWTH_CONSTRUCTOR_DESCRIPTORS，原官方SERVER、无性能负载/无profiler；constructor真实descriptor足以定位scope。若全部true再仅补最多2并发请求观察waiting，不上32req定位。保存完整source/DB-before/command/所有错误，root负责结束后的DB-after/fullpost/封存。
- systems独立核110149/110747的21/22源SHA、DB四份实体三hash完全相同501表18789行；两run实际抢占均1。基点KV521840、未命中growth521936，必须保留容量差，不将无效策略微差当收益。详见原件independent-screen-review与agent handoff。

## 2026-10-21 11:35Z actual V2导致growth回退，分桶整模型筛选进行

- 112603 scope诊断exit0，EngineCore156959 actual AsyncScheduler，唯一failed guard为not scheduler.use_v2_model_runner（真实True）；其余逐guard全true、setup_errors[]，Unitary/FullAttention/42layers/16block/BF16/2KV/head128/FCFS/reserveTrue均确认。先前仅从plugin ModelRunnerFL推断V1不成立；本地fake配置合同也不证明运行时启用。原件run/control/source/DB-after/fullpost均本地解压framework，11:32:08.170110Z清卡68MiB/0%/9031closed。
- systems接续评估actual V2 placeholder/FCFS/predictor/延迟释放，若语义允许才新独立revision支持；不改启动参数、不开环境关V2、不覆盖旧9245/105930。下一次真实服务必须CHECKED marker，不能再把INSTALLED当执行。
- **当前唯一GPU：framework/20261021T113208Z-bucket-innovation-context16k-long，runner157580**，source code/bucket-20261021T105930Z（d262runtime/2107footer/runner0681），samebc51/官方SERVER/no profiler/16K1024out32req/c64/seed721201。单层/KV门已过，但physical GEMM M变化的性能/数值/accuracy尚待；首次可能新增调优cache，必须看DB再下结论。
- 两流Attention独立原型已作者+framework终审/root读审，runtime93c3124ccab9311cb98f319d9f786f7aae571f9c1d976d1a9f1d623adca378db、gate914f7eb3abee25f05af8cb1a7a78eb96ede7b8c88aaf427014e16b3f745ae291已上传，launch_mixed_overlap_gate.sh准备。仅D29/P2019/16K一个真实单层，连续不同Q/整KV/RNG/主流join正确性后4组ABBA各4calls测完整wall和regular event；未安装服务，full-model强ref峰值/纯decode graph期间reap未设计。当前bucket结束并完整清卡后串行跑此门，无实际硬件并发或收益声明。

## 2026-10-21 11:41Z 分桶首轮有冷调优，双流门的计时反证

- 113208 bucket exit0、EngineCore157777 FIRST_SELECTED actual1696→1792，32成功0失败/同tokens，231.61926844483241s/2405.0503386020355total、preemptions0→1、KV521936。DB501表18789行→506表18926行（+5表137行），schema/logical/physical均变，不能用此冷轮直接判稳定回退。11:37:27.415623Z完整清卡，原件本地已下载解压。
- 113727 overlap单层gate exit0：D29/P2019/16K、连续不同Q输出整bits/有限/padding/整KV/RNG/no-plan均pass，pending_after_sync0/peak4。4calls ABBA完整wall串行12.8991/12.8682ms、两流12.5962/12.5275ms，约+2.50%只是单层信号；**event窗口反而串行12.4282/12.4143ms、两流12.5501/12.4846ms更慢**，不证明硬件重叠加速。4calls timingEvent初次record/host管理可能摊销成wall假信号，hardware准备只增loops选项的新门，后续32/64calls一次短复核，不先服务集成。完整raw/source/result/control已本地解压。
- **当前唯一GPU：framework/20261021T113946Z-bucket-warm-repeat-context16k-long，runner159375**。原bucket105930源/同bc51/官方SERVER/16K1024out32req/c64/seed721201，无profiler，仅一次必要warm重复。113727完整postflight11:39:46.229205Z68MiB/0%/9031closed后才启动。
- growth V2新revision72d6f3822c96be028f6ab3cd818de1da6bafdb38d52a50a12633851717332803、独立init变换e5bad3d863a36d0d24bc3650c513600e23909d2224fb315bb8eb99943f8b0d9a已实现，旧9245/105930不动。仅exact builtin Scheduler/AsyncScheduler，追加actual async源hash/继承method身份及defer_block_free=False，保留future预算/其他scope。actual源码证V2仅分配后组装payload/PP1 next-step cadence，Async先推进computed再加placeholder，当前max future仍覆盖；已一项必要合同过，待framework独立终审再新隔离source。后继要新DB506同条件基点，不把旧DB501当matched。

## 2026-10-21 11:48Z 两个小信号留档，不扩大；V2匹配对照在卡

- 113946 warmbucket exit0，220.39044175297022s/2527.586929674515total、32/0同tokens、preemptions0→1；DB before=after506表18926行，三hash相同。原件已本地解压。相对旧501库基点约0.05%不应报收益；原冷轮231.619的明显额外开销随warm消失，但仍未证明分桶改善正式skip1后的吞吐。代码/门/两个run保留，不优先大accuracy。11:45:52.843157Z fullpost68/0/closed。
- 114553 overlap64 gate exit0/correctnessalltrue/pending_after_sync0/peak9。新ab1脚本及方法v2，ABBA64calls wall串行12.4656046/12.455694ms vs两流12.4184280/12.4157882，median12.4606493→12.4171081约0.3494%；event median12.4091864→12.4141359基本持平略慢。原4calls表面2.50%大幅缩小，不证明硬件并发或E2E收益；保留未确认微小host信号，不服务集成/不扩大accuracy。新旧raw/源码/method/commands均本地解压，重要经验是短窗口可被timingEvent惰性初始化/管理成本显著污染，不能只看wall单数。11:47:13.030618Z fullpost68/0/closed。
- **当前唯一GPU：framework/20261021T114713Z-growth-v2-matched-base-context16k-long，runner161064**，原080656源码，新bc51driver/官方SERVER/no profiler/16K1024out32req/c64/seed721201，新库506状态。此轮是growthV2所需matched新基点，不能混原501库结果当严格pair。
- 新V2已作者+framework/root交叉审，必要actual V2 placeholder合同独立通过，无旧suite重复。隔离source已CPU准备code/growth-v2-20261021T114249Z，仅从原080656新增72d6f3822c96be028f6ab3cd818de1da6bafdb38d52a50a12633851717332803 runtime与init830ff5805cb4d989cbc9225ef423720a6e261754ba180d2ca495e76434d7e421，完整source/hash/asset/变化清单innovation-source.json。不叠v1growth/descriptor/bucket/gather，尚未服务执行。基点结束/清卡后同launch_context_long_screen.sh串行运行，必须实际FIRST_CHECKED/DEFERRED，不靠INSTALLED；positive后才新accuracy。
- hardware并行回看已测prefill配置/actual54c源码，最多提2个未测且有硬件依据的候选；不把decode2warp自动外推到2D，不重做旧grid，也不抢GPU。框架仍优先，有反证就记录停止。所有agent成果持续写各自handoff。

## 2026-10-21 11:53Z V2新策略实际上卡

- 114713 DB506原080656匹配基点exit0：220.24970296164975s/2529.202048898997total、32成功0失败/524288input32768out、meanTTFT62440.3197ms/medianITL92.196925ms、KV521840、preemptions0→1。DB before=after506表18926行、三hash相同，原件封存/本地下载进行中；11:52:46.493627Z完整postflight68MiB/0%/9031closed。
- **当前唯一GPU：framework/20261021T115247Z-growth-v2-innovation-context16k-long，runner162380**，source code/growth-v2-20261021T114249Z（runtime72d6/init830f，仅新准入，不含旧v1/diag/bucket/gather/overlap）。同bc51driver/原官方SERVER/no profiler/16K1024out32req/c64/seed721201，DB506匹配。
- 先看EngineCore是否真实FIRST_CHECKED+DEFERRED，再读32success/tokens/抢占差值/吞吐/TTFT/DB/KV，不能用旧103/105给新策略背书。若策略收益不足或倒退，保留准确负结果，停止扩大；最终原13eb完整两档对照仍待，正式分数未声称。

- 11:56Z真实新V2进展：EngineCore162561 FIRST_CHECKED free31595/future1151；FIRST_DEFERRED free2702/future2722。19:56:11日志29running/3waiting、KV92.9%、321.8output tok/s。预算策略确实起作用，尚未完整结果或accuracy；不要仅从降低抢占预期就报吞吐收益。

## 2026-10-21 12:00Z 新V2真实生效但冷轮较慢，仅补warm

- 115247 V2 exit0、真实EngineCore162561 CHECKED+DEFERRED，29running/3waiting，实际抢占0→0。32成功0失败/524288input32768out、238.11336583085358s/2339.4570819502455total，meanTTFT68405.784913ms，KV521936。相对114713新基点220.249703s/TTFT62440.319729ms是慢信号，不能因少1次抢占就当吞吐改善；但DB506/18926→512/19130(+6表204行)，因此还不能当热态回退结论。
- 11:59:21.132870Z完整postflight68MiB/0%/9031closed，完整raw/control/source/DB-before-after已远端封存并下载进行中。
- **当前唯一GPU：framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long，runner163945**，原V2 source114249、samebc51/原官方SERVER/no profiler/16K1024out32req/c64/seed721201，DB512。仅一次必要warm短复核，不先重跑大accuracy；positive才进一步matched控制/accuracy/正式，negative如实保留并停止扩大。
- 下一个唯一新方向：actual2D full-visible prefix省causal mask，已有42行/17旧配置CPU复盘，避免重复tile扫描；hardware实现严格sourceguard/固定BM128-T64-w8-s1和原dot/softmax顺序，framework交叉审。尚未代码定稿或设备执行，3D/C2/无支持features必须原路；最短P2019/16K+Q2048/16K bitwise/KV/RNG后合理32/64calls计时，先判断有无真实大信号。w16仅研究，未实施。

## 2026-10-21 12:27Z 重大经验落盘，完整原版官方基线已启动

- 115950 V2 warm exit0，真实EngineCore164138 CHECKED+DEFERRED，32/0同tokens、抢占0→0、KV521840。221.23383624106646s/2517.95118443368total、meanTTFT67130.273776ms。DB512表19130行前后schema/logical/physical完全不变；对114713基点220.249703s/TTFT62440.319729ms未显示吞吐收益、TTFT约+7.51%，保留研究实现和负结果，不扩大accuracy。库已从506增512是跨run边界，微小耗时差不称严格稳定回退；停止继续调参此策略。12:18:37.889080Z完整清卡68/0/closed，原件下载已重试成功，正在取回；一次文件传输auto-review超时并非安全否定，无待用户批准事项。
- 121838 prefix-visible gate exit0，两实际shape C3-P2019/KV16K及Q2048/KV16K完整out bits/KV/RNG/padding/2Dselected/3D原C2fallback全pass，随机物理页+16共享旧prefix+slot-1/NaNtail。最终policy87c6a31075939c551402d7007b491546a215584a58ec82caddc08fc7249998d6、gate d3dbf65a9a711360c92ca7c6a01a4ec23046926ee753cd37f836ad33a3bf1996、派生kernel a6d3604aaf3896dce150b8ef56253a3d0fa12dd89095740bb1ec99ce975ddaa2。
- 仅P2019、预先record过的events32callsABBA：wall12.5943597→12.5596171ms（0.2759%），event12.4910102→12.4343061ms（0.4540%）。只是小单层信号，代码/门/测量保留，不声称E2E或模型accuracy，不优先扩大验证。proxy已finally还原；12:25:01.258460Z fullpost68/0/closed并远端封存。
- **关键依赖隔离经验：** retained a0c runtime在iluvatar module-level导入时会持久写site-packages/attention.py，再删pycache；top-p仅进程内替换。只git archive原13eb插件不足以获得真正原始基线。root+systems独立纯AST撤两段+EOF marker，从54c41796bytes得到bab2c0b9f9a7793ca411796b48ebb4734433160e7e99eabf46ddb7f1c30cb6e0/41176bytes，与最早a4 .orig逐byte相同（len(str)41166是字符数）。现有d60/SQL/C2/C3对照均基于retained，仍有效；尚未运行的原13eb基线及时加此前置，没有伪造旧数据。
- 已审restore helper8b3337e06e4dc083b5f99cafd785c6d5a49b64c86a10d721d47c76c304c8eda6，12:26:07Z实际apply成功。共同锁内9031关闭/单卡68MiB0%无进程双检、3份原输入备份核字节、原子替换保mode/uid/gid、posthash bab2；不动SQLite/Tritoncache/pycache。远端完整record=/workspace/experiments/minicpm-s2/dependency-restores/20261021T122607Z-original-baseline，含manifest/前后源/reference/runtime/helper。baseline期间禁止import任何retained/C3平台路径，会写回54c；只允许stdlib只读监测。恢复后候选下次启动可自行按提交代码再写54c，不能在baseline活跃时做。
- **当前唯一GPU：official/20261021T122607Z-original-baseline，runner166637**，control同名-control，source code/official-base-20261021T091033Z（pristine13eb，runner446f12），launcher a4fac213/driver79119f，第三marker显式空串；原官方benchmark0813/原SERVER/两档各4轮丢首/no profiler/no smoke。启动前installed bab2再次核实。后续必须启动后再核manifest archived attention= bab2、无retained markers/源模块、原8raw/2summary/成功tokens/第2–4均值及清理，不能仅凭exit0。原始匹配总体提升尚待。

- 12:39:57.289035Z原版startup独立核验：225个归档源SHA逐项全部匹配，当前installed与manifest archived Attention均bab2，归档无retained runtime、服务无BIV150 marker。真实server166651/EngineCore166820/benchmark167244，已有POST与64running/真实GPU负载，4K1/4运行中。核验JSON已本地保存experiments/official/20261021T122607Z-original-baseline-control/startup-source-review.json；这是启动完整性证据，不是完成成绩。restore与prefix原件已全部本地，systems独立核验通过；无待用户批准事项。
