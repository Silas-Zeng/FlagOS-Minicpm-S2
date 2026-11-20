<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill log2域换底

在当前normalized＋Q-hoist中将score/max保持log2域，P与alpha直接exp2；不改tile/页序/地址。M2047/KV16K组件FP64抽样、writer、换值Graph与inputs/RNG通过；换底改变FP32舍入，不能称跨臂逐位。Event省0.2888%，wall慢0.9317%，第二次候选提交CPU4.58ms对其余约1.4ms，原轮保留。ASM换底乘法20→0，n_regs114→116/shared32K不变。仅保留微小GPU正信号，模型收益未确认；qmod仅runtime0，不授官方或105资格，后续GQA固定w4结果另列。

相关代码：[kernel.diff](../../experiments/framework/20261025T152608409713Z-prefill-log2-component/source/kernel.diff)；[worker.py](../../experiments/framework/20261025T152608409713Z-prefill-log2-component/source/worker.py)；[results.json](../../experiments/framework/20261025T152608409713Z-prefill-log2-component/results.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T152608409713Z-prefill-log2-component](../runs/bi-v150/20261025T152608409713Z-prefill-log2-component.md)（登记#277）：FP64/writer/换值Graph/inputs/RNG通过；Event8.358478→8.334337ms省0.2888%，wall8.453647→8.532408ms慢0.9317%。 **是否保留：** 保留微小GPU正信号；模型收益未确认，不授官方/105资格，后续GQA固定w4结果另列。
