# 当前实验状态

2026-10-26。BI-V150由本方管理，C500由队友独立管理。

- 合格主线仍main6971／treeaa43，4K/16K暖均5656.77/4119.24 tok/s，原105题103/105；不重跑没变的基线。
- QKV宽tile模型4K暖均−2.57%，16K首暖−0.36%，六轮1280 SUCCESS后停止；down小M SplitK8官方4K首暖−0.34%，两轮512 SUCCESS后停止。都不跑105、不合并、不定新基线。
- O宽tile组件省20.33%，原官方4K冷/首暖/第三轮4894.19/5538.59/5568.49 tok/s，768 SUCCESS；第三轮对对应5677.28观察−1.9162%，已停止。16K/105未跑，不定新基线；原SIGTERM/exit1及清理回执保留。
- GQA T32慢43.01%、SME span慢0.3806%，停止。down K256 INT8精确整数门失败，未计时，不推进依赖融合。fresh-KV长组件逐位/FP64通过但慢30.1099%；QKV＋RoPE融合14项通过但Graph慢12.4198%/12.8168%，均停止，不进官方。
- LPT长上下文慢3.57%，不改该范围。Q2048/KV2048完整Graph省12.2180%，Q2048/KV4096省5.7144%，初始/换值跨臂逐位。纯causal旧long-only FP64门仍两臂false，原样保留诊断；middle原FP64硬门通过。直接JIT Event正而wall负另记，不混入完整Graph结果。
- **07:16 UTC启动快照，未有官方结论**：`20261026T071618Z-main6971-lpt-early-four-rounds`，候选tree `df8cde68`，supervisor351873/owner351874/driver351877。双Manager安装成功，尚未取得实际选择资格；由root继续核实际回执及原官方结果，不把安装当启用或基线。运行目录 `/workspace/experiments/minicpm-s2/official/20261026T071618Z-main6971-lpt-early-four-rounds`，owner状态在同名`-control/state.json`。不并行启动第二GPU实验。
- 最新用户要求低于可比基线就停止；只读原CSV的外层执行此规则，官方脚本/服务参数不变。原件按run保留，模型负、测试构造失败、参考范围不适用分别登记。
- 用户重新授权子智能体并行硬件调研；它们仅CPU准备，唯一GPU由root统一排队，研究不是已确认收益。

[唯一实验总表](team/experiments.md) · [GEMM](team/methods/shape-gemm.md) · [Prefill调序](team/methods/prefill-lpt.md) · [SME span](team/methods/gqa-sme-span.md) · [INT8精确门](team/methods/down-group256.md) · [fresh-KV](team/methods/prefill-fresh-kv.md) · [QKV融合](team/methods/qkv-rope-fusion.md)。本批8轮原始文本/CSV/源码已核605文件SHA并登记，总315条；大张量、DB/native仍按原manifest留远端。历史交接保留在[归档](archive/ai/20261026-current-before-four.md)。
