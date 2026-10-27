# FlagOS 第二季 MiniCPM5-2B 双平台实验

当前有效BI-V150基线为[框架PR92](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/92)／main b3b87d2：原官方4K／16K各四轮弃首均6481.2267／4826.4467 tok/s，原105题102/105。KV容量差异与105请求分支覆盖限制保留；C500结果独立。

最新批次新增七轮、725份原件：macro0/1严格同轮组件省1.0521%，direct-P近持平停止，真实mixed S4覆盖组件保留正信号。新mixed-S4原官方4K两轮首暖6168.07低于A6301.93（观察−2.1241%）后按预设主动停；512成功，KV548432对548336不同，非严格因果。候选不合并，16K／105停止，保留原基线。入口：[mixed S4方法](team/methods/native-gqa-mixed-s4.md)／[Q32方法](team/methods/native-q32-transfer.md)／[当前接续](CURRENT_WORK.md)。

原件完整保存：mixed61原gzip193MB的完整tar流无损xz14.7MB，全部105原件及tar流SHA实际通过；不裁剪张量／日志。其余五轮保原gzip分块，恢复入口见各轮raw-evidence.json。

团队主要看：**尝试了什么、改了什么、怎么测、结果怎样、是否保留。**

- **[实验总表](team/experiments.md)**：唯一登记视图，包含成功、失败与待确认项。
- **[按方法查阅](team/README.md)**：同一方法的实验集中展示，每轮短记链接代码、命令和原始结果。
- 硬件入口：[天数 BI-V150](team/platforms/bi-v150.md) · [沐曦－曦云 C500](team/platforms/c500.md)。

## 三个仓库各管什么

