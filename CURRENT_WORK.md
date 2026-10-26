# 当前实验状态

14:16 UTC GQA stages2已结束：原8门/逐位通过，真实软件流水生成但完整组件慢27.63241%，停止不扫stages3。owner389628/worker389632已退出，DB/source/native/9031/设备清理通过。59份原件已同步，现336条／333个唯一run；没有官方/105/新基线/代码合并。

13:50 UTC GQA组合收尾：原8门及逐位通过，实际SME LLVM/ASM各8条，但完整组件慢10.73864%，停止不接模型。owner389306/worker389310已退出并清理。59份原件已同步，现335条／332个唯一run；没有新基线/105/代码合并。

12:46 UTC：N-only身份修复v2官方已结束，新增1轮登记，现334条／331个唯一run。4K四轮暖均5719.8133（观察+1.1145%），16K冷/首暖3642.71/4005.55（首暖观察−2.7652%）后主动停；六轮1280 SUCCESS。原prefill栈/新FX42实际闭合，KV516320；保留4K正/16K负混合结果，不合并/跑105/定新基线。289份原件逐SHA复制，source/native/DB与本轮进程清理通过；本轮supervisor/owner/driver已退出，不按旧PID重复占卡。main6971的5656.77/4119.24、103/105仍为原基线。


[局部收益预算与限制](analysis/2026-10-26-local-to-e2e-budget.md) · [已有模型对照复核](analysis/2026-10-26-local-to-e2e-review.md)。M64组件10.55%不能外推整模；旧QKV/down/O/LPT没有本次SHA失配，不据此重跑。原结果、valid字段与失败均保留。

11:42 UTC scalar-page-base收尾：新增1轮，现333条／330个唯一run。8类原门及跨臂逐位通过，完整producer＋reducer Event0.542196542→0.544291317ms（慢0.38635%），停止不接模型。SGPR104/spill75为lane保存非HBM，SME实际传输仍0；for＋scalar组合机制未验证，无新官方/105/基线。59份原件及分析原字节同步，DB/source/native与清理通过。

11:39 UTC N-only官方收尾：新登记1轮，现332条／329个唯一run。M64-only候选4K冷/首暖4758.57/5440.33 tok/s，512 SUCCESS；对首暖5533.03观察−1.675393%后主动早停，SIGTERM/owner exit1不是框架错误。pack42/FX42/M64选中已证，KV516320对548336；compute-order因model_runner固定SHA未更新而scope拒绝回原路，prefill全栈未闭合，不能纯归因N-only。停止本模型候选；16K/105未跑，无新基线；清理及DB/source/native恢复通过。287份原件按原字节保留，不重跑或校正原valid字段。

11:13 UTC P256收尾：新登记1轮，现331条／328个唯一run。新P[N/256,K,256]在M2048保原tile且8门/RNG通过，完整Graph Event0.563351333141→0.704238474369ms，慢约25.01%；停止该布局后续M32/M64及单份全M准备。原B两槽异步环、候选B同步与回退同时观测，未证明精确因果。N128历史分开保留；本批不含仍运行的M64-only官方结果，无新官方、105或基线。41份原件及回执已同步。

10:57 UTC N-only批量更新：新登记3轮，现330条／327个唯一run。42真实down权重GPU helper/opaque/Graph及M32回退门通过，未调用完整Llama安装链；M32单层完整Graph省约3.63%，保留组件信号；M2048明确BN256→128后慢约61.60%，停止该大M候选，负结果不否定独立M32/M64正信号。原W/P双份1008MiB、KV容量及官方净性能仍未定；没有新官方、105或基线。原始文本和分轮回执已同步。

10:28 UTC批量更新：新增连续读参考、GQA页号预取、N-only布局3轮，现327条／324个唯一run。连续读参考665.432GB/s不是HBM/GQA硬上限；page-only原8门与逐位通过但无可分辨正信号，已停；N-only M64单层Event省10.5534%、9类case通过，仅保留组件候选，42层额外1008MiB/24576 KV token风险和模型收益未测。原件142份文本（含旧profile补回的15份linear缓存）已同步；源码/DB及所属设备清理通过。无新官方成绩、105、基线或代码合并。

