<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 无损KV位编码与页内布局

真实42层位样本支持继续组件；逻辑少读约24.2%不等于HBM或吞吐收益。

相关代码：[archive-receipt.json](../../experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/archive-receipt.json)；[kv-bit-stats.json](../../experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/kv-bit-stats.json)；[result.json](../../experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/result.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T011819661362Z-main241-real-kv-bits](../runs/bi-v150/20261027T011819661362Z-main241-real-kv-bits.md)（登记#349）：main241/native14f独立诊断，原数学题256prompt tokens，42层各128token的真实post-RoPE K/V共5.25MiB；writer与cache全部逐位相等。CPU无损12bit+escape估算K/V逻辑少读24.20258%/24.21341%，全部行可压 **是否保留：** 保留样本；准备完整writer＋decode组件，不进入生产。
