<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# BI-V150连续流读取参考

固定512MiB BF16连续流读＋128KiB checksum输出，三组Event中位约0.806800ms、逻辑读665.432GB/s；两次内容checksum、一次copy正确性及计时后checksum通过。仅连续流读参考，不是物理HBM或散页GQA硬上限，不是吞吐优化/官方成绩。DB/source/native与设备清理通过。同期补回main6971三个实际linear缓存文本，仍不伪装大M实际参数采集。

相关代码：[results.json](../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/results.json)；[worker.py](../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/source/worker.py)；[archive-receipt.json](../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/archive-receipt.json)；[triton-cache](../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/triton-cache)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T101034477784Z-biv150-stream-read-reference-hotspot-component](../runs/bi-v150/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component.md)（登记#325）：连续流读参考665.432GB/s，checksum/copy检查通过；不是HBM硬上限或模型吞吐收益。 **是否保留：** 保留带宽参考及实际linear文本，用于预算；不替换比赛基线，不从连续读参考推GQA可实现收益。