10:00 UTC补充：GQA动态for＋二维span也已完成，8类检查通过，但Event0.541187→0.947350ms（慢75.0504%），停止；源码/DB/native/9031已清理。当前324条／321个唯一run，无新基线。下一步用已有流量与硬件证据评估实际带宽，不把硬件指令启用等同收益。

2026-10-26。BI-V150由本方管理，C500由队友独立管理。

09:35 UTC阶段更新：新登记6轮，现323条／320个唯一run。main6971 Graph诊断已完成并清理，四采样有效，fresh native FX证明缺项保留；只用于热点排序。BF16 packed v2通过8项正确性但组件慢71.89%，停止；history-tail v2成功复用Q、消除SGPR spill，但跨臂逐位要求未通过，未计时，停止当前候选。原始文本与源码分别核191／94成员SHA；大Graph JSON以gzip保留原字节，大张量/DB/native/ixsys仍留远端。CPU继续根据真实GQA热点探索，不重启已停止候选；无新基线或代码合并。

- 合格主线仍main6971／treeaa43，4K/16K暖均5656.77/4119.24 tok/s，原105题103/105；不重跑没变的基线。
- QKV宽tile模型4K暖均−2.57%，16K首暖−0.36%，六轮1280 SUCCESS后停止；down小M SplitK8官方4K首暖−0.34%，两轮512 SUCCESS后停止。都不跑105、不合并、不定新基线。
- O宽tile组件省20.33%，原官方4K冷/首暖/第三轮4894.19/5538.59/5568.49 tok/s，768 SUCCESS；第三轮对对应5677.28观察−1.9162%，已停止。16K/105未跑，不定新基线；原SIGTERM/exit1及清理回执保留。
- GQA T32慢43.01%、SME span慢0.3806%，停止。down K256 INT8精确整数门失败，未计时，不推进依赖融合。fresh-KV长组件逐位/FP64通过但慢30.1099%；QKV＋RoPE融合14项通过但Graph慢12.4198%/12.8168%，均停止，不进官方。
- LPT长上下文慢3.57%，不改该范围。Q2048/KV2048完整Graph省12.2180%，Q2048/KV4096省5.7144%，初始/换值跨臂逐位。纯causal旧long-only FP64门仍两臂false，原样保留诊断；middle原FP64硬门通过。直接JIT Event正而wall负另记，不混入完整Graph结果。
- **LPT官方已结束，保留混合结果候选**：071618／tree `df8cde68`，4K四轮4863.05/5694.95/5694.17/5778.33，暖均5722.4833 tok/s，对5656.77观察+1.1617%；16K冷3757.10、首暖4111.36，对应4119.46观察−0.19663%后停。六轮1280 SUCCESS；私有LPT Q-hoist实际selected已由posthoc原件核实。KV548432对548336，非严格因果；无105/合并/新基线，不称稳定整体收益或整体负。07:57 source/native/DB及清理通过，条件后继已skip。
- gate partial融合真实opaque/F.linear身份/config及M2030八项数值/Graph等门通过，但完整Graph1.305489→1.499709ms慢14.8772%，停止M2048、8层工作集和模型。两臂都是两个launch，partial_up shared128KiB/reg169；原QKV组件使用mm、不是生产linear的直接对照，限制单列保留。
- 前阶段gate等测试均已结束；本轮诊断与布局组件的终态见页首。主线继续用main6971，新增方法仅保留对应已测资格，不继承其103/105。
- 本批早停由外层只读原CSV后执行，官方脚本/服务参数不变；停止决定及已测轮次均保留，不当作完整官方成绩。后续验证遵循当前AGENTS.md，历史队列不自动重启。
- 用户重新授权子智能体并行硬件调研；它们仅CPU准备，唯一GPU由root统一排队，研究不是已确认收益。

[唯一实验总表](team/experiments.md) · [GEMM](team/methods/shape-gemm.md) · [Prefill调序](team/methods/prefill-lpt.md) · [SME span](team/methods/gqa-sme-span.md) · [INT8精确门](team/methods/down-group256.md) · [fresh-KV](team/methods/prefill-fresh-kv.md) · [QKV融合](team/methods/qkv-rope-fusion.md) · [gate融合](team/methods/gate-partial-fusion.md)。本阶段两批10轮原始文本/CSV/源码分别核605/342文件SHA并登记，总317条、314个唯一run；大张量、DB/native仍按原manifest留远端。历史交接保留在[归档](archive/ai/20261026-current-before-four.md)。
