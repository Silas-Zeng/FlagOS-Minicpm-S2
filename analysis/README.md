# 分析索引

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

本目录保存简洁、便于审计的分析摘要，依据的原始材料位于 `/workspace/experiments/minicpm-s2/`。

2026-10-22 最新入口：

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
