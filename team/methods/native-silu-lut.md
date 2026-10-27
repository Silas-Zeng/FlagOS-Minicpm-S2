<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# BF16 SiLU精确查表

完整gate慢10.37%，正确性通过，停止。

相关代码：[result.json](../../experiments/framework/20261027T014725735145Z-native-silu-lut-component/result.json)；[archive-receipt.json](../../experiments/framework/20261027T014725735145Z-native-silu-lut-component/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T014725735145Z-native-silu-lut-component](../runs/bi-v150/20261027T014725735145Z-native-silu-lut-component.md)（登记#351）：真实layer20权重/M2048完整native gate：A实际14f SO、B同量化/GEMM及BF16舍入，仅以256KiB同设备精确表替SiLU expf和除法。65280有限BF16位型×12up逐位、12项真实gate/Graph/side及独立INT64、输入/表/RNG门全过。完整 **是否保留：** 停止，不进入生产或官方测试。