| 仓库 | 团队查看内容 |
|---|---|
| [vllm-plugin-FL](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL) | 比赛原始框架＋按方法拆分的 PR；框架和插件内算子实现共用代码库，测试结果按具体受测版本说明 |
| [FlagGems](https://github.com/Silas-Zeng/FlagGems) | 比赛指定算子代码＋实际发生的算子改动PR；目前没有新增库内算子实现 |
| 本实验库 | 实验总表、方法记录、每轮短记和原始证据；按硬件区分 |

框架PR的顺序和依赖见[协作安排](docs/pr-collaboration-plan.md)。PR正文链接方法记录，所有维护说明使用自然中文，英文专有名词和代码标识保留。

## 历史结果与方法导航（按各轮版本解释）

| 方法 / 版本 | 结果与处理 |
|---|---|
| **团队新main56／PR66** | 双序列prefill已合并；队友native5cbb单pair观察4K/16K +0.3739%/+0.8399%，105题101/105。本站main241/native14f成绩不迁移；新源码已同步，未开展本站新main测试。[原PR与证据](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/66) |
| **本站已受测main241／native14f** | 原官方4K/16K各四轮弃首均 **5850.05／4487.49 tok/s**；同身份原官方105题 **104/105（99.0476%），valid/pass**，无请求错误/截断/空答案。Q32/C3未被105覆盖，原owner覆盖检查失败单独保留；两档吞吐原件另有Q32实际选中。跨版本KV不同，不把观察差异算严格单项收益。[基线与原件](team/methods/baseline-environment.md)／[当前工作](CURRENT_WORK.md) |
| **历史main594／PR59** | PR59已合并。队友同环境两臂105均102/105且逐题相同，4K单次5588.22→5623.29（+0.62749%）、16K4108.86→4188.04（+1.92698%）；其native/暖机/评分口径与本方旧成绩分开。本站一次探针已核新M64实际MM-out配置，不重复其官方/准确率验证。[PR59原证据](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/59)／[当前工作](CURRENT_WORK.md) |
| **本方历史参考：main6971／PR60** | 已完成原官方4K/16K各四轮，弃首轮 **5656.77／4119.24 tok/s**；同源105题 **103/105**。本页旧QKV/down/O、N-only及GQA结果均按其当时版本解释，不把组件比例迁移到团队新main。 |
| [BF16 down N方向分组布局](team/methods/bf16-nonly-down.md) | N128单层M64省10.55%、M32省3.63%；精确身份修复后的M64-only官方4K暖均5719.8133（观察+1.1145%），16K首暖4005.55（观察−2.7652%）后停。六轮1280 SUCCESS、旧prefill栈/新FX42闭合；KV516320、1008MiB常驻副本，保留混合结果，不合并/定基线/跑105。旧v1身份失配与大M两种负布局分别保留。 |
| [GQA下一页号预取](team/methods/gqa-page-lookahead.md) | 原8门及跨臂逐位通过，完整producer＋reducer Event慢0.105735%、wall快0.06134%，无可分辨正信号，停止；实际next-page load后立即wait，未实现预期重叠 |
| [连续流读取参考](team/methods/stream-read-reference.md) | 512MiB BF16连续读＋checksum参考 **665.432GB/s**；正确性及清理通过，非HBM或GQA硬上限，不是吞吐优化成绩；本批另补回三个实际linear缓存文本 |
| [GQA动态for＋二维span](team/methods/gqa-for-span.md) | 真实N64/S2长度多重集组件通过8类正确性检查，但完整producer＋reducer **0.541187→0.947350ms（慢75.05%）**，停止，不进模型或替换基线 |
| [GQA标量KV页基址与动态for组合](team/methods/gqa-scalar-page-base.md) | scalar＋while慢0.38635%且SME未生效；for＋scalar＋一维i64 stages1实际SME8却慢10.73864%；stages2实际async-copy4/SME16仍慢27.63241%。三项原8门/逐位通过，均停止不接模型，机制生成不等于净收益。 |
| [当前Graph热点](team/methods/main6971-graph-profile.md) | 4K诊断完成，四个Graph采样有效；采样区间以GQA decode为首、linear为次。插桩时间不作正常耗时占比；fresh native FX证明缺项保留，未改变官方基线 |
| [BF16 down权重布局](team/methods/bf16-packed-down.md)／[Prefill历史尾部分离](team/methods/prefill-history-tail.md) | packed通过8项正确性检查，但完整组件慢 **71.89%**，停止；history-tail已消除循环Q读取和SGPR溢出，但跨臂逐位门失败，未计时，停止该候选。均未合并或替换基线 |
| [Prefill CTA调序](team/methods/prefill-lpt.md) | 两个早期chunk完整Graph省 **12.2180%／5.7144%**；纯causal原FP64两臂false仅留诊断，middle硬门通过，long慢3.57%保留原核。原官方4K暖均 **5722.48 tok/s（观察+1.1617%）**，16K首暖 **4111.36（−0.19663%）**后停；六轮1280成功，实际私有Q-hoist选中。KV不同，保留混合结果候选；16K未满/无105，不合并或定新基线 |
| [GQA SME span](team/methods/gqa-sme-span.md)／[fresh-KV](team/methods/prefill-fresh-kv.md) | 数值/Graph等门通过，但组件分别慢 **0.3806%／30.1099%**，停止；SME mask变化不当实际传输启用证明，fresh-KV仅测long |
| [down K256 INT8](team/methods/down-group256.md)／[QKV＋RoPE融合](team/methods/qkv-rope-fusion.md) | INT8首个精确整数门失败、未计时，停止当前错误实现；QKV融合14项通过但M2030/2048 Graph慢 **12.4198%／12.8168%**，停止。其组件使用mm，未绑定生产opaque/F.linear；单层合成激活，不外推官方或准确率 |
| [gate partial融合](team/methods/gate-partial-fusion.md) | 实际生产opaque/F.linear身份/config及M2030八项逐位/FP64/Graph等门通过，完整Graph **1.305489→1.499709ms（慢14.8772%）**。停止M2048、工作集和模型；无生产接线或新基线 |
| [主线复核与native备用方案](team/methods/main-correctness.md) | PR48备用f2ca：103/105与原mixed通过；完整官方4K/16K弃首轮 **5271.89/3763.84 tok/s**，TTFT **4281.63/137244.33ms**，1536请求成功。保留备用，PR仍Draft；旧99/105采样结果和temperature0专项异常分别保留，根因未定。团队main0915本轮原105为100/105（102 stop＋3 cap，0传输错误/空答案）；与旧99/105及mixed专项异常并列保留，不宣称根因已修 |
| [GQA KV读取缓存策略](team/methods/gqa-kv-cg.md) | 三个组件形状Event省 **2.6666%/1.3662%/1.2912%**。旧官方首暖4944.66混有Q-hoist/compute-order未启用，原成绩保留。修正关联身份并确认两者实际选中后，4K冷/首暖 **5073.26/5362.19 tok/s**，两轮512成功；对历史/当期首暖观察 **−6.7750%/−6.9386%** 后主动停止，第三轮中断、16K/105不跑。KV547648对547536，非严格因果；本轮无模型净收益，不合并或定基线 |
| [GQA四页T64计算块](team/methods/gqa-four-page-t64.md) | 三轮数值/Graph/FP64通过，原T64、固定w4、真实N4布局Event分别慢126.90%/64.71%/42.93%；最后实际mma=[1,4]仍无净收益，整个路线收口，不再扫参或进模型 |
| [Prefill log2域](team/methods/prefill-log2.md) | 数值及换值Graph通过；Event省0.2888%，wall慢0.9317%，仅保留微小GPU信号，模型收益未确认 |
| [native SiLU相邻两列访存](team/methods/native-silu-vec2.md) | 15case逐位/Graph通过；隔离尾处理Event慢 **6.9849%**、完整gate慢 **2.4404%**，无净收益。独立私有测试库，不改生产csrc；[实验PR52](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/52)已关闭、未合并，保存实现与教训 |
| [GQA stride常量折叠](team/methods/gqa-kv-stride.md) | 原8组数值/Graph及alternate-stride13项通过，整数mul27→13；Event省 **−0.0410%**、wall省 **+0.0454%**，未见净收益，收口，不进模型 |
| [LM-head双行GEMV](team/methods/lm-head-paired-gemv.md) | 随机M2组件数值/guard/RNG通过，Event **0.835→2.046ms**；明确负，停止，不接模型或创建优化PR |
| [Attention head-major分页读取](team/methods/attention-head-major.md) | 当前/原FlagGems/新loader三臂数值/Graph通过，Event **8.366/29.733/82.944ms**；候选明确负，停止。page16 loader与N64是组合变化 |
| [Attention连续页段寻址](team/methods/attention-affine-pages.md) | 原四语义及串行prefill绑定通过；官方两档各4轮、1536成功，弃首轮4K **5741.68** / 16K **4050.10 tok/s**，相对main526仅观察−0.30%/+0.12%。KV546432对547536，未确认净收益，不定基线/105；组件约5.0–6.9%局部省时保留 |
| [Attention next-K预取](team/methods/attention-next-k.md) | 首次逐位等检查通过，ASM定位门失败、未计时；CPU后核发现真实PV前wait/barrier，预期重叠机制不成立，停止本实现 |
| [GQA恒等rescale跳过](team/methods/gqa-identity-rescale.md) | N33/B40/S16及B32/S4各8组数值/Graph通过，组件耗时分别+2.308%/+1.058%；未见收益，不推进模型/官方。B32首次空padding验证器失败单列保留 |
| **[历史main0bf9性能对照基线](team/methods/pr25-kv-current.md)** | 161030官方4K/16K各4轮、1536/0，第2–4轮 `5758.72/4045.20 tok/s`，TTFT `3626.85/124212.05ms`；526文件/tree8671、SO14f、KV547536、DBfb035。本实例完整105为99/105、未达标，仅保留性能对照身份；532 VERIFY1通过；171101/172742启动图门误拒，174713因已完成轮次负差主动早停（4K−0.98%、16K部分暖轮−1.94%，背景负载未完全匹配，不严格归因KV），不设新基线。183929仅有0.31–0.34s搬运毛预算。队友PR31单轮与102/105条件单列，不跨条件算收益 |
| [535 KV＋H2D 完整官方观察](team/methods/pr25-kv-current.md) | 193100两档各4轮、1536/0，第2–4轮4K **5703.70**、16K **4060.24 total tok/s**，TTFT `3635.20/123213.90ms`，28条FULL链。KV546432对基线547536，`gain_calculated=false`、差值null；完整105尚未通过，不设新基线。前序VERIFY1与两轮筛选原件保留；staging primitive不在此组合内 |
| [538 staging完整四轮](team/methods/pr25-kv-current.md) | 1536成功，官方后三轮均4K5724.16/16K4079.71 tok/s（观察−0.60%/+0.85%）；KV546528对547536，非严格因果，不设新基线/105 |
| [RoPE→KV](team/methods/rope-kv-fusion.md)／[末层FFN选行](team/methods/final-ffn-row-prune.md) | RoPE模型门通过，性能6完整轮1280成功后无净正信号早停：4K暖均5744.28、16K首暖4008.32，KV失配，非完整两档四轮，不定基线/105。FFN与o_proj/S1后继mixed均失败；新对照证明原main526同mixed也失败、精确同请求serial通过，不能归因选行；模型资格未过，暂停性能 |
| [末层Query精确选行](team/methods/selected-query-row.md) | v3四shape双臂、完整KV字节/guard/P及参考差异已保存；输出有限但非bitexact，仅局部数值，模型/105/吞吐未验证。前两次初始化与pinned构造失败均保留；模型门已准备，受共同mixed问题影响暂不启动 |
| **BI-V150前序已完成四轮与准确率的版本：PR15+PR21+Q fragment（#22/#23）** | 官方1536请求、两档各4轮，第2–4轮均值4K `5313.59`、16K `3764.67 total tok/s`，较PR15+PR21旧基线`+3.80%/+9.56%`；Math500 L3 `100/105（95.24%）`通过。Q实际选中、fallback0，shared `65536→32768`、循环内Q read0。DB种子相同但KV `521840`对旧`521936`，不宣称严格等KV单项因果 |
| [PR25＋缓存修复后的KV对照](team/methods/pr25-kv-current.md) | `7596cc0`基点关闭VERIFY回读后的两轮对照，双方768请求全成功、同KV546432与初始DB。候选4K `5402.15/5767.57`（`+0.103%/+0.644%`，无FULL覆盖，不归因KV收益）；16K `3733.69/3972.85`（`+4.728%/−0.493%`）。未见明显退化但收益未稳定；保留当时筛选结果；后继main与535状态见上方，不把旧两轮转为新版本成绩。VERIFY1字节与4题语义门单独保留 |
| [PR24真实路径复验](team/methods/pr24-main.md) | 131603隔离缓存后，实际34层native图、Math500 L3 `100/105`通过。此前六轮因旧AOT图失配撤回模型资格；旧约1.018秒Attention仅为失配运行的活动，不能作为当前预算。组件与KV字节原件保留，不追溯恢复旧成绩 |
| [默认编译缓存身份修复](team/methods/native-cache-identity.md) | PR35保留默认缓存；49项组件通过，重启4/4语义正确（含4908token）、同AOT与34层native图。首启checker格式误拒原件保留；不替代完整准确率 |
| BI-V150历史SQL+C3完整组合 | 官方准确率103/105，完整两档吞吐已留档；这些结果只属于该历史组合，DB/KV对照限制见[原报告](docs/technical-report.md)。对应方法已合并，不能把历史准确率自动赋予新增 CPU 组合 |
| [CPU metadata＋async token](team/methods/cpu-combination.md) | 两轮64/0、同KV与DB，单轮吞吐+0.6986%、平均TTFT−0.1250%，性能信号保留待确认；完整Math500 Level 3准确率102/105（97.1429%），通过 |
| [Q fragment循环外保留](team/methods/q-fragment-hoist.md) | 已合入PR23，其完整官方与准确率结果归属于上表对应版本；旧单轮结果继续保留，不覆盖新结果 |
| [C3重复视图清理](team/methods/c3-views.md) | 短输入单层耗时降低5.97%；真实服务仅表观+0.0177%且KV容量失配，未确认端到端收益，保留局部候选 |
| [输入准备等待](team/methods/input-prep.md) | 4K短负载与16K长输出的部分累计中，等待占预处理均低于0.1%；暂不优先改造此处同步。诊断不计吞吐收益 |
| [KV复制](team/methods/kv-pitched.md) | 字节正确性和局部成本信号已记录，尚无稳定端到端收益；工具已合并，仍需显式调用，未启用 KV offload |
| 沐曦－曦云C500 | 由该平台队友补充环境与实测，不能套用BI-V150结果 |

框架与算子优化同等考虑，按实际热点、硬件和输入特点、净收益及验证成本选择；先核对队友已有实现，避免重复开发。本批GQA `.cg`三个组件形状局部正；旧官方首暖负同时关闭了Q-hoist/compute-order，而当期原main启用两者，属于混杂对照；修正集成并确认两者选中后的官方首暖仍负，已按策略停止，KV不同不作严格因果；stride、LM-head与head-major未见净收益并收口；KV和选行既有结果保留，后续[GPU热点](team/methods/gpu-hotspots.md)诊断须对应实际加载图和当前代码，历史轨迹不能直接代替新版本预算。CPU小收益继续保留。

本阶段已登记受测基点为PR25＋缓存修复的`7596cc0`，KV候选的源码树与改动清单随各轮原件保存；后续main集成不自动继承这些成绩。已完成官方四轮的`4c57567d`及更早版本分别保留，旧负结果不删除。最新运行状态和下一步见[当前工作](CURRENT_WORK.md)。

原始日志与环境文件保留在experiments/，从短记进入即可；不需要先读审计过程。早期未证实、放弃或失败的方法仍在总表中。

[当前工作](CURRENT_WORK.md) · [协作规范](AGENTS.md) · [AI交接、详细清单与历史过程归档](archive/README.md)

每轮复用启动器自动留原件，简写结论与下一步；结果按组批量同步，完整技术报告留到阶段结束。

最新闭合：ABI v2官方16K暖均4826.4467，对A观察+6.5491%（KV少144）；同源码原105题102/105、95%门通过。4K/16K正观察仍明示KV差异，启动capture不证明105请求分支覆盖。CPU Q32探针原checker失败与sidecar静态接受分列，无数值/性能资格；详见方法记录。

原生BF16 GQA同步版本已通过[框架PR92](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/92)合并至main `b3b87d2a`，上述4K/16K与105结果作为接续基线并保留条件限制。宏1及M16映射后继仅保留组件/诊断资格，不转移为官方收益。

后继Q32原生Attention完整组件正确性通过，但Event慢21.56%而停止，不进入模型；入口缺SO路径的首失败单列。当前同步原生GQA热点profile原posthoc不完整，已有节点解析通过；插桩区间只作诊断，完整3109原件以无损xz保留，沿每轮raw-evidence索引恢复。
