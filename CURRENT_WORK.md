# 当前实验状态

2026-10-26。BI-V150由本方管理，C500由队友独立管理。

- 合格主线仍main6971／treeaa43，4K/16K暖均5656.77/4119.24 tok/s，原105题103/105；不重跑没变的基线。
- QKV宽tile模型4K暖均−2.57%，16K首暖−0.36%，六轮1280 SUCCESS后停止；down小M SplitK8官方4K首暖−0.34%，两轮512 SUCCESS后停止。都不跑105、不合并、不定新基线。
- GQA T32八类数值/FP64/Graph通过，但Event慢43.01%，SGPR spill0→84，停止。Prefill LPT长上下文逐位/FP64通过但慢3.57%；短causal原臂与候选逐位一致，旧long-only误差界拒绝两臂，尚未计时，不当框架新错误。
- O宽tile42真实权重组件Event10.210502→8.134766ms，省20.33%，84数值/FP64/Graph/side stream通过。独立模型原官方已启动，结果待完成，尚无105或合并资格。
- 最新用户要求低于可比基线就停止；只读原CSV的外层执行此规则，官方脚本/服务参数不变。原件按run保留，模型负、测试构造失败、参考范围不适用分别登记。
- 用户重新授权子智能体并行硬件调研；它们仅CPU准备，唯一GPU由root统一排队，研究不是已确认收益。

[唯一实验总表](team/experiments.md) · [GEMM方法](team/methods/shape-gemm.md) · [GQA两页](team/methods/gqa-two-page-t32.md) · [Prefill调序](team/methods/prefill-lpt.md)。完整原件由每轮短记链接；历史交接保留在[归档](archive/ai/20261026-current-before-four.md)。
