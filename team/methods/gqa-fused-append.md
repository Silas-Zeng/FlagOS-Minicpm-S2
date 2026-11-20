<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA尾段append融合

只对私有尾slot省独立writer启动，不改BF16/页序/归约。实际编译VGPR增51超过预设预算后停止；数值和计时尚未运行，不称错误或实测慢，不扩展或放宽阈值。

相关代码：[comparison.json](../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/comparison.json)；[archive-receipt.json](../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/archive-receipt.json)；[candidate.py](../../experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/source/candidate.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T090439643177Z-gqa-fused-append-hotspot-component](../runs/bi-v150/20261027T090439643177Z-gqa-fused-append-hotspot-component.md)（登记#366）：尾段append融合编译成功；VGPR93→144超预设+16预算，SGPR spill0→50，shared8KiB不变。数值/计时均未运行，清理通过。 **是否保留：** 停止冻结实现，不放宽预算或扫参；非数值错误/实测慢。
