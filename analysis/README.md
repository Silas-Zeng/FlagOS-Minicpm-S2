# 分析索引

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

本目录保存简洁、便于审计的分析摘要，依据的原始材料位于 `/workspace/experiments/minicpm-s2/`。

2026-10-22 最新入口：

- [KV框架本阶段交接](2026-10-22-kv-framework-milestone.md)：真实恢复、私有页排序、VERIFY0双失配和已准备的后继容量候选。
- [页序候选不回读配对](2026-10-22-kv-pair-screen.md)：固定源、DB共同起点和真实命中条件；在途状态读CURRENT。
- [恢复容量必要下界早退](2026-10-22-kv-restore-capacity-fast-reject.md)、[完整覆盖省ZERO](2026-10-22-kv-full-overwrite-no-zero-plan.md)、[KV布局与传输研究](2026-10-22-kv-layout-transfer-research.md)：后继独立候选或设计，不继承已测版本结果。
- [实际KV布局与执行器](2026-10-22-kv-runtime-descriptor.md)：195012最短上卡与独立验收，normal42、UniProc和队列证据。
- [单请求KV保存恢复协议](2026-10-22-kv-transaction-protocol.md)、[worker实现](2026-10-22-kv-worker-implementation.md)、[独立审阅](2026-10-22-kv-transaction-independent-review.md)：真实事务接入、失败回滚与验证边界，最新设备状态读CURRENT。
- [KV硬件预算与一手资料](2026-10-22-kv-save-restore-hardware-evidence.md)：20GiB主机限制、1GiB单slot、真实完成依赖与历史记账小候选。
- [按物理连续段选择保存前缀](2026-10-22-kv-fragment-aware-prefix-plan.md)：真实尾部碎片引出的后继设计，尚未实现或测得收益。
- [恢复私有页映射顺序](2026-10-22-kv-owned-page-order-plan.md)：真实1044段的原因、66段几何边界及唯一候选的所有权约束，是否已上卡以CURRENT为准。
- [硬件与输入驱动的框架探索阶段记录](2026-10-22-framework-milestone.md)：本批决策、正负结果和下一项工作。
- [调度与 KV 创新](2026-10-22-scheduler-kv-innovation.md)：真实缺页证据、否定方向和保存恢复状态机。
- [KV 页复制门](2026-10-22-kv-page-copy-gate.md)：四种布局/页映射的上卡正确性与成本。
- [C3 覆盖与 mapped decode](2026-10-22-c3-coverage-and-metadata.md)、[prefix 服务](2026-10-22-visible-prefix-service.md)、[gate-up 服务对照](2026-10-22-mm-cta-service-comparison.md)、[小框架短测](2026-10-22-small-framework-comparison.md)：各候选证据和适用边界。
- [全项目框架实验记录](2026-10-21-framework-experiments.md) 与 [当前交接](../CURRENT_WORK.md)：历史实验和最新执行状态。

记录规则：

- 每项结论都关联实验编号和原始日志路径。
- 将未启用性能分析器的性能测量与启用分析器的诊断运行分开。
- 单次原始重复结果不能当作官方平均值。
- CPU 与设备计时可能重叠，须分别记录。
- 记录实验标识、源码版本和性能分析器设置。
