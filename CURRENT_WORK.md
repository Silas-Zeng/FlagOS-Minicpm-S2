# 当前实验状态

2026-10-26。BI-V150由本方管理，C500由队友独立管理。

- 合格主线仍main6971／treeaa43，4K/16K暖均5656.77/4119.24 tok/s，原105题103/105；不重跑没变的基线。
- QKV宽tile模型4K暖均−2.57%，16K首暖−0.36%，六轮1280 SUCCESS后停止；down小M SplitK8官方4K首暖−0.34%，两轮512 SUCCESS后停止。都不跑105、不合并、不定新基线。
- O宽tile组件省20.33%，原官方4K冷/首暖/第三轮4894.19/5538.59/5568.49 tok/s，768 SUCCESS；第三轮对对应5677.28观察−1.9162%，已停止。16K/105未跑，不定新基线；原SIGTERM/exit1及清理回执保留。
- GQA T32慢43.01%、SME span慢0.3806%，停止。down K256 INT8精确整数门失败，未计时，不推进依赖融合。fresh-KV长组件逐位/FP64通过但慢30.1099%；QKV＋RoPE融合14项通过但Graph慢12.4198%/12.8168%，均停止，不进官方。
- LPT长上下文慢3.57%，不改该范围。Q2048/KV2048完整Graph省12.2180%，Q2048/KV4096省5.7144%，初始/换值跨臂逐位。纯causal旧long-only FP64门仍两臂false，原样保留诊断；middle原FP64硬门通过。直接JIT Event正而wall负另记，不混入完整Graph结果。
- **LPT官方已结束，保留混合结果候选**：071618／tree `df8cde68`，4K四轮4863.05/5694.95/5694.17/5778.33，暖均5722.4833 tok/s，对5656.77观察+1.1617%；16K冷3757.10、首暖4111.36，对应4119.46观察−0.19663%后停。六轮1280 SUCCESS；私有LPT Q-hoist实际selected已由posthoc原件核实。KV548432对548336，非严格因果；无105/合并/新基线，不称稳定整体收益或整体负。07:57 source/native/DB及清理通过，条件后继已skip。
- gate partial融合真实opaque/F.linear身份/config及M2030八项数值/Graph等门通过，但完整Graph1.305489→1.499709ms慢14.8772%，停止M2048、8层工作集和模型。两臂都是两个launch，partial_up shared128KiB/reg169；原QKV组件使用mm、不是生产linear的直接对照，限制单列保留。
- 阶段测试均已结束，未安排新GPU任务；最后gate owner于07:57:50 UTC完成source/DB恢复与设备/9031清理。主线继续用main6971，新增方法仅保留对应已测资格，不继承其103/105。
- 本批早停由外层只读原CSV后执行，官方脚本/服务参数不变；停止决定及已测轮次均保留，不当作完整官方成绩。后续验证遵循当前AGENTS.md，历史队列不自动重启。
- 用户重新授权子智能体并行硬件调研；它们仅CPU准备，唯一GPU由root统一排队，研究不是已确认收益。

[唯一实验总表](team/experiments.md) · [GEMM](team/methods/shape-gemm.md) · [Prefill调序](team/methods/prefill-lpt.md) · [SME span](team/methods/gqa-sme-span.md) · [INT8精确门](team/methods/down-group256.md) · [fresh-KV](team/methods/prefill-fresh-kv.md) · [QKV融合](team/methods/qkv-rope-fusion.md) · [gate融合](team/methods/gate-partial-fusion.md)。本阶段两批10轮原始文本/CSV/源码分别核605/342文件SHA并登记，总317条、314个唯一run；大张量、DB/native仍按原manifest留远端。历史交接保留在[归档](archive/ai/20261026-current-before-four.md)。
