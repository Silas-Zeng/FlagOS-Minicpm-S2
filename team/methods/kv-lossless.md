<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 无损KV位编码与页内布局

SoA完整组件慢355.51%，正确性通过；停止实现，保留真实位样本。

相关代码：[archive-receipt.json](../../experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/archive-receipt.json)；[kv-bit-stats.json](../../experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/kv-bit-stats.json)；[result.json](../../experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/result.json)；[archive-receipt.json](../../experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component/archive-receipt.json)；[archive-receipt.json](../../experiments/framework/20261027T015640083939Z-gqa-lossless12-soa-hotspot-component/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T011819661362Z-main241-real-kv-bits](../runs/bi-v150/20261027T011819661362Z-main241-real-kv-bits.md)（登记#349）：main241/native14f独立诊断，原数学题256prompt tokens，42层各128token的真实post-RoPE K/V共5.25MiB；writer与cache全部逐位相等。CPU无损12bit+escape估算K/V逻辑少读24.20258%/24.21341%，全部行可压 **是否保留：** 保留样本；准备完整writer＋decode组件，不进入生产。
- [20261027T015104107809Z-gqa-lossless12-soa-hotspot-component](../runs/bi-v150/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component.md)（登记#352）：无损KV页内SoA首包：整数提升32位后直接bitcast BF16被编译器拒绝，未获得GPU数值或计时结论。保留冻结包及失败日志；下一包只显式收为uint16再bitcast，不改框架/数学/容差。DB恢复和清理通过。 **是否保留：** 首包编译失败，保留；单行类型修正另run验证。
- [20261027T015640083939Z-gqa-lossless12-soa-hotspot-component](../runs/bi-v150/20261027T015640083939Z-gqa-lossless12-soa-hotspot-component.md)（登记#353）：无损KV页内SoA v2：真实KV短样本拓展组件，65536 BF16位型编码、8项数值/Graph/FP64等与writer三转换门通过，有限输入跨臂逐位一致。完整writer+producer+reducer Graph ABBA 0.543926090002→2.477649092674ms， **是否保留：** 性能显著负，停止当前实现，不进入模型或官方测试。
